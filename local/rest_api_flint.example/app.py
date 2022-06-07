from flask import Flask, send_from_directory, request, jsonify
from flask_restful import Resource, Api, reqparse
import os
import subprocess
import time
import json
from datetime import datetime
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from shutil import copyfile

app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://127.0.0.1:8080/",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:5000",
        r"^https://.+example.com$",
    ],
)
api = Api(app)


### swagger specific ###
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "FLINT REST API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


@app.route("/", methods=["GET"])
def home():
    return "FLINT.Example API"


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "FLINT Rest Api"
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
        res = subprocess.run(["moja.cli", "--help"], stdout=subprocess.PIPE)
    else:
        res = subprocess.run(
            ["moja.cli", "--help-section", arg], stdout=subprocess.PIPE
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
    res = subprocess.run(["moja.cli", "--version"], stdout=subprocess.PIPE)
    e = time.time()

    response = {
        "exitCode": res.returncode,
        "execTime": e - s,
        "response": res.stdout.decode("utf-8"),
    }
    return {"data": response}, 200


@app.route("/point", methods=["POST"])
def point():
    """
    Get Point example of FLINT
    ---
    tags:
      - point
    responses:
      200:
            description: Point based example FLINT
    """
    s = time.time()

    if int(request.headers.get("Content-Length")) > 0:
        request_data = request.get_json(force=True)

        if request_data:
            with open("config/received_point_example.json", "w") as outfile:
                json.dump(request_data, outfile, indent=1)

            point_example = "config/received_point_example.json"
    else:
        point_example = "config/point_example.json"
    lib_simple = "config/libs.base.simple.json"
    logging_debug = "config/logging.debug_on.conf"

    if os.path.exists("output") == False:
        os.mkdir("output", mode=0o666)

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%H:%M:%S.%f - %b %d %Y")
    f = open(timestampStr + "point_example.csv", "w+")
    res = subprocess.run(
        [
            "moja.cli",
            "--config",
            point_example,
            "--config",
            lib_simple,
            "--logging_config",
            logging_debug,
        ],
        stdout=f,
    )
    e = time.time()
    UPLOAD_DIRECTORY = "./"
    if os.path.exists("config/received_point_example.json") == True:
        os.rename(
            "config/received_point_example.json",
            "config/received_point_example" + timestampStr + ".json",
        )
    copyfile(
        "./" + timestampStr + "point_example.csv",
        "./output/" + timestampStr + "point_example.csv",
    )
    copyfile(
        "./" + "Moja_Debug.log",
        "./output/" + timestampStr + "point_example.csv_Moja_Debug.log",
    )
    return (
        send_from_directory(
            UPLOAD_DIRECTORY, timestampStr + "point_example.csv", as_attachment=True
        ),
        200,
    )


@app.route("/rothc", methods=["POST"])
def rothc():
    """
    Get RothC example of FLINT
    ---
    tags:
      - rothc
    responses:
      200:
            description: RothC based example FLINT
    """
    s = time.time()
    if int(request.headers.get("Content-Length")) > 0:
        request_data = request.get_json(force=True)

        if request_data:
            with open("config/received_rothc_example.json", "w") as outfile:
                json.dump(request_data, outfile, indent=1)

            point_example = "config/received_rothc_example.json"
    else:
        point_example = "config/point_rothc_example.json"
    lib_simple = "config/libs.base_rothc.simple.json"
    logging_debug = "config/logging.debug_on.conf"

    if os.path.exists("output") == False:
        os.mkdir("output", mode=0o666)

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%H:%M:%S.%f - %b %d %Y")
    f = open(timestampStr + "point_rothc_example.csv", "w+")
    res = subprocess.run(
        [
            "moja.cli",
            "--config",
            point_example,
            "--config",
            lib_simple,
            "--logging_config",
            logging_debug,
        ],
        stdout=f,
    )
    e = time.time()
    UPLOAD_DIRECTORY = "./"

    if os.path.exists("config/received_rothc_example.json") == True:
        os.rename(
            "config/received_rothc_example.json",
            "config/received_rothc_example" + timestampStr + ".json",
        )
    copyfile(
        "./" + timestampStr + "point_rothc_example.csv",
        "./output/" + timestampStr + "point_rothc_example.csv",
    )
    copyfile(
        "./" + "Moja_Debug.log",
        "./output/" + timestampStr + "point_rothc_example.csv_Moja_Debug.log",
    )

    return (
        send_from_directory(
            UPLOAD_DIRECTORY,
            timestampStr + "point_rothc_example.csv",
            as_attachment=True,
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
