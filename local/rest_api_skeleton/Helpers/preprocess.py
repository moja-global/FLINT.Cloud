import os, time, subprocess
import shutil
import json
import rasterio as rst

def launch_run(title, input_dir): 
    s = time.time()
    with open(f"{input_dir}/gcbm_logs.csv", "w+") as f:
        res = subprocess.Popen(
            [
                "/opt/gcbm/moja.cli",
                "--config_file",
                "gcbm_config.cfg",
                "--config_provider",
                "provider_config.json",
            ],
            stdout=f,
            cwd=f"{input_dir}",
        )
    (_, err) = res.communicate()

    if not os.path.exists(f"{input_dir}/output"):
        return "OK"

    # cut and paste output folder to app/output/simulation_name
    shutil.copytree(f"{input_dir}/output", (f"{os.getcwd()}/output/{title}"))
    shutil.make_archive(
        f"{os.getcwd()}/output/{title}", "zip", f"{os.getcwd()}/output/{title}"
    )
    shutil.rmtree((f"{input_dir}/output"))
    e = time.time()

    response = {
        "exitCode": res.returncode,
        "execTime": e - s,
        "response": "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body.",
    }

class Configs:

    def __init__(self, input_dir) -> None:
        self.input_dir = input_dir
        self.Rasters = []
        self.Rastersm = []  
        self.nodatam = []
        self.nodata = []
        self.cellLatSize = []
        self.cellLonSize = []
        self.paths = []
        self.lst = []
        self.provider_config = open(f"{os.getcwd()}/templates/provider_config.json", "r+")  

    def get_config_templates(self):
        if not os.path.exists(f"{self.input_dir}/templates"):
            shutil.copytree(
                f"{os.getcwd()}/templates", f"{self.input_dir}/templates", dirs_exist_ok=False
            )
            self.provider_config = open(f"{self.input_dir}/templates/provider_config.json", "r+")

    def get_modules_cbm_config(self):
        with open(f"{self.input_dir}/templates/modules_cbm.json", "r+") as modules_cbm_config:
            data = json.load(modules_cbm_config)
            disturbances = [file.split(".")[0][:-5] for file in os.listdir(f"{self.input_dir}/disturbances/")]  # drop `_moja` to match modules_cbm.json template
            modules_cbm_config.seek(0)  
            data["Modules"]["CBMDisturbanceListener"]["settings"]["vars"] = disturbances
            json.dump(data, modules_cbm_config, indent=4)
            modules_cbm_config.truncate()

    # for database input
    def database_writes(self):
        data = json.load(self.provider_config)
        for file in os.listdir(f"{self.input_dir}/db/"):
            data["Providers"]["SQLite"] = {"type": "SQLite", "path": file }
        self.provider_config.seek(0)


    def write_configs(self, config_type : str):
        data = json.load(self.provider_config)
        for file in os.listdir(f"{self.input_dir}/{config_type}/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = file
            d["layer_prefix"] = file[:-5]
            self.lst.append(d)
        if config_type == "disturbances" or config_type == "classifiers": 
            for root, _, files in os.walk(
                os.path.abspath(f"{self.input_dir}/{config_type}/")
            ):
                for file in files:
                    fp = os.path.join(root, file)
                    self.Rasters.append(fp)
                    self.paths.append(fp)
        for self.nd in self.Rasters:
            img = rst.open(self.nd)  
            t = img.transform 
            x = t[0]
            y = -t[4]
            n = img.nodata 
            self.cellLatSize.append(x)
            self.cellLonSize.append(y)
            self.nodata.append(n)
        result = all(element == self.cellLatSize[0] for element in self.cellLatSize)  
        if result:
            cellLat = x
            cellLon = y
            self.nd = n
            blockLat = x * 400
            blockLon = y * 400
            tileLat = x * 400
            tileLon = y * 4000
        else:
            print("Corrupt files")

        self.provider_config.seek(0)
        new_values = {"cellLonSize": cellLon,"cellLatSize": cellLat, "blockLonSize": blockLon, "blockLatSize": blockLat, "tileLatSize": tileLat, "tileLonSize": tileLon}
        data["Providers"]["RasterTiled"]["layers"] = self.lst  
        data["Providers"]["RasterTiled"].update(new_values)

        json.dump(data, self.provider_config, indent=4)
        self.provider_config.truncate()

        self.dictionary = {
            "layer_type": "GridLayer",
            "layer_data": "Byte",
            "nodata": self.nd,
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
                "tiles": [
                    {
                        "x": int(t[2]),
                        "y": int(t[5]),
                        "index": 12674,
                    }
                ],
                "pixel_size": cellLat,
                "layers": [],
            }

    def add_file_to_path(self, config_type):
        for root, _, files in os.walk(os.path.abspath(f"{self.input_dir}/{config_type}/")):
            for file in files:
                fp = os.path.join(root, file)
                self.paths.append(fp)

    def copy_directory(self):
        for i in self.paths:
            shutil.copy2(i, (f"{self.input_dir}"))

    def flatten_directory(self, config_type):
        shutil.rmtree((f"{self.input_dir}/{config_type}/"))
    
class DisturbanceConfig(Configs):
    def __init__(self, input_dir, config_file : str, attribute : dict = None ) -> None:
        super().__init__(input_dir)
        self.config_file = config_file
        self.attribute = attribute

    def disturbances_special(self):
        with open(f"{self.input_dir}/{self.config_file}", "w", encoding="utf8") as json_file:
            self.dictionary["attributes"] = self.attribute
            json.dump(self.dictionary, json_file, indent=4)
        with open(
            f"{self.input_dir}/study_area.json", "w", encoding="utf"
        ) as json_file:
            study_area = []
            self.study_area["layers"] = study_area
            json.dump(self.study_area, json_file, indent=4)
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

    def __call__(self):
        self.get_config_templates()
        self.get_modules_cbm_config()
        self.write_configs("disturbances")
        self.disturbances_special()
        self.add_file_to_path("disturbances")
        self.copy_directory()

class ClassifierConfig(Configs):
    def __init__(self, input_dir, config_file : str, attribute : dict ) -> None:
        super().__init__(input_dir)
        self.config_file = config_file
        self.attribute = attribute

    def classifier_special(self):
        with open(f"{self.input_dir}/{self.config_file}", "w", encoding="utf8") as json_file:
            self.dictionary["attributes"] = self.attribute
            json.dump(self.dictionary, json_file, indent=4)

        with open(
            f"{self.input_dir}/study_area.json", "w", encoding="utf"
        ) as json_file:
            study_area = []
            for file in os.listdir(f"{self.input_dir}/classifiers/"):
                study_area.append(
                    {"name": file[:10], "type": "VectorLayer", "tags": ["classifier"]}
                )

            self.study_area["layers"] = study_area
            json.dump(self.study_area, json_file, indent=4)

        def __call__(self):
            self.get_config_templates()
            self.get_modules_cbm_config()
            self.write_configs("classifiers")
            self.classifier_special()
            self.add_file_to_path("classifiers")
            self.copy_directory()

class MiscellaneousConfig(Configs):
    def __init__(self, input_dir, config_file : str, attribute : dict ) -> None:
        super().__init__(input_dir)
        self.config_file = config_file
        self.attribute = attribute
        
    def miscellaneous_special(self):    
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
        """this is an experimental thing"""
        with open(f"{self.input_dir}/{self.config_file}", "w", encoding="utf8") as json_file:
            self.dictionary["layer_type"] = "GridLayer"
            if self.config_file ==  "mean_annual_temperature_moja.json":
                self.dictionary["layer_data"] = "Float32"
            else:
                self.dictionary["layer_data"] = "Int16"
            self.dictionary["nodata"] = 32767
            json.dump(self.dictionary, json_file, indent=4)

        # for study area
        with open(
            f"{self.input_dir}/study_area.json", "w", encoding="utf"
        ) as json_file:
            study_area = []

            for file in os.listdir(f"{self.input_dir}/miscellaneous/"):
                study_area.append({"name": file[:10], "type": "VectorLayer"})

            self.study_area["layers"] = study_area
            json.dump(self.study_area, json_file, indent=4)

        def __call__(self):
            self.get_config_templates()
            self.get_modules_cbm_config()
            self.write_configs("miscellaneous")
            self.classifier_special()
            self.add_file_to_path("miscellaneous")
            self.copy_directory()
            self.flatten_directory("miscellaneous")


