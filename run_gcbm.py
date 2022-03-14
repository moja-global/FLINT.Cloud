# Docker-compose up the database and the web server
# Extract the zip file and store it in the folder
# Call the endpoints to get the results
# Show the output in nice visual way

import subprocess


import os
os.system('cd local/rest_api_gcbm/ && docker-compose up -d')

