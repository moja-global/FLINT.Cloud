import zipfile
import os

#  Unzip file
zip = 'GCBM_New_Demo_Run.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('GCBM')

template = os.path.join('local','rest_api_gcbm','templates.zip')
extract_to = os.path.join('local','rest_api_gcbm')
with zipfile.ZipFile(template, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

templates_path = os.path.join('local','rest_api_gcbm','templates')
new_templates_path = os.path.join('local','rest_api_gcbm','template')
os.rename(templates_path,new_templates_path)