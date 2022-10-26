from nis import cat
import os
import shutil
import json
from unicodedata import category
from .preprocess import GCBMSimulation
import rasterio as rst
from flask import  jsonify, request
from flask_restful import Resource
from threading import Thread
from .utils import launch_run




class Gcbm(Resource):

    #create new gcbm 
    def post(self):
        title = request.form.get("title") or "simulation"
        title = "".join(c for c in title if c.isalnum())
        # input_dir = f"{title}"
        input_dir = f"{os.getcwd()}/input/{title}"
        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")
            message = "New {title} simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
        else:
            message = "Simulation already exists with name {title}. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."
        return {"data": message}, 200

    #get a list of simulations
    def get(self):
        pass



""" 

Upload details stores the information about the files upload in a json file.

sample_db = {
    "filename":{
        "path": "",
        "category":"disturbance"
    },
    "filename": {
        "path": "",
        "category": "classifier"
    }
} """


class GbcmUpload(Resource):

    # this is used to fetch all files uploaded in regards to that simulation
    def get(self):
        title = request.form.get("title") or "simulation"
        input_dir = f"{os.getcwd()}/input/{title}"
        if os.path.exists(f"{input_dir}/upload_details.json"):
            with open(
                f"{input_dir}/upload_details.json", "w+", encoding="utf8"
            ) as upload_details:
                upload_details_dictionary = json.load(upload_details)
                return jsonify(
                    {
                        "message": "File retrived successfully",
                        "data": upload_details_dictionary,
                    }
                )

    # upload files to a paticular category.
    def post(self):
        """ sample - payload ={
        "title": "run4",
        "file": "file-uploaded",
        "category": "classifier"
        } """

        title = request.form.get("title") or "simulation"
        category = request.args.get("category")
        files = request.files.getlist("file")

        input_dir = f"{os.getcwd()}/input/{title}"

        if os.path.exists(f"{input_dir}/upload_details.json"):
            with open(
                f"{input_dir}/upload_details.json", "w+", encoding="utf8"
            ) as upload_details:
                upload_details_dictionary = json.load(upload_details)
        else:
            with open(
                f"{input_dir}/upload_details.json", "w", encoding="utf8"
            ) as upload_details:
                upload_details_dictionary = {}
        #     uploadDetailsDictionary = json.load(upload_details)
        # print(uploadDetailsDictionary)

        for file in files:
            file.save(f"{input_dir}/{file.filename}")
            upload_details_dictionary[file.filename] = {
                "path": f"{input_dir}/{file.filename}",
                "category": category,
            }
        json.dump(upload_details_dictionary, upload_details, indent=4)

        return {
            "data": "All files uploaded succesfully. Proceed to the next step of the API at gcbm/dynamic."
        }


class Config(Resource):

    # this get request will fetch the config templates. E.g modules.json, provider.json , and return them so that user can see them as seen on flint UI here -- https://flint-ui.vercel.app/gcbm/configurations/local-domain
    def get(self):
        pass

    def post(self):
        pass


# Running the simulation
class GcbmRun(Resource):
    def post(self):
        title = request.form.get("title") or "simulation"
        input_dir = f"{os.getcwd()}/input/{title}"

        gcbm_simulation = GCBMSimulation(input_dir=input_dir)
        gcbm_simulation.set_config_templates()
        gcbm_simulation.add_database_to_provider_config()
        gcbm_simulation.add_files_to_provider_config_layers()
        gcbm_simulation.generate_provider_config()

        thread = Thread(
            target=launch_run, kwargs={"title": title, "input_dir": input_dir}
        )
        thread.start()
        return {"status": "Run started"}, 200


class DownloadGcbmResult(Resource):
    
    #download result /or check status of list is not avaliable
    def get(self):
        pass

