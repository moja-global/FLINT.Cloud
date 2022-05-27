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
    project_dir = f"{title}"
    if not os.path.exists(f"{os.getcwd()}/input/{project_dir}"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}")
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
    project_dir = f"{title}"
    if not os.path.exists(f"{os.getcwd()}/input/{project_dir}"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}")
    logging.debug(os.getcwd())
    if os.path.exists(f"{os.getcwd()}/input/{project_dir}") and not os.path.exists(f"{os.getcwd()}/input/{project_dir}/disturbances"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}/disturbances")
    if os.path.exists(f"{os.getcwd()}/input/{project_dir}") and not os.path.exists(f"{os.getcwd()}/input/{project_dir}/classifiers"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}/classifiers")
    if os.path.exists(f"{os.getcwd()}/input/{project_dir}") and not os.path.exists(f"{os.getcwd()}/input/{project_dir}/db"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}/db")
    if os.path.exists(f"{os.getcwd()}/input/{project_dir}") and not os.path.exists(f"{os.getcwd()}/input/{project_dir}/miscellaneous"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}/miscellaneous")
    if os.path.exists(f"{os.getcwd()}/input/{project_dir}") and not os.path.exists(f"{os.getcwd()}/input/{project_dir}/templates"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}/templates")

    # Function to flatten paths
    def fix_path(path):
        return os.path.basename(path.replace("\\", "/"))
    

    if "disturbances" in request.files:
      for file in request.files.getlist("disturbances"):
          file.save(f"{os.getcwd()}/input/{project_dir}/disturbances/{file.filename}")
    else:
      return{"error": "Missing configuration file"}, 400

    if "classifiers" in request.files:
        for file in request.files.getlist("classifiers"):
          file.save(f"{os.getcwd()}/input/{project_dir}/classifiers/{file.filename}")
    else:
      return{"error": "Missing configuration file"}, 400

    if "db" in request.files:
        for file in request.files.getlist("db"):
            file.save(f"{os.getcwd()}/input/{project_dir}/db/{file.filename}")
    else:
      return{"error": "Missing configuration file"}, 400

    if "miscellaneous" in request.files:
        for file in request.files.getlist("miscellaneous"):
            file.save(f"{os.getcwd()}/input/{project_dir}/miscellaneous/{file.filename}")
    else:
        return{"error": "Missing configuration file"}, 400
    
    if "templates" in request.files:
        for file in request.files.getlist("templates"):
            file.save(f"{os.getcwd()}/input/{project_dir}/templates/{file.filename}")
    else:
        return{"error": "Missing configuration file"}, 400
        

    get_modules_cbm(project_dir)
    get_provider_config(project_dir)
    # layers(project_dir)

    return {
       "data": "All files uploaded succesfully. Proceed to the next step of the API at gcbm/dynamic."
  }

def get_modules_cbm(project_dir):
   with open(f"{os.getcwd()}/input/{project_dir}/templates/modules_cbm.json", "r+") as pcf:
        disturbances = []
        data = json.load(pcf)
        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/disturbances/"):
            disturbances.append(file.split('.')[0])    
        pcf.seek(0)
        data["Modules"]["CBMDisturbanceListener"]["settings"]["vars"] = disturbances
        json.dump(data, pcf, indent=4)
        pcf.truncate()

