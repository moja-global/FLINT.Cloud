import os
import zipfile

zip = "run4.zip"
with zipfile.ZipFile(zip, "r") as zip_ref:
    zip_ref.extractall("output")
