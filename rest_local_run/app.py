from threading import Thread
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
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restful import Resource, Api, reqparse
from flask import Flask, send_from_directory, request, jsonify, redirect, send_file

app = Flask(__name__)
# ppath = "/"
# AutoIndex(app, browse_root=ppath)
api = Api(app)

# logger config
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "FLINT-GCBM REST API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "FLINT-GCBM Rest Api"
    f = open("./static/swagger.json", "w+")
    json.dump(swag, f)
    return jsonify(swag)


@app.route('/help/<string:arg>', methods=['GET'])
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
    if arg == 'all':
        res = subprocess.run(
            ['/opt/gcbm/moja.cli', '--help'], stdout=subprocess.PIPE)
    else:
        res = subprocess.run(
            ['/opt/gcbm/moja.cli', '--help-section', arg], stdout=subprocess.PIPE)
    e = time.time()

    response = {
        'exitCode': res.returncode,
        'execTime': e - s,
        'response': res.stdout.decode('utf-8')
    }
    return {'data': response}, 200


@app.route('/version', methods=['GET'])
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
    res = subprocess.run(
        ['/opt/gcbm/moja.cli', '--version'], stdout=subprocess.PIPE)
    e = time.time()

    response = {
        'exitCode': res.returncode,
        'execTime': e - s,
        'response': res.stdout.decode('utf-8')
    }
    return {'data': response}, 200


@app.route('/gcbm/new', methods=['POST'])
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
    title = request.form.get('title') or 'simulation'
    # Sanitize title
    title = ''.join(c for c in title if c.isalnum())
    project_dir = f'{title}'
    if not os.path.exists(f'{os.getcwd()}/input/{project_dir}'):
        os.makedirs(f'{os.getcwd()}/input/{project_dir}')
        message = "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
    else:
        message = "Simulation already exists. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."
    
    return {'data': message}, 200
   

@app.route('/gcbm/upload', methods=['POST'])
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
    title = request.form.get('title') or 'simulation'
    # Sanitize title
    title = ''.join(c for c in title if c.isalnum())

    # Create project directory
    project_dir = f'{title}'
    if not os.path.exists(f'{os.getcwd()}/input/{project_dir}'):
        os.makedirs(f'{os.getcwd()}/input/{project_dir}')
    logging.debug(os.getcwd())

    # Function to flatten paths
    def fix_path(path):
        return os.path.basename(path.replace('\\', '/'))

    # Process configuration files
    if 'config_files' in request.files:
        for file in request.files.getlist('config_files'):
            # Fix paths in provider_config
            if file.filename == 'provider_config.json':
                provider_config = json.load(file)
                provider_config['Providers']['SQLite']['path'] = fix_path(
                    provider_config['Providers']['SQLite']['path'])
                layers = []
                for layer in provider_config['Providers']['RasterTiled']['layers']:
                    layer['layer_path'] = fix_path(layer['layer_path'])
                    layers.append(layer)
                provider_config['Providers']['RasterTiled']['layers'] = layers
                with open(f'{os.getcwd()}/input/{project_dir}/provider_config.json', 'w') as pcf:
                    json.dump(provider_config, pcf)
            # Fix paths in modules_output
            elif file.filename == 'modules_output.json':
                modules_output = json.load(file)
                modules_output['Modules']['CBMAggregatorSQLiteWriter']['settings']['databasename'] = 'output/gcbm_output.db'
                modules_output['Modules']['WriteVariableGeotiff']['settings']['output_path'] = 'output'
                with open(f'{os.getcwd()}/input/{project_dir}/modules_output.json', 'w') as mof:
                    json.dump(modules_output, mof)
            else:
                # Save file immediately
                file.save(f'{os.getcwd()}/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing configuration file'}, 400

    # Save input
    if 'input' in request.files:
        for file in request.files.getlist('input'):
            # Save file immediately
            file.save(f'{os.getcwd()}/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing input'}, 400

    # Save db
    if 'db' in request.files:
        for file in request.files.getlist('db'):
            # Save file immediately
            file.save(f'{os.getcwd()}/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing database'}, 400

    return {"data":"All files uploaded sucessfully. Proceed to the next step of the API at gcbm/dynamic."}, 200


@app.route('/gcbm/dynamic', methods=['POST'])
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
    title = request.form.get('title') or 'simulation'
    # Sanitize title
    title = ''.join(c for c in title if c.isalnum())
    project_dir = f'{title}'

    gcbm_config_path = 'gcbm_config.cfg'
    provider_config_path = 'provider_config.json'

    if not os.path.exists(f'{os.getcwd()}/input/{project_dir}'):
      os.makedirs(f'{os.getcwd()}/input/{project_dir}')
    

    thread = Thread(target=launch_run, kwargs={
                    'title': title, 'project_dir': project_dir})
    thread.start()
    #subscriber_path = create_topic_and_sub(title)
    return {"status": "Run started"}, 200



def launch_run(title, project_dir):
    s = time.time()
    logging.debug('Starting run')
    with open(f'{os.getcwd()}/input/{project_dir}/gcbm_logs.csv', 'w+') as f:
        res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', 'gcbm_config.cfg',
                               '--config_provider', 'provider_config.json'], stdout=f, cwd=f'{os.getcwd()}/input/{project_dir}')
    logging.debug('Communicating')
    (output, err) = res.communicate()
    logging.debug('Communicated')
    if not os.path.exists(f'{os.getcwd()}/input/{project_dir}/output'):
        logging.error(err)
        return 'OK'
    logging.debug('Output exists')
    #returncode = final_run(title, gcbm_config_path, provider_config_path, project_dir)
    shutil.make_archive(f'{os.getcwd()}/input/{project_dir}/output', 'zip', f'{os.getcwd()}/input/{project_dir}/output')
    logging.debug('Made archive')
    e = time.time()

    logging.debug('Generated URL')
    response = {
        'exitCode': res.returncode,
        'execTime': e - s,
        'response': "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body."
    }
    

@app.route('/gcbm/download', methods=['POST'])
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
    title = request.form.get('title') or 'simulation'
    # Sanitize title
    title = ''.join(c for c in title if c.isalnum())
    project_dir = f'{title}'
    return send_file(f'{os.getcwd()}/input/{project_dir}/output.zip',attachment_filename='output.zip')
    

@app.route('/gcbm/list', methods=['GET'])
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
    for file in os.listdir(f'{os.getcwd()}/input'):
        list.append(file)

    return {"data": list, "message": "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download."}, 200


@app.route('/gcbm/status', methods=['POST'])
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
    title = request.form.get('title') or 'simulation'
    # Sanitize title
    title = ''.join(c for c in title if c.isalnum())

    if os.path.isfile(f'{os.getcwd()}/input/{title}/output.zip'):
        message = "Output is ready to download at gcbm/download"
    else:
        message = "In Progress"

    return {"finished": message }


@app.route('/check', methods=['GET', 'POST'])
def check():
    return 'Checks OK', 200


@app.route('/', methods=['GET'])
def home():
    return 'FLINT.Cloud API'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
