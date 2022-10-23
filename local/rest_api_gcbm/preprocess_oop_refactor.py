from nis import cat
import os
import shutil
import json
from unicodedata import category
import rasterio as rst
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from threading import Thread
from app import launch_run

app = Flask(__name__)
# creating an API object
api = Api(app)


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


class EditConfig(Resource):

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


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


class GCBMSimulation:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.Rastersm = []
        self.rasters = []
        self.paths = []
        self.nodatam = []
        self.dictionary = {}
        self.study_area = {}
        self.provider_config = open(
            f"{self.input_dir}/templates/provider_config.json", "r+"
        )

    def get_uploaded_files_details(self):
        with open(
            f"{self.input_dir}/upload_details.json", "w+", encoding="utf8"
        ) as upload_details:
            upload_details_dictionary = json.load(upload_details)
        return upload_details_dictionary

    def set_config_templates(self):
        if not os.path.exists(f"{self.input_dir}/templates"):
            shutil.copytree(
                f"{os.getcwd()}/templates",
                f"{self.input_dir}/templates",
                dirs_exist_ok=False,
            )

    def add_database_to_provider_config(self):
        data = json.load(self.provider_config)
        upload_details_dictionary = self.get_uploaded_files_details()
        for file in upload_details_dictionary:
            if file["category"] == "db":
                data["Providers"]["SQLite"] = {"path": file["path"], "type": "SQLite"}
        self.provider_config.seek(0)

    # disturbances, #classifiers, #miscellaneous e.t.c,
    def add_files_to_provider_config_layers(self):
        data = json.load(self.provider_config)
        layer = []
        upload_details_dictionary = self.get_uploaded_files_details()
        for file in upload_details_dictionary:
            dic = {
                "name": file,
                "layer_path": file["path"],
                "layer_prefix": file["path"][:5],
            }
            layer.append(dic)
        data["Providers"]["RasterTiled"]["layers"] += layer

    def generate_provider_config(self):
        data = json.load(self.provider_config)
        nodata = []
        cellLatSize = []
        cellLonSize = []

        # if there is disturbances.
        upload_details_dictionary = self.get_uploaded_files_details()
        for file in upload_details_dictionary:
            if file["category"] == "disturbances":
                self.rasters.append(file["path"])

        for nd in self.rasters:
            img = rst.open(nd)
            t = img.transform
            x = t[0]
            y = -t[4]
            n = img.nodata
            cellLatSize.append(x)
            cellLonSize.append(y)
            nodata.append(n)

        result = all(element == cellLatSize[0] for element in cellLatSize)
        print(result)
        if result:
            cellLat = x
            cellLon = y
            nd = n
            blockLat = x * 400
            blockLon = y * 400
            tileLat = x * 4000
            tileLon = y * 4000
        else:
            print("Corrupt files")

        self.provider_config.seek(0)

        data["Providers"]["RasterTiled"]["cellLonSize"] = cellLon
        data["Providers"]["RasterTiled"]["cellLatSize"] = cellLat
        data["Providers"]["RasterTiled"]["blockLonSize"] = blockLon
        data["Providers"]["RasterTiled"]["blockLatSize"] = blockLat
        data["Providers"]["RasterTiled"]["tileLatSize"] = tileLat
        data["Providers"]["RasterTiled"]["tileLonSize"] = tileLon

        json.dump(data, self.provider_config, indent=4)
        self.provider_config.truncate()

        self.dictionary = {
            "layer_type": "GridLayer",
            "layer_data": "Byte",
            "nodata": nd,
            "tileLatSize": tileLat,
            "tileLonSize": tileLon,
            "blockLatSize": blockLat,
            "blockLonSize": blockLon,
            "cellLatSize": cellLat,
            "cellLonSize": cellLon,
        }

        self.study_area = {
            "tile_size": tileLat,
            "block_size": blockLat,
            "tiles": [{"x": int(t[2]), "y": int(t[5]), "index": 12674}],
            "pixel_size": cellLat,
            "layers": [],
        }

    def set_attributes(self, file_name: str, payload: dict):
        with open(
            f"{self.input_dir}/{file_name}.json", "w", encoding="utf8"
        ) as json_file:
            self.dictionary["attributes"] = payload
            json.dump(self.dictionary, json_file, indent=4)

    def set_study_area(self):
        with open(
            f"{self.input_dir}/study_area.json", "w", encoding="utf"
        ) as json_file:
            study_area = []

            upload_details_dictionary = self.get_uploaded_files_details()
            for file in upload_details_dictionary:
                if file["category"] == "miscellaneous":
                    study_area.append({"name": file[:10], "type": "VectorLayer"})
                elif file["category"] == "classifiers":
                    study_area.append(
                        {
                            "name": file[:10],
                            "type": "VectorLayer",
                            "tags": ["classifier"],
                        }
                    )
                elif file["category"] == "disturbances":
                    study_area.append(
                        {
                            "name": file[:10],
                            "type": "VectorLayer",
                            "tags": ["classifier"],
                        }
                    )
                    study_area.append(
                        {
                            "name": file[:10],
                            "type": "DisturbanceLayer",
                            "tags": ["disturbance"],
                        }
                    )

            self.study_area["layers"] = study_area
            json.dump(self.study_area, json_file, indent=4)
