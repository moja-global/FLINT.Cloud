from crypt import methods
from threading import Thread

from numpy import append
from run_distributed import *
from flask_autoindex import AutoIndex
from flask_swagger_ui import get_swaggerui_blueprint
from flask_swagger import swagger
from datetime import timedelta
from datetime import datetime
from google.cloud import storage, pubsub_v1
from google.api_core.exceptions import AlreadyExists
import logging
import shutil
import json
import time
import subprocess
import os
import flask.scaffold
import rasterio as rst
from flask import jsonify
from config_table import rename_columns
import sqlite3
from preprocess import get_config_templates, get_modules_cbm_config, get_provider_config

flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restful import Resource, Api, reqparse
from flask import Flask, send_from_directory, request, jsonify, redirect, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://127.0.0.1:8080/",
        "http://127.0.0.1:8000",
        "http://localhost:5000",
        "http://localhost:8000",
        r"^https://.+example.com$",
    ],
)
# ppath = "/"
# AutoIndex(app, browse_root=ppath)
api = Api(app)

# logger config
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


### swagger specific ###
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "FLINT-GCBM REST API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "FLINT-GCBM Rest Api"
    f = open("./static/swagger.json", "w+")
    json.dump(swag, f)
    return jsonify(swag)


@app.route("/help/<string:arg>", methods=["GET"])
def help(arg):
    """
    Get Help Section
    ---
    tags:
            - help
    parameters:
    - name: arg
            in: path
            description: Help info about named section. Pass all to get all info
            required: true
            type: string
    responses:
            200:
            description: Help
    """
    s = time.time()
    if arg == "all":
        res = subprocess.run(["/opt/gcbm/moja.cli", "--help"], stdout=subprocess.PIPE)
    else:
        res = subprocess.run(
            ["/opt/gcbm/moja.cli", "--help-section", arg], stdout=subprocess.PIPE
        )
    e = time.time()

    response = {
        "exitCode": res.returncode,
        "execTime": e - s,
        "response": res.stdout.decode("utf-8"),
    }
    return {"data": response}, 200


@app.route("/version", methods=["GET"])
def version():
    """
    Get Version of FLINT
    ---
    tags:
            - version
    responses:
            200:
            description: Version
    """
    s = time.time()
    res = subprocess.run(["/opt/gcbm/moja.cli", "--version"], stdout=subprocess.PIPE)
    e = time.time()

    response = {
        "exitCode": res.returncode,
        "execTime": e - s,
        "response": res.stdout.decode("utf-8"),
    }
    return {"data": response}, 200


@app.route("/gcbm/new", methods=["POST"])
def gcbm_new():
    """
    Create a new GCBM simulation with a title.
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
            - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Create a new simulation for GCBM Implementation of FLINT
    """
    # Default title = simulation
    title = request.form.get("title") or "simulation"
    # Sanitize title
    title = "".join(c for c in title if c.isalnum())
    # input_dir = f"{title}"
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
        message = "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
    else:
        message = "Simulation already exists. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."

    return {"data": message}, 200


