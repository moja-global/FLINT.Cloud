import base64
import logging
import os
import json
import shutil
import time
import subprocess
from datetime import timedelta
from flask import Flask, request
from google.cloud import storage, pubsub_v1
from google.api_core import retry
from google.api_core.exceptions import AlreadyExists


app = Flask(__name__)

project = os.environ.get('PROJECT_NAME') or 'flint-cloud'
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


def publish_message(topic, attribs, project=project):
    """Publish message in given topic"""
    msg = json.dumps(attribs).encode('utf-8')
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


def delete_blob(title, source_file_name):
    """Deletes a file to from the bucket."""
    # The ID of your GCS bucket
    bucket_name = "simulation_data_flint-cloud"
    # The path to your file to upload
    #source_file_name = "local/path/to/file"
    # The ID of your GCS object
    destination_blob_name = "simulations/simulation-"+title+"/"+source_file_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.delete()

    logging.debug(
        "Deleted %s.",
        destination_blob_name
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


def create_log(title):
    """Create log file"""
    with open('log.txt', 'w+') as lf:
        lf.write(time.ctime() + '\n')
    upload_blob(title, 'log.txt')


def check_log(title):
    """Check for log"""
    storage_client = storage.Client()
    bucket_name = 'simulation_data_flint-cloud'
    bucket = storage_client.bucket(bucket_name)
    blob_path = f'simulations/simulation-{title}/log.txt'
    return storage.Blob(bucket=bucket, name=blob_path).exists(storage_client)


def cleanup_log(title):
    """Erase log file"""
    delete_blob(title, 'log.txt')


@app.route('/', methods=['POST'])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = 'no Pub/Sub message received'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        msg = 'invalid Pub/Sub message format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    pubsub_message = envelope['message']

    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
        msg = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()
        data = json.loads(msg)
        topic_name = data['topic']
        topic_path = publisher.topic_path(project, topic_name)
        title = data['title']

        # Exit if input exists already
        if os.path.exists(f'/input/{title}'):
            return '', 204

        if check_log(title):
            return '', 204
        create_log(title)

        # Publish info message
        info_msg = {'message': 'Simulation started'}
        publish_message(topic_name, info_msg)

        # download input from bucket
        download_blob(title, 'input.zip')
        if not os.path.exists(f'/input/{title}'):
            os.makedirs(f'/input/{title}')
        shutil.unpack_archive('input.zip', f'/input/{title}/')
        os.remove('input.zip')

        s = time.time()
        logging.debug('Starting run')
        with open(f'/input/{title}/gcbm_logs.csv', 'w+') as f:
            res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', 'gcbm_config.cfg',
                                    '--config_provider', 'provider_config.json'], stdout=f, cwd=f'/input/{title}')
        logging.debug('Communicating')
        (output, err) = res.communicate()
        logging.debug('Communicated')
        if not os.path.exists(f'/input/{title}/output'):
            logging.error(err)
            publish_message(topic_name, {'error': err})
            return
        logging.debug('Output exists')
        #returncode = final_run(title, gcbm_config_path, provider_config_path, title)
        shutil.make_archive('output', 'zip', f'/input/{title}/output')
        shutil.rmtree(f'/input/{title}/output')
        logging.debug('Made archive')
        #shutil.make_archive('input', 'zip', f'/input/{title}')
        shutil.rmtree('/input')
        upload_blob(title, 'output.zip')
        logging.debug('Uploaded output')
        #upload_blob(title, 'input.zip')
        e = time.time()

        download_url = generate_download_signed_url_v4(title)
        logging.debug('Generated URL')
        response = {
            'exitCode': res.returncode,
            'execTime': e - s,
            'response': "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body.",
            'urls': download_url
        }
        logging.info(response)
        publish_message(topic_name, response)
        cleanup_log(title)

    return '', 204


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080
    app.run(host='0.0.0.0', port=PORT)
