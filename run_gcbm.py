# Docker-compose up the database and the web server
# Extract the zip file and store it in the folder
# Call the endpoints to get the results
# Show the output in nice visual way

#import subprocess
import zipfile
import os

os.system('cd local/rest_api_gcbm/ && docker-compose up -d')
zip_dir = os.path.dirname(os.path.realpath(__file__)) + "/GCBM_Demo_Run.zip"
to_extract_path = os.path.dirname(os.path.realpath(__file__)) + "/GCBM_Demo_Run"
if not os.path.isfile(to_extract_path):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "/GCBM_Demo_Run")
unzipped_file = zipfile.ZipFile(zip_dir, "r")
unzipped_file.extractall(to_extract_path)
