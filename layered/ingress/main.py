from flask import Flask, request
from google.cloud import storage, pubsub_v1
from google.api_core.exceptions import AlreadyExists
from googleapiclient import discovery
import json
import logging
import os
import shutil


app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'flint-cloud-baec10f8dd27.json'
publisher = pubsub_v1.PublisherClient()


def create_topic(name, project='flint-cloud'):
    """Create topic in the given project and subscribe to it. Returns subscription path"""
    topic_path = publisher.topic_path(project, name)
    try:
        topic = publisher.create_topic(request={'name': topic_path})
    except AlreadyExists:
        pass


def create_sub(name, project='flint-cloud'):
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


def publish_message(topic, data, project='flint-cloud'):
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

    project = 'flint-cloud'
    zone = 'us-central1-a'
    instance = 'instance-1'

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
    small_run(sim_data)
    # large_run(sim_data)

    return {'status': 'Run started', 'subscription': subscriber_path}, 200


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(host='0.0.0.0', port=PORT)