def get_provider_config(project_dir):
   with open(f"{os.getcwd()}/input/{project_dir}/templates/provider_config.json", "r+") as gpc:
        lst = []
        data = json.load(gpc)
        
        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/disturbances/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/classifiers/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/miscellaneous/"): 
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = "../layers/tiles" + file
            d["layer_prefix"] = file[:-5]
            lst.append(d)    
        gpc.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        Rasters = []
        Rastersm = []
        nodatam = []
        nodata = []
        cellLatSize = []
        cellLonSize = []

        for root, dirs, files in os.walk(os.path.abspath(f"{os.getcwd()}/input/{project_dir}/disturbances/")):
            for file in files:
                fp = os.path.join(root, file)
                Rasters.append(fp)

        for root, dirs, files in os.walk(os.path.abspath(f"{os.getcwd()}/input/{project_dir}/classifiers/")):
            for file in files:
                fp1 = os.path.join(root, file)
                Rasters.append(fp1)

        for nd in Rasters:
            img = rst.open(nd)
            t = img.transform
            x = t[0]
            y = -t[4]
            cellLatSize.append(x)
            cellLonSize.append(y)
    
        result = all(element == cellLatSize[0] for element in cellLatSize)
        if(result):
            cellLat = x
            cellLon = y
            blockLat = x*400
            blockLon = y*400
            tileLat = x*4000
            tileLon = y*4000
        else:
             print("Corrupt files")
        
        gpc.seek(0)

        data["Providers"]["RasterTiled"]["cellLonSize"] = cellLon
        data["Providers"]["RasterTiled"]["cellLatSize"] = cellLat
        data["Providers"]["RasterTiled"]["blockLonSize"] = blockLon
        data["Providers"]["RasterTiled"]["blockLatSize"] = blockLat
        data["Providers"]["RasterTiled"]["tileLatSize"] = tileLat
        data["Providers"]["RasterTiled"]["LonSize"] = tileLon

        json.dump(data, gpc, indent=4)
        gpc.truncate()

        dictionary = {
        "layer_type": "GridLayer",
        "layer_data": "Byte",
        "nodata": 255,
        "tileLatSize": tileLat,
        "tileLonSize": tileLon,
        "blockLatSize": blockLat,
        "blockLonSize": blockLon,
        "cellLatSize": cellLat,
        "cellLonSize": cellLon,
    }

        for root, dirs, files in os.walk(os.path.abspath(f"{os.getcwd()}/input/{project_dir}/miscellaneous/")):
            for file in files:
                fp2 = os.path.join(root, file)
                Rastersm.append(fp2)

            for i in Rastersm:
                img = rst.open(i)
                d = img.nodata
                nodatam.append(d)


        with open(f"{os.getcwd()}/input/{project_dir}/miscellaneous/intial_age_moja.json", 'w', encoding ='utf8') as json_file1:
            dictionary["layer_type"] = "GridLayer"
            dictionary["layer_data"] = "Int16"
            dictionary["nodata"] = nodatam[1]
            json.dump(dictionary, json_file1, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/miscellaneous/mean_annual_temperature_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["layer_type"] = "GridLayer"
            dictionary["layer_data"] = "Float32"
            dictionary["nodata"] = nodatam[0]
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/classifiers/Classifier1_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {"1": "TA", "2": "BP", "3": "BS", "4": "JP", "5": "WS", "6": "WB", "7": "BF", "8": "GA"} 
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/classifiers/Classifier2_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {"1": "5", "2": "6","3": "7",
        "4": "8"} 
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2011_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2011,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          }  
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2012_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] =  {
        "1": {
            "year": 2012,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          } 
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2013_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] =  {
        "1": {
            "year": 2012,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2014_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2014,
            "disturbance_type": "Mountain pine beetle — Very severe impact",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2014_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2015,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2015_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2016,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2016_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2016,
            "disturbance_type": "Wildfire",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2018_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2018,
            "disturbance_type": "Mountain pine beetle — Low impact",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        with open(f"{os.getcwd()}/input/{project_dir}/disturbances/disturbances_2018_moja.json", 'w', encoding ='utf8') as json_file:
            dictionary["attributes"] = {
        "1": {
            "year": 2018,
            "disturbance_type": "Mountain pine beetle — Low impact",
            "transition": 1
            }
          }
            json.dump(dictionary, json_file, indent = 4)

        study_area = {
            "tile_size": tileLat,
            "block_size": blockLat,
            "tiles": [{
               "x": t[2],
               "y": t[5],
               "index": 12674
            }],
            "pixel_size": cellLat,
            "layers": [

            ]
        }

        with open(f"{os.getcwd()}/input/{project_dir}/miscellaneous/study_area.json", 'w', encoding = 'utf') as json_file:

            list = []

            for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/miscellaneous/"):
                d1 = dict()
                d1["name"] = file[:-10]
                d1["type"] = "VectorLayer"
                list.append(d1)
            study_area["layers"] = list

            for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/classifiers/"):
                d1 = dict()
                d1["name"] = file[:-10]
                d1["type"] = "VectorLayer"
                d1["tags"] = ["classifier"]
                list.append(d1)
            study_area["layers"] = list

            for file in os.listdir(f"{os.getcwd()}/input/{project_dir}/disturbances/"):
                d1 = dict()
                d1["name"] = file[:-10]
                d1["type"] = "DisturbanceLayer"
                d1["tags"] = ["disturbance"]
                list.append(d1)
            study_area["layers"] = list

            

            json.dump(study_area, json_file, indent=4)

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
    project_dir = f"{title}"

    gcbm_config_path = "gcbm_config.cfg"
    provider_config_path = "provider_config.json"

    if not os.path.exists(f"{os.getcwd()}/input/{project_dir}"):
        os.makedirs(f"{os.getcwd()}/input/{project_dir}")

    thread = Thread(
        target=launch_run, kwargs={"title": title, "project_dir": project_dir}
    )
    thread.start()
    # subscriber_path = create_topic_and_sub(title)
    return {"status": "Run started"}, 200


def launch_run(title, project_dir):
    s = time.time()
    logging.debug("Starting run")
    with open(f"{os.getcwd()}/input/{project_dir}/gcbm_logs.csv", "w+") as f:
        res = subprocess.Popen(
            [
                "/opt/gcbm/moja.cli",
                "--config_file",
                "gcbm_config.cfg",
                "--config_provider",
                "provider_config.json",
            ],
            stdout=f,
            cwd=f"{os.getcwd()}/input/{project_dir}",
        )
    logging.debug("Communicating")
    (output, err) = res.communicate()
    logging.debug("Communicated")
    if not os.path.exists(f"{os.getcwd()}/input/{project_dir}/output"):
        logging.error(err)
        return "OK"
    logging.debug("Output exists")
    # returncode = final_run(title, gcbm_config_path, provider_config_path, project_dir)
    shutil.make_archive(
        f"{os.getcwd()}/input/{project_dir}/output",
        "zip",
        f"{os.getcwd()}/input/{project_dir}/output",
    )
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
    project_dir = f"{title}"
    return send_file(
        f"{os.getcwd()}/input/{project_dir}/output.zip",
        attachment_filename="output.zip",
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

    return {
        "data": list,
        "message": "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download.",
    }, 200


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