@app.route("/gcbm/upload", methods=["POST"])
def gcbm_upload():
    """
    Upload files for GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: File upload for GCBM Implementation FLINT
    """

    # Default title = simulation
    title = request.form.get("title") or "simulation"
    # Sanitize title
    title = "".join(c for c in title if c.isalnum())

    # Create project directory
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
    logging.debug(os.getcwd())

    # input files follow a strict structure
    if not os.path.exists(f"{input_dir}/disturbances"):
        os.makedirs(f"{input_dir}/disturbances")
    if not os.path.exists(f"{input_dir}/classifiers"):
        os.makedirs(f"{input_dir}/classifiers")
    if not os.path.exists(f"{input_dir}/db"):
        os.makedirs(f"{input_dir}/db")
    if not os.path.exists(f"{input_dir}/miscellaneous"):
        os.makedirs(f"{input_dir}/miscellaneous")

    # store files following structure defined in curl.md
    if "disturbances" in request.files:
        for file in request.files.getlist("disturbances"):
            file.save(f"{input_dir}/disturbances/{file.filename}")
    else:
        return {"error": "Missing configuration file"}, 400

    if "classifiers" in request.files:
        for file in request.files.getlist("classifiers"):
            file.save(f"{input_dir}/classifiers/{file.filename}")
    else:
        return {"error": "Missing configuration file"}, 400

    if "db" in request.files:
        for file in request.files.getlist("db"):
            file.save(f"{input_dir}/db/{file.filename}")
    else:
        return {"error": "Missing configuration file"}, 400

    if "miscellaneous" in request.files:
        for file in request.files.getlist("miscellaneous"):
            file.save(f"{input_dir}/miscellaneous/{file.filename}")
    else:
        return {"error": "Missing configuration file"}, 400

    return {
        "data": "All files uploaded succesfully. Proceed to the next step of the API at gcbm/dynamic."
    }


@app.route("/config", methods=["POST"])
def config_table():
    obj = request.get_json()
    print(obj)
    input_dir = f"{os.getcwd()}/input/{obj['simulation_name']}"
    response = dict()
    try:
        return {
            "status": 1,
            "response": rename_columns(obj["tables"], obj["simulation_name"]),
        }
    except Exception:
        return {"status": 0, "error": Exception}


@app.route("/upload/db/tables", methods=["POST"])
def send_table():
    """
    Get GCBM table names from database file
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
            - in: Params
            name: title
                    type: string
            description: GCBM table output
    """
    # Default title = simulation
    title = request.form.get("title") or "simulation"
    input_dir = f"{os.getcwd()}/input/{title}/db/"
    conn = sqlite3.connect(input_dir + "gcbm_input.db")
    sql_query = """SELECT name FROM sqlite_master 
    WHERE type='table';"""

    tables = conn.execute(sql_query).fetchall()
    resp = dict()
    # iterate over all the table name
    for table_name in tables:
        schema = []
        ins = "PRAGMA table_info('" + table_name[0] + "')"
        # key as the table name and values as the column names
        for row in conn.execute(ins).fetchall():
            schema.append(row[1])
        resp[table_name[0]] = schema
    return resp, 200


@app.route("/gcbm/table/rename", methods=["POST"])
def rename_table():
    """
    Rename a table
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
            - in: Params
            name: title
                    type: string
            name: previous
                    type: string
            nsme: new
                    type: string
            description: Status indicating success/failure in performing the rename
    """
    title = request.form.get("title") or "simulation"
    input_dir = f"{os.getcwd()}/input/{title}/db/"
    try:
        connection = sqlite3.connect(input_dir + "gcbm_input.db")
        cursor = connection.cursor()
        previous_name = request.form.get("previous")
        new_name = request.form.get("new")
        cursor.execute(f"ALTER TABLE {previous_name} rename to {new_name}")
        return {"status": 1}
    except Exception as exception:
        return {"status": 0, "error": str(exception)}


@app.route("/gcbm/dynamic", methods=["POST"])
def gcbm_dynamic():
    """
    Get GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                - in: body
            name: title
            required: true
            schema:
                    type: string
            description: GCBM Implementation FLINT
    """
    # Default title = simulation
    title = request.form.get("title") or "simulation"

    # Sanitize title
    title = "".join(c for c in title if c.isalnum())
    input_dir = f"{os.getcwd()}/input/{title}"

    get_config_templates(input_dir)
    get_modules_cbm_config(input_dir)
    get_provider_config(input_dir)

    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")

    thread = Thread(target=launch_run, kwargs={"title": title, "input_dir": input_dir})
    thread.start()
    # subscriber_path = create_topic_and_sub(title)
    return {"status": "Run started"}, 200


