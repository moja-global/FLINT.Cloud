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
from flask import Flask, send_from_directory, request, jsonify, redirect

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


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'flint-cloud-81ab3d7821f5.json'
publisher = pubsub_v1.PublisherClient()

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


def create_topic_and_sub(name, project='flint-cloud'):
    """Create topic in the given project and subscribe to it. Returns subscription path"""
    topic_path = publisher.topic_path(project, name)
    try:
        topic = publisher.create_topic(request={'name': topic_path})
    except AlreadyExists:
        pass
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project, f'{name}-sub')
    with subscriber:
        try:
            subscription = subscriber.create_subscription(
                request={'name': subscription_path, 'topic': topic_path}
            )
        except AlreadyExists:
            pass
    return subscription_path


def publish_message(topic, attribs, project='flint-cloud'):
    """Publish message in given topic"""
    msg = json.dumps(attribs).encode('utf-8')
    topic_path = publisher.topic_path(project, topic)
    return publisher.publish(topic_path, msg)


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


@app.route('/gcbm', methods=['POST'])
def gcbm():
    """
            Get GCBM implementation of FLINT
            ---
            tags:
                    - gcbm
            responses:
                    200:
                    description: GCBM Implementation FLINT
            """
    s = time.time()
    if 'file' in request.files:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save(uploaded_file.filename)
        gcbm_config = uploaded_file.filename
    else:
        gcbm_config = 'gcbm_config.cfg'

    if 'input_db' in request.files:
        uploaded_file = request.files['input_db']
        if uploaded_file.filename != '':
            uploaded_file.save('/gcbm_files/input_database/gcbm_input.db')
    config_provider = 'provider_config.json'

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%H:%M:%S.%f - %b %d %Y")
    f = open(timestampStr + "point_example.csv", "w+")
    subprocess.run(["pwd"], cwd="/gcbm_files/config")
    res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', gcbm_config,
                           '--config_provider', config_provider], stdout=f, cwd='/gcbm_files/config')
    e = time.time()
    (output, err) = res.communicate()

    # This makes the wait possible
    res_status = res.wait()
    response = {
        'exitCode': res.returncode,
        'execTime': e - s,
        'response': "Operation executed successfully"
    }
    return {'data': response}, 200
    # return redirect("http://0.0.0.0:8080/gcbm_files/config/..\output", code=302)
    #UPLOAD_DIRECTORY = "./gcbm_files/config/"
    # return send_from_directory(UPLOAD_DIRECTORY,timestampStr + "..\output\gcbm_output.db", as_attachment=True), 200


