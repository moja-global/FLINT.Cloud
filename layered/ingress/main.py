from flask import Flask, request
from google.cloud import storage, pubsub_v1
from google.api_core.exceptions import AlreadyExists
from googleapiclient import discovery
from datetime import timedelta
import json
import logging
import os
import shutil
from estimate_run_size import SimulationSize, estimate_simulation_size


app = Flask(__name__)

project = os.environ.get('PROJECT_NAME') or 'flint-cloud'
zone = os.environ.get('GCE_ZONE') or 'us-central1-a'
instance = os.environ.get('GCE_NAME') or 'instance-1'
with open('service_account.json', 'w') as saf:
    saf.write(os.environ.get('SERVICE_ACCOUNT') or 'ERROR')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'
publisher = pubsub_v1.PublisherClient()


def create_topic(name, project=project):
    """Create topic in the given project and subscribe to it. Returns subscription path"""
    topic_path = publisher.topic_path(project, name)
    try:
        topic = publisher.create_topic(request={'name': topic_path})
    except AlreadyExists:
        pass


def create_sub(name, project=project):
    topic_path = publisher.topic_path(project, name)
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


def publish_message(topic, data, project=project):
    """Publish message in given topic"""
    create_topic(topic)
    msg = json.dumps(data).encode('utf-8')
    topic_path = publisher.topic_path(project, topic)
    return publisher.publish(topic_path, msg)


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

    logging.debug(
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

    logging.debug(
        "File %s downloaded to %s.",
        source_blob_name, destination_file_name
    )


def estimate_size(project_dir):
    try:
        size = 'Large' if estimate_simulation_size(
            project_dir) == SimulationSize.Large else 'Small'
    except:
        size = 'Small'
    return {'size': size}


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

    # Save information about the size of simulation
    sim_size = estimate_size(f'/input/{project_dir}')
    with open(f'size.json', 'w') as f:
        json.dump(sim_size, f)
    upload_blob(title, 'size.json')

    return {"data": "All files uploaded sucessfully. Proceed to the next step of the API at gcbm/dynamic."}, 200


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

    # Verify output exists
    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    bucket = storage_client.bucket(bucket_name)
    blob_path = f'simulations/simulation-{title}/output.zip'
    stats = storage.Blob(bucket=bucket, name=blob_path).exists(storage_client)
    return {'finished': stats}


def small_run(data):
    """Publish message for small run on Pub/Sub"""
    publish_message('small-simulations', data)


def large_run(data):
    """Start GCE instance and publish  message for large run on Pub/Sub"""
    service = discovery.build('compute', 'v1')

    request = service.instances().start(project=project, zone=zone, instance=instance)
    response = request.execute()
    logging.info(response)

    publish_message('large-simulations', data)


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

    # Verify simulation exists
    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    bucket = storage_client.bucket(bucket_name)
    blob_path = f'simulations/simulation-{title}/input.zip'
    stats = storage.Blob(bucket=bucket, name=blob_path).exists(storage_client)
    if not stats:
        return {'error': 'Simulation not found!'}, 404

    # Create topic and subscriber for simulation
    topic_name = f'sim-{title}'
    create_topic(topic_name)
    subscriber_path = create_sub(topic_name)

    # Submit simulation to Cloud Run/Compute Engine via Pub/Sub
    # TODO: Determine where to submit the simulation by estimating runtime
    # TODO: Modify config according to selected environment
    sim_data = {
        'topic': topic_name,
        'title': title,
        'subscription': subscriber_path
    }

    # Get simulation size details and forward to appropriate service
    download_blob(title, 'size.json')
    with open('size.json') as f:
        sim_size = json.load(f)

    if sim_size['size'] == 'Small':
        small_run(sim_data)
    else:
        large_run(sim_data)

    return {'status': 'Run started', 'subscription': subscriber_path}, 200


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
    url = generate_download_signed_url_v4(project_dir)

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


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(host='0.0.0.0', port=PORT)
