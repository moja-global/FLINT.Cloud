import os
import shutil
import json
import rasterio as rst



class GCBM:
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

    def set_config_templates(self):
        if not os.path.exists(f"{self.input_dir}/templates"):
            shutil.copytree(
                f"{os.getcwd()}/templates",
                f"{self.input_dir}/templates",
                dirs_exist_ok=False,
            )

    def add_disturbances_to_modules_cbm_config(self):
        with open(
            f"{self.input_dir}/templates/modules_cbm.json", "r+"
        ) as modules_cbm_config:
            disturbances = []
            data = json.load(modules_cbm_config)
            for file in os.listdir(f"{self.input_dir}/disturbances/"):
                disturbances.append(file.split(".")[0][:-5])
            modules_cbm_config.seek(0)
            data["Modules"]["CBMDisturbanceListener"]["settings"]["vars"] = disturbances
            json.dump(data, modules_cbm_config, indent=4)
            modules_cbm_config.truncate()

    def add_database_to_provider_config(self):
        data = json.load(self.provider_config)
        for file in os.listdir(f"{self.input_dir}/db/"):
            data["Providers"]["SQLite"] = {"path": file, "type": "SQLite"}
        self.provider_config.seek(0)

    # disturbances, #classifiers, #miscellaneous,
    def add_variables_to_provider_config_layers(self, variable):
        data = json.load(self.provider_config)
        lst = []
        for file in os.listdir(f"{self.input_dir}/{variable}/"):
            dic = {"name": file[:10], "layer_path": file, "layer_prefix": file[:5]}
            lst.append(dic)
        self.provider_config.seek(0)
        data["Providers"]["RasterTiled"]["layers"] += lst

    def generate_provider_config(self):
        data = json.load(self.provider_config)
        nodata = []
        cellLatSize = []
        cellLonSize = []

        for root, _, files in os.walk(
            os.path.abspath(f"{self.input_dir}/disturbances/")
        ):
            for file in files:
                fp = os.path.join(root, file)
                self.Rasters.append(fp)
                self.paths.append(fp)

        for root, _, files in os.walk(
            os.path.abspath(f"{self.input_dir}/classifiers/")
        ):
            for file in files:
                fp1 = os.path.join(root, file)
                self.Rasters.append(fp1)
                self.paths.append(fp1)

        for nd in self.Rasters:
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
            "tiles": [{"x": int(t[2]), "y": int(t[5]), "index": 12674,}],
            "pixel_size": cellLat,
            "layers": [],
        }

    def get_input_json(self):
        for root, _, files in os.walk(
            os.path.abspath(f"{self.input_dir}/miscellaneous/")
        ):
            for file in files:
                fp2 = os.path.join(root, file)
                self.Rastersm.append(fp2)

            for i in self.Rastersm:
                img = rst.open(i)
                d = img.nodata
                self.nodatam.append(d)

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

            for file in os.listdir(f"{self.input_dir}/miscellaneous/"):
                study_area.append({"name": file[:10], "type": "VectorLayer"})

            for file in os.listdir(f"{self.input_dir}/classifiers/"):
                study_area.append(
                    {"name": file[:10], "type": "VectorLayer", "tags": ["classifier"]}
                )

            for file in os.listdir(f"{self.input_dir}/disturbances/"):
                study_area.append(
                    {
                        "name": file[:10],
                        "type": "DisturbanceLayer",
                        "tags": ["disturbance"],
                    }
                )

            self.study_area["layers"] = study_area
            json.dump(self.study_area, json_file, indent=4)

    def add_file_path(self, variable):
        for root, _, files in os.walk(os.path.abspath(f"{self.input_dir}/{variable}/")):
            for file in files:
                fp = os.path.join(root, file)
                self.paths.append(fp)

    def copy_files_to_input_directory(self):
        for i in self.paths:
            shutil.copy2(i, (f"{self.input_dir}"))

    def clean_up_directory(self, variable):
        shutil.rmtree((f"{self.input_dir}/{variable}/"))


##test run