@app.route("/gcbm/getConfig", methods=["POST"])
def getConfig():
    """
    Return .json for the input .tiff files
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
            - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Name of the Simulation
            name: file_name
            required: true
            schema:
                    type: string
            description: Name of the File
    """
    # Default title = Simulation
    title = request.form.get("title").strip()
    file_name = request.form.get("file_name").strip()
    input_dir = f"{os.getcwd()}/input/{title}"

    # check if title is empty
    if title == "":
        return {"error": "No Simulation name specified"}, 400

    # check if file_name is empty
    if file_name == "":
        return {"error": "No file name specified"}, 400

    # Check if simulation exists or not
    if not os.path.exists(f"{input_dir}"):
        return {"error": "Simulation with the name " + title + " doesn't exists"}, 400

    input_dir_file = f"{input_dir}/{file_name}.json"
    # Check if file exists or not
    if not os.path.exists(f"{input_dir_file}"):
        return {"error": "File with name " + file_name + " doesn't exists"}, 400

    # Return the json for the corresponding file name
    file_obj = open(f"{input_dir_file}")
    obj = json.load(file_obj)
    return {"data": obj}, 200


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


@app.route("/gcbm/download", methods=["POST"])
def gcbm_download():
    """
    Download GCBM Input and Output
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: GCBM Download FLINT
    """
    # Default title = simulation
    title = request.form.get("title") or "simulation"
    # Sanitize title
    title = "".join(c for c in title if c.isalnum())

    output_dir = f"{os.getcwd()}/output/{title}.zip"
    input_dir = f"{os.getcwd()}/input/{title}"

    # if the title has an input simulation and there is no output simulation then they should check the status.
    if not os.path.exists(f"{output_dir}") and os.path.exists(f"{input_dir}"):
        return {
            "message": "You simulation is currently running, check the status via /gcbm/status"
        }

    # if there is no input simulation and no output simulation then the simulation does not exist.
    elif not os.path.exists(f"{output_dir}") and not os.path.exists(f"{input_dir}"):
        return {
            "message": "You don't have a simulation with this title kindly check the title and try again"
        }

    return send_file(
        f"{os.getcwd()}/output/{title}.zip", attachment_filename="{title}.zip",
    )


@app.route("/gcbm/list", methods=["GET"])
def gcbm_list_simulations():
    """
    Get GCBM Simulations List
    ---
    tags:
            - gcbm
    responses:
            200:
    description: GCBM Simulations List
    """

    list = []
    for file in os.listdir(f"{os.getcwd()}/input"):
        list.append(file)

    return (
        {
            "data": list,
            "message": "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download.",
        },
        200,
    )


@app.route("/gcbm/status", methods=["POST"])
def status():
    """
    Get status of a simulation
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Get status of simulation
    """
    # Default title = simulation
    title = request.form.get("title") or "simulation"
    # Sanitize title
    title = "".join(c for c in title if c.isalnum())

    if os.path.isfile(f"{os.getcwd()}/input/{title}/output.zip"):
        message = "Output is ready to download at gcbm/download"
    else:
        message = "In Progress"

    return {"finished": message}


@app.route("/check", methods=["GET", "POST"])
def check():
    return "Checks OK", 200


@app.route("/", methods=["GET"])
def home():
    return "FLINT.Cloud API"


@app.route("/upload/title", methods=["POST"])
def getTitle():
    """
    Get simulation title for GCBM implementation of FLINT
    ---
    tags:
            - gcbm-upload
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Get simulation title for GCBM
    """
    # Default sim_title = simulation
    sim_title = request.form.get("title") or "simulation"

    # Sanitize title
    sim_title = "".join(c for c in sim_title if c.isalnum())

    # input_dir = f"{title}"
    input_dir = f"{os.getcwd()}/input/{sim_title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
        message = f"New {sim_title} simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
    else:
        message = f"Simulation already exists with name {sim_title}. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."

    return {"data": message}, 200


