import zipfile
import os

#  Unzip file
zip = os.path.join("tests","linux-demo.zip")
with zipfile.ZipFile(zip, "r") as zip_ref:
    zip_ref.extractall("tests")

# template = os.path.join("local", "rest_api_gcbm", "templates.zip")
# extract_to = os.path.join("local", "rest_api_gcbm", "cml_report")
# with zipfile.ZipFile(template, "r") as zip_ref:
#     zip_ref.extractall(extract_to)
