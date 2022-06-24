import os
import zipfile
import requests
import json

#  Unzip file
zip = 'GCBM_Demo_Run.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('GCBM')

os.chdir(os.path.join('GCBM','GCBM_Demo_Run'))

url = "http://localhost:8080/gcbm/upload"

files = {
    'config_files': open(os.path.join('config','variables.json'),'rb'),
    'config_files': open(os.path.join('config','spinup.json'),'rb'),
    'config_files': open(os.path.join('config','provider_config.json'),'rb'),
    'config_files': open(os.path.join('config','pools_cbm.json'),'rb'),
    'config_files': open(os.path.join('config','modules_output.json'),'rb'),
    'config_files': open(os.path.join('config','modules_cbm.json'),'rb'),
    'config_files': open(os.path.join('config','logging.conf'),'rb'),
    'config_files': open(os.path.join('config','localdomain.json'),'rb'),
    'config_files': open(os.path.join('config','internal_variables.json'),'rb'),
    'config_files': open(os.path.join('config','gcbm_config.cfg'),'rb'),
    'input': open(os.path.join('layers','tiled','bounding_box.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','Classifier1_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','Classifier1_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','Classifier2_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','Classifier2_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2011_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2011_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2012_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2012_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2013_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2013_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2014_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2014_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2015_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2015_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2016_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2016_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2018_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','disturbances_2018_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','initial_age_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','initial_age_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','mean_annual_temperature_moja.json'),'rb'),
    'input': open(os.path.join('layers','tiled','mean_annual_temperature_moja.tiff'),'rb'),
    'input': open(os.path.join('layers','tiled','study_area.json'),'rb'),
    'input': open(os.path.join('input_database','gcbm_input.db'),'rb'),
    'db': open(os.path.join('input_database','gcbm_input.db'),'rb'),
    'title':'run4'
}

res = requests.post(url,files=files)
print(json.loads(res.text))
