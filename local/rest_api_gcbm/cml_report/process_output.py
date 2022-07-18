import os
import zipfile

zip = 'test-run.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('output')