@app.route("/gcbm/upload/disturbances", methods=["POST"])
def gcbm_disturbances():
    """
    Disturbances file for GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm-upload
    responses:
            200:
    parameters:
                    - in: body
            name: string
            required: true
            schema:
                    type: string
            description: Disturbances File upload for GCBM Implementation FLINT
    """

    # Get the title from the payload
    title = request.form.get("title") or "simulation"

    # Check for project directory else create one
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
    logging.debug(os.getcwd())

    # input files follow a strict structure
    if not os.path.exists(f"{input_dir}/disturbances"):
        os.makedirs(f"{input_dir}/disturbances")

    # store disturbances file in a new folder
    if "disturbances" in request.files:
        for file in request.files.getlist("disturbances"):
            file.save(f"{input_dir}/disturbances/{file.filename}")
    else:
        return {"error": "Missing disturbances file"}, 400

    return {"data": "Disturbances file uploaded succesfully. Proceed to the next step."}


@app.route("/gcbm/upload/classifiers", methods=["POST"])
def gcbm_classifiers():
    """
    Classifiers file for GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm-upload
    responses:
            200:
    parameters:
                    - in: body
            name: string
            required: true
            schema:
                    type: string
            description: Classifiers File upload for GCBM Implementation FLINT
    """

    # Get the title from the payload
    title = request.form.get("title") or "simulation"

    # Check for project directory else create one
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
    logging.debug(os.getcwd())

    # input files follow a strict structure
    if not os.path.exists(f"{input_dir}/classifiers"):
        os.makedirs(f"{input_dir}/classifiers")

    # store disturbances file in a new folder
    if "classifiers" in request.files:
        for file in request.files.getlist("classifiers"):
            file.save(f"{input_dir}/classifiers/{file.filename}")
    else:
        return {"error": "Missing classifiers file"}, 400

    return {"data": "Classifiers file uploaded succesfully. Proceed to the next step."}


@app.route("/gcbm/upload/miscellaneous", methods=["POST"])
def gcbm_miscellaneous():
    """
    Miscellaneous file for GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm-upload
    responses:
            200:
    parameters:
                    - in: body
            name: string
            required: true
            schema:
                    type: string
            description: Miscellaneous File upload for GCBM Implementation FLINT
    """

    # Get the title from the payload
    title = request.form.get("title") or "simulation"

    # Check for project directory else create one
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
    logging.debug(os.getcwd())

    # input files follow a strict structure
    if not os.path.exists(f"{input_dir}/miscellaneous"):
        os.makedirs(f"{input_dir}/miscellaneous")

    # store miscellaneous file in a new folder
    if "miscellaneous" in request.files:
        for file in request.files.getlist("miscellaneous"):
            file.save(f"{input_dir}/miscellaneous/{file.filename}")
    else:
        return {"error": "Missing miscellaneous file"}, 400

    return {
        "data": "Miscellaneous file uploaded succesfully. Proceed to the next step."
    }


@app.route("/gcbm/upload/db", methods=["POST"])
def gcbm_db():
    """
    db file for GCBM Dynamic implementation of FLINT
    ---
    tags:
            - gcbm-upload
    responses:
            200:
    parameters:
                    - in: body
            name: string
            required: true
            schema:
                    type: string
            description: db File upload for GCBM Implementation FLINT
    """

    # Get the title from the payload
    title = request.form.get("title") or "simulation"

    # Check for project directory else create one
    input_dir = f"{os.getcwd()}/input/{title}"
    if not os.path.exists(f"{input_dir}"):
        os.makedirs(f"{input_dir}")
    logging.debug(os.getcwd())

    # input files follow a strict structure
    if not os.path.exists(f"{input_dir}/db"):
        os.makedirs(f"{input_dir}/db")

    # store miscellaneous file in a new folder
    if "db" in request.files:
        for file in request.files.getlist("db"):
            file.save(f"{input_dir}/db/{file.filename}")
    else:
        return {"error": "Missing db file"}, 400

    return {"data": "db file uploaded succesfully. Proceed to the next step."}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
