from flask import Flask, send_from_directory, request, jsonify, redirect
from flask_restful import Resource, Api, reqparse
import os
import subprocess
import time
import json
from datetime import datetime
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_autoindex import AutoIndex
from run_distributed import *

app = Flask(__name__)
ppath = "/"
AutoIndex(app, browse_root=ppath)    
api = Api(app)



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
	json.dump(swag,f)
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
	if arg=='all':
		res = subprocess.run(['/opt/gcbm/moja.cli', '--help'], stdout=subprocess.PIPE)
	else:
		res = subprocess.run(['/opt/gcbm/moja.cli', '--help-section', arg], stdout=subprocess.PIPE)
	e = time.time()
		
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : res.stdout.decode('utf-8')
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
	res = subprocess.run(['/opt/gcbm/moja.cli', '--version'], stdout=subprocess.PIPE)
	e = time.time()
		
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : res.stdout.decode('utf-8')
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
	res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', gcbm_config, '--config_provider', config_provider], stdout=f, cwd='/gcbm_files/config')
	e = time.time()
	(output, err) = res.communicate()  

	#This makes the wait possible
	res_status = res.wait()
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : "Operation executed successfully"
	}
	return {'data': response}, 200
	#return redirect("http://0.0.0.0:8080/gcbm_files/config/..\output", code=302)
	#UPLOAD_DIRECTORY = "./gcbm_files/config/"	
	#return send_from_directory(UPLOAD_DIRECTORY,timestampStr + "..\output\gcbm_output.db", as_attachment=True), 200


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

	# Create project directory
	project_dir = f'{title}-{time.time()}'
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
				provider_config['Providers']['SQLite']['path'] = fix_path(provider_config['Providers']['SQLite']['path'])
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

	s = time.time()
	f = open(f'/input/{project_dir}/gcbm_logs.csv', 'w+')
	res = subprocess.Popen(['/opt/gcbm/moja.cli', '--config_file', 'gcbm_config.cfg', '--config_provider', 'provider_config.json'], stdout=f, cwd=f'/input/{project_dir}')
	e = time.time()
	(output, err) = res.communicate()  

	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : "Operation executed successfully"
	}
	return {'data': response}, 200

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
