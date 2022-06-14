import os
import zipfile

zip = 'output.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('output')