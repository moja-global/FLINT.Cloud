import zipfile

#  Unzip file
zip = 'GCBM_New_Demo_Run.zip'
with zipfile.ZipFile(zip, 'r') as zip_ref:
    zip_ref.extractall('GCBM')