def upload_blob(title, source_file_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    bucket_name = "simulation_data_flint-cloud"
    # The path to your file to upload
    #source_file_name = "local/path/to/file"
    # The ID of your GCS object
    destination_blob_name = "simulations/simulation-"+title+"/"+source_file_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    logger.debug(
        "File %s uploaded to %s.",
        source_file_name, destination_blob_name
    )


def download_blob(title, source_blob_name):
    """Downloads a file from the bucket."""
    # The ID of your GCS bucket
    bucket_name = "simulation_data_flint-cloud"
    # The path to your file to download
    #source_file_name = "local/path/to/file"
    # The ID of your GCS object
    destination_file_name = source_blob_name
    source_blob_name = "simulations/simulation-"+title+"/"+source_blob_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    logger.debug(
        "File %s downloaded to %s.",
        source_blob_name, destination_file_name
    )


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
    name = 'simulations/simulation-' + title + '/input.zip'
    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    bucket = storage_client.bucket(bucket_name)
    stats = storage.Blob(bucket=bucket, name=name).exists(storage_client)

    if not stats:
        return {'data': "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."}, 200
    else:
        return {'data': "Simulation already exists. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."}, 400


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
    if not os.path.exists(f'/input/{project_dir}'):
        os.makedirs(f'/input/{project_dir}')

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
                with open(f'/input/{project_dir}/provider_config.json', 'w') as pcf:
                    json.dump(provider_config, pcf)
            # Fix paths in modules_output
            elif file.filename == 'modules_output.json':
                modules_output = json.load(file)
                modules_output['Modules']['CBMAggregatorSQLiteWriter']['settings']['databasename'] = 'output/gcbm_output.db'
                modules_output['Modules']['WriteVariableGeotiff']['settings']['output_path'] = 'output'
                with open(f'/input/{project_dir}/modules_output.json', 'w') as mof:
                    json.dump(modules_output, mof)
            else:
                # Save file immediately
                file.save(f'/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing configuration file'}, 400

    # Save input
    if 'input' in request.files:
        for file in request.files.getlist('input'):
            # Save file immediately
            file.save(f'/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing input'}, 400

    # Save db
    if 'db' in request.files:
        for file in request.files.getlist('db'):
            # Save file immediately
            file.save(f'/input/{project_dir}/{file.filename}')
    else:
        return {'error': 'Missing database'}, 400

    # save input in bucket (to maintain state for Cloudrun)
    shutil.make_archive('input', 'zip', f'/input/{project_dir}')
    upload_blob(title, 'input.zip')

    return {"data": "All files uploaded sucessfully. Proceed to the next step of the API at gcbm/dynamic."}, 200


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

    # download input from bucket
    download_blob(title, 'input.zip')
    if not os.path.exists(f'/input/{project_dir}'):
        os.makedirs(f'/input/{project_dir}')
    shutil.unpack_archive('input.zip', f'/input/{project_dir}/')
    os.remove('input.zip')

    thread = Thread(target=launch_run, kwargs={
                    'title': title, 'project_dir': project_dir})
    thread.start()
    subscriber_path = create_topic_and_sub(title)
    return {'status': 'Run started', 'subscription': subscriber_path}, 200


def launch_run(title, project_dir):
    s = time.time()
    logging.debug('Starting run')
    with open(f'/input/{project_dir}/gcbm_logs.csv', 'w+') as f:
        res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', 'gcbm_config.cfg',
                               '--config_provider', 'provider_config.json'], stdout=f, cwd=f'/input/{project_dir}')
    logging.debug('Communicating')
    (output, err) = res.communicate()
    logging.debug('Communicated')
    if not os.path.exists(f'/input/{project_dir}/output'):
        logging.error(err)
        publish_message(title, {'error': err})
        return
    logging.debug('Output exists')
    #returncode = final_run(title, gcbm_config_path, provider_config_path, project_dir)
    shutil.make_archive('output', 'zip', f'/input/{project_dir}/output')
    shutil.rmtree(f'/input/{project_dir}/output')
    logging.debug('Made archive')
    #shutil.make_archive('input', 'zip', f'/input/{project_dir}')
    shutil.rmtree('/input')
    upload_blob(title, 'output.zip')
    logging.debug('Uploaded output')
    #upload_blob(title, 'input.zip')
    e = time.time()

    download_url = generate_download_signed_url_v4(project_dir)
    logging.debug('Generated URL')
    response = {
        'exitCode': res.returncode,
        'execTime': e - s,
        'response': "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body.",
        'urls': download_url
    }
    logging.info(response)
    publish_message(title, response)


def generate_download_signed_url_v4(project_dir):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """

    bucket_name = 'simulation_data_flint-cloud'
    blob_path = 'simulations/simulation-'+project_dir + '/'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob_input = bucket.blob(blob_path+"input.zip")

    url_input = blob_input.generate_signed_url(
        version="v4",
        # This URL is valid for 30 minutes
        expiration=timedelta(minutes=30),
        # Allow GET requests using this URL.
        method="GET",
    )

    blob_output = bucket.blob(blob_path+"output.zip")

    url_output = blob_output.generate_signed_url(
        version="v4",
        # This URL is valid for 30 minutes
        expiration=timedelta(minutes=30),
        # Allow GET requests using this URL.
        method="GET",
    )

    url = {}
    url['input'] = url_input
    url['output'] = url_output
    url['message'] = 'These links are valid only upto 30 mins. Incase the links expire, you may create a new request.'
    return url


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
    url = generate_download_signed_url_v4('simulations/'+project_dir)

    return url, 200


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
    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    blobs = storage_client.list_blobs(bucket_name, prefix='simulations/')
    blob_map = {}
    blob_list = []
    for blob in blobs:
        dir_name = blob.name.split('/')[1]
        if dir_name not in blob_map:
            blob_map[dir_name] = 1
            blob_list.append(dir_name)

    return {'data': blob_list, 'message': "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download."}, 200


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

    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    bucket = storage_client.bucket(bucket_name)
    blob_path = f'simulations/simulation-{title}/output.zip'
    stats = storage.Blob(bucket=bucket, name=blob_path).exists(storage_client)
    return {'finished': stats}


@app.route('/check', methods=['GET', 'POST'])
def check():
    return 'Checks OK', 200


@app.route('/', methods=['GET'])
def home():
    return 'FLINT.Cloud API'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
