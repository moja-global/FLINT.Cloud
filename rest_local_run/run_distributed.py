import os
import shutil
import json
import time
from argparse import ArgumentParser
from textwrap import dedent
from glob import glob
from contextlib import contextmanager
from random import randint
import subprocess
from datetime import datetime

EXAMPLE_STAGING_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "local_files")
)
EXAMPLE_FILESERVER_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "remote_files")
)


def find_config_file(config_path, *search_path):
    for config_file in (
        fn
        for fn in glob(os.path.join(config_path, "*.json"))
        if "internal" not in fn.lower()
    ):
        # Drill down through the config file contents to see if the whole search path
        # is present; if it is, then this is the right file to modify.
        config = json.load(open(config_file, "r"))
        for entry in search_path:
            config = config.get(entry)
            if config is None:
                break

        if config is not None:
            return config_file

    return None


@contextmanager
def update_json_file(path):
    with open(path, "r") as json_file:
        contents = json.load(json_file)

    yield contents

    with open(path, "w") as json_file:
        json_file.write(json.dumps(contents, indent=4, ensure_ascii=False))


def run_block(title, tile_idx, block_idx):
    block_name = f"{tile_idx}_{block_idx}"
    working_dir = os.path.join(EXAMPLE_FILESERVER_ROOT, title)
    block_working_dir = os.path.join(working_dir, "work", block_name)
    shutil.rmtree(block_working_dir, ignore_errors=True)
    os.makedirs(block_working_dir)

    for config_file in glob(os.path.join(working_dir, "config", "*.*")):
        shutil.copy(config_file, block_working_dir)

    vars_config_file = find_config_file(block_working_dir, "Variables")
    with update_json_file(vars_config_file) as variables_config:
        variables_config["Variables"]["job_id"] = block_name

    landscape_config_file = find_config_file(
        block_working_dir, "LocalDomain", "landscape"
    )
    with update_json_file(landscape_config_file) as study_area_config:
        landscape_config = study_area_config["LocalDomain"]["landscape"]
        landscape_config["num_threads"] = 0
        landscape_config["iteration_type"] = "BlockIndex"
        landscape_config["blocks"] = [
            {"tile_index": tile_idx, "block_index": block_idx}
        ]
        if "tiles" in landscape_config:
            del landscape_config["tiles"]

    output_dir = os.path.join(working_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    batch_config_file = (
        glob(os.path.join(block_working_dir, "*.cfg"))
        + glob(os.path.join(block_working_dir, "gcbm_config.json"))
    )[0]

    gcbm_args = [
        "/some/server-side/flint/moja.cli",
        "--config_file" if batch_config_file.endswith("cfg") else "--config",
        batch_config_file,
        "--config_provider",
        "provider_config.json",
    ]
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%H:%M:%S.%f - %b %d %Y")
    f = open(timestampStr + "gcbm_logs.csv", "w+")
    subprocess.run(["pwd"], cwd="/gcbm_files/config")
    res = subprocess.Popen(
        [
            "/opt/gcbm/moja.cli",
            "--config_file" if batch_config_file.endswith("cfg") else "--config",
            batch_config_file,
            "--config_provider",
            "provider_config.json",
        ],
        stdout=f,
        cwd="/gcbm_files/config",
    )
    # e = time.time()
    (output, err) = res.communicate()

    # This makes the wait possible
    res_status = res.wait()
    response = {
        "exitCode": res.returncode,
        "response": "Operation executed successfully",
    }

    print(f"Server: running GCBM (not really): {' '.join(gcbm_args)}")
    return {"data": response}, 200


def get_blocks(staging_dir):
    staging_config_dir = os.path.join(staging_dir, "config")
    localdomain = json.load(
        open(find_config_file(staging_config_dir, "LocalDomain"), "r")
    )
    tiles = [tile["index"] for tile in localdomain["LocalDomain"]["landscape"]["tiles"]]
    blocks_per_tile = 100
    for tile_idx in tiles:
        for block_idx in range(blocks_per_tile):
            yield tile_idx, block_idx


def upload_simulation_files(title, staging_dir, input_files):
    remote_simulation_dir = os.path.join(EXAMPLE_FILESERVER_ROOT, title)
    print(
        f"Client: uploading simulation files to {remote_simulation_dir} - in a real "
        "simulation, this would be done through SCP or some other method."
    )

    print(f"  - uploading staged config files from {staging_dir}")
    shutil.rmtree(remote_simulation_dir, ignore_errors=True)
    shutil.copytree(staging_dir, remote_simulation_dir)

    remote_input_data_dir = os.path.join(remote_simulation_dir, "input")
    print(f"  - uploading data files to {remote_input_data_dir}:")
    os.makedirs(remote_input_data_dir)
    for input_file in input_files:
        print(f"      {input_file}")
        remote_filename = os.path.join(
            remote_input_data_dir, os.path.basename(input_file)
        )
        shutil.copyfile(input_file, remote_filename)


def stage_files(title, gcbm_config, provider_config):
    # Create a temporary staging directory for new config files that will be copied to the
    # distributed run storage location.
    staging_dir = os.path.join(EXAMPLE_STAGING_ROOT, title)
    shutil.rmtree(staging_dir, ignore_errors=True)
    os.makedirs(staging_dir)

    print(f"Client: staging simulation files for {title} in {staging_dir}")

    staging_config_dir = os.path.join(staging_dir, "config")
    os.makedirs(staging_config_dir)

    # Copy the GCBM config file: a .cfg referencing multiple .json files, or a single .json file.
    if gcbm_config.endswith("cfg"):
        working_gcbm_config_file = os.path.join(staging_config_dir, "gcbm_config.cfg")
        with open(working_gcbm_config_file, "w") as working_gcbm_config:
            for line in open(gcbm_config, "r"):
                _, config_file = line.strip().split("=")
                gcbm_config_dir = os.path.dirname(gcbm_config)
                shutil.copy(
                    os.path.join(gcbm_config_dir, config_file), staging_config_dir
                )
                working_gcbm_config.write(f"config={os.path.basename(config_file)}\n")
    else:
        shutil.copy(gcbm_config, os.path.join(staging_config_dir, "gcbm_config.json"))

    # Copy the provider config file, flattening file paths and adding all input data to a list
    # of files to be copied to the distributed run storage location.
    input_files = []
    working_provider_config_file = os.path.join(
        staging_config_dir, "provider_config.json"
    )
    shutil.copy(provider_config, working_provider_config_file)
    input_data_root = "/".join(("..", "..", "input"))
    with update_json_file(working_provider_config_file) as working_provider_config:
        for provider_name, provider_settings in working_provider_config[
            "Providers"
        ].items():
            datasource_path = provider_settings.get("path")
            if datasource_path:
                input_files.append(
                    os.path.abspath(
                        os.path.join(os.path.dirname(provider_config), datasource_path)
                    )
                )
                provider_settings["path"] = "/".join(
                    (input_data_root, os.path.basename(datasource_path))
                )

            layers = provider_settings.get("layers")
            if layers:
                original_provider_path = os.path.dirname(provider_config)
                for layer in layers:
                    layer_path = layer.get("layer_path")
                    abs_layer_path = os.path.abspath(
                        os.path.join(original_provider_path, layer_path)
                    )
                    input_files.append(abs_layer_path)
                    if os.path.isfile(abs_layer_path):
                        layer_metadata_path = f"{os.path.splitext(layer_path)[0]}.json"
                        input_files.append(
                            os.path.abspath(
                                os.path.join(
                                    original_provider_path, layer_metadata_path
                                )
                            )
                        )

                    layer["layer_path"] = "/".join(
                        (input_data_root, os.path.basename(layer_path))
                    )

    return (staging_dir, input_files)


def final_run(title, gcbm_config, provider_config, project_dir):

    staging_dir, input_files = stage_files(title, gcbm_config, provider_config)
    upload_simulation_files(title, staging_dir, input_files)

    # output_dir = os.path.join(working_dir, "output")
    os.makedirs("output", exist_ok=True)

    f = open(f"/input/{project_dir}/gcbm_logs.csv", "w+")
    subprocess.run(["pwd"], cwd="/gcbm_files/config")
    res = subprocess.Popen(
        [
            "/opt/gcbm/moja.cli",
            "--config_file",
            gcbm_config,
            "--config_provider",
            "provider_config.json",
        ],
        stdout=f,
        cwd=f"/input/{project_dir}",
    )
    (output, err) = res.communicate()

    # This makes the wait possible
    res_status = res.wait()
    return res.returncode

    # queue = []
    # for tile_idx, block_idx in get_blocks(staging_dir):
    #    print(f"Client: queueing tile {tile_idx}, block {block_idx} for simulation")
    #    queue.append((tile_idx, block_idx))

    # Pretending we're a cluster for the example - in reality the workers would receive
    # jobs from Celery through a message broker.
    # for tile_idx, block_idx in queue:
    #    print(f"Server: worker {randint(0, 4)} running tile {tile_idx}, block {block_idx} for {title}")
    #    run_block(title, tile_idx, block_idx)
