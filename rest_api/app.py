from flask import Flask, send_from_directory
from flask_restful import Resource, Api, reqparse
import os
import subprocess
import time
from datetime import datetime

app = Flask(__name__)
api = Api(app)

@app.route('/help/<string:arg>')
def help(arg):
	# return our data and 200 OK HTTP code
	s = time.time()
	if arg=='all':
		res = subprocess.run(['moja.cli', '--help'], stdout=subprocess.PIPE)
	else:
		res = subprocess.run(['moja.cli', '--help-section', arg], stdout=subprocess.PIPE)
	e = time.time()
		
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : res.stdout.decode('utf-8')
	}
	return {'data': response}, 200


@app.route('/version')
def version():
	# return our data and 200 OK HTTP code
	s = time.time()
	res = subprocess.run(['moja.cli', '--version'], stdout=subprocess.PIPE)
	e = time.time()
		
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : res.stdout.decode('utf-8')
	}
	return {'data': response}, 200


@app.route('/point')
def point():
	# return our data and 200 OK HTTP code
	s = time.time()
	point_example = 'config/point_example.json'
	lib_simple = 'config/libs.base.simple.json'
	logging_debug = 'config/logging.debug_on.conf'

	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("%H:%M:%S.%f - %b %d %Y")
	f = open("output_files/"+timestampStr + "point_example.csv", "w+")
	res = subprocess.run(['moja.cli', '--config', point_example, '--config', lib_simple, '--logging_config', logging_debug], stdout=f)
	e = time.time()
	UPLOAD_DIRECTORY = "./"	
	'''
	response = {
		'exitCode' : res.returncode,
		'execTime' : e - s,
		'response' : send_from_directory(UPLOAD_DIRECTORY,"output_files/"+timestampStr + "point_example.csv", as_attachment=True)
	}
	'''
	return send_from_directory(UPLOAD_DIRECTORY,"output_files/"+timestampStr + "point_example.csv", as_attachment=True), 200


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
