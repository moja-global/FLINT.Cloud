import os
import zipfile

output_zip = 'output.zip'
if zipfile.is_zipfile(output_zip):
    with zipfile.ZipFile(output_zip, 'r') as zip_ref:
        zip_ref.extractall('output')
