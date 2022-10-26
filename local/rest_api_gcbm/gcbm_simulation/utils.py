import logging
import shutil
import json
import time
import subprocess
import os

def launch_run(title, input_dir):
    s = time.time()
    logging.debug("Starting run")
    with open(f"{input_dir}/gcbm_logs.csv", "w+") as f:
        res = subprocess.Popen(
            [
                "/opt/gcbm/moja.cli",
                "--config_file",
                "gcbm_config.cfg",
                "--config_provider",
                "provider_config.json",
            ],
            stdout=f,
            cwd=f"{input_dir}",
        )
    logging.debug("Communicating")
    (output, err) = res.communicate()
    logging.debug("Communicated")

    if not os.path.exists(f"{input_dir}/output"):
        logging.error(err)
        return "OK"
    logging.debug("Output exists")

    # cut and paste output folder to app/output/simulation_name
    shutil.copytree(f"{input_dir}/output", (f"{os.getcwd()}/output/{title}"))
    shutil.make_archive(
        f"{os.getcwd()}/output/{title}", "zip", f"{os.getcwd()}/output/{title}"
    )
    shutil.rmtree((f"{input_dir}/output"))
    logging.debug("Made archive")
    e = time.time()

    logging.debug("Generated URL")
    response = {
        "exitCode": res.returncode,
        "execTime": e - s,
        "response": "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body.",
    }