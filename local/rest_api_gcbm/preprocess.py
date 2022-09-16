import os
import shutil
import json
import rasterio as rst


def get_config_templates(input_dir):
    if not os.path.exists(f"{input_dir}/templates"):
        shutil.copytree(
            f"{os.getcwd()}/templates", f"{input_dir}/templates", dirs_exist_ok=False
        )


# TODO: there needs to be a link between the files configured here append
# the ["vars"] attribute of modules_cbm.json -> CBMDisturbanceListener
# current hack is to drop the last five characters, but thats very fragile
def get_modules_cbm_config(input_dir):
    with open(f"{input_dir}/templates/modules_cbm.json", "r+") as modules_cbm_config:
        disturbances = []
        data = json.load(modules_cbm_config)
        for file in os.listdir(f"{input_dir}/disturbances/"):
            disturbances.append(
                file.split(".")[0][:-5]
            )  # drop `_moja` to match modules_cbm.json template
        modules_cbm_config.seek(0)
        data["Modules"]["CBMDisturbanceListener"]["settings"]["vars"] = disturbances
        json.dump(data, modules_cbm_config, indent=4)
        modules_cbm_config.truncate()


def get_provider_config(input_dir):
    with open(f"{input_dir}/templates/provider_config.json", "r+") as provider_config:
        lst = []
        data = json.load(provider_config)

        for file in os.listdir(f"{input_dir}/db/"):
            d = dict()
            d["path"] = file
            d["type"] = "SQLite"
            data["Providers"]["SQLite"] = d
        provider_config.seek(0)

        for file in os.listdir(f"{input_dir}/disturbances/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = file
            d["layer_prefix"] = file[:-5]
            lst.append(d)
        provider_config.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{input_dir}/classifiers/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = file
            d["layer_prefix"] = file[:-5]
            lst.append(d)
        provider_config.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        for file in os.listdir(f"{input_dir}/miscellaneous/"):
            d = dict()
            d["name"] = file[:-10]
            d["layer_path"] = file
            d["layer_prefix"] = file[:-5]
            lst.append(d)
        provider_config.seek(0)
        data["Providers"]["RasterTiled"]["layers"] = lst

        Rasters = []
        Rastersm = []
        nodatam = []
        nodata = []
        cellLatSize = []
        cellLonSize = []
        paths = []

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/disturbances/")):
            for file in files:
                fp = os.path.join(root, file)
                Rasters.append(fp)
                paths.append(fp)

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/classifiers/")):
            for file in files:
                fp1 = os.path.join(root, file)
                Rasters.append(fp1)
                paths.append(fp1)

        for nd in Rasters:
            img = rst.open(nd)
            t = img.transform
            x = t[0]
            y = -t[4]
            n = img.nodata
            cellLatSize.append(x)
            cellLonSize.append(y)
            nodata.append(n)

        result = all(element == cellLatSize[0] for element in cellLatSize)
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

        provider_config.seek(0)

        data["Providers"]["RasterTiled"]["cellLonSize"] = cellLon
        data["Providers"]["RasterTiled"]["cellLatSize"] = cellLat
        data["Providers"]["RasterTiled"]["blockLonSize"] = blockLon
        data["Providers"]["RasterTiled"]["blockLatSize"] = blockLat
        data["Providers"]["RasterTiled"]["tileLatSize"] = tileLat
        data["Providers"]["RasterTiled"]["tileLonSize"] = tileLon

        json.dump(data, provider_config, indent=4)
        provider_config.truncate()

        dictionary = {
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

        # should be able to accept variable number of inputs, but requires
        # means for user to specify/verify correct ["attributes"]
        def get_input_layers():
            for root, dirs, files in os.walk(
                os.path.abspath(f"{input_dir}/miscellaneous/")
            ):
                for file in files:
                    fp2 = os.path.join(root, file)
                    Rastersm.append(fp2)

                for i in Rastersm:
                    img = rst.open(i)
                    d = img.nodata
                    nodatam.append(d)

            with open(
                f"{input_dir}/initial_age_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["layer_type"] = "GridLayer"
                dictionary["layer_data"] = "Int16"
                dictionary["nodata"] = nodatam[1]
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/mean_annual_temperature_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["layer_type"] = "GridLayer"
                dictionary["layer_data"] = "Float32"
                dictionary["nodata"] = nodatam[0]
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/Classifier1_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["layer_type"] = "GridLayer"
                dictionary["layer_data"] = "Byte"
                dictionary["nodata"] = nd
                dictionary["attributes"] = {
                    "1": "TA",
                    "2": "BP",
                    "3": "BS",
                    "4": "JP",
                    "5": "WS",
                    "6": "WB",
                    "7": "BF",
                    "8": "GA",
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/Classifier2_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["layer_type"] = "GridLayer"
                dictionary["layer_data"] = "Byte"
                dictionary["nodata"] = nd
                dictionary["attributes"] = {"1": "5", "2": "6", "3": "7", "4": "8"}
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2011_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["layer_data"] = "Byte"
                dictionary["nodata"] = nd
                dictionary["attributes"] = {
                    "1": {"year": 2011, "disturbance_type": "Wildfire", "transition": 1}
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2012_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {"year": 2012, "disturbance_type": "Wildfire", "transition": 1}
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2013_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {
                        "year": 2013,
                        "disturbance_type": "Mountain pine beetle — Very severe impact",
                        "transition": 1,
                    },
                    "2": {
                        "year": 2013,
                        "disturbance_type": "Wildfire",
                        "transition": 1,
                    },
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2014_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {
                        "year": 2014,
                        "disturbance_type": "Mountain pine beetle — Very severe impact",
                        "transition": 1,
                    }
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2015_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {"year": 2016, "disturbance_type": "Wildfire", "transition": 1}
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2016_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {"year": 2016, "disturbance_type": "Wildfire", "transition": 1}
                }
                json.dump(dictionary, json_file, indent=4)

            with open(
                f"{input_dir}/disturbances_2018_moja.json", "w", encoding="utf8"
            ) as json_file:
                dictionary["attributes"] = {
                    "1": {
                        "year": 2018,
                        "disturbance_type": "Mountain pine beetle — Low impact",
                        "transition": 1,
                    }
                }
                json.dump(dictionary, json_file, indent=4)

        get_input_layers()

        def get_study_area():
            study_area = {
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

            with open(f"{input_dir}/study_area.json", "w", encoding="utf") as json_file:
                list = []

                for file in os.listdir(f"{input_dir}/miscellaneous/"):
                    d1 = dict()
                    d1["name"] = file[:-10]
                    d1["type"] = "VectorLayer"
                    list.append(d1)
                study_area["layers"] = list

                for file in os.listdir(f"{input_dir}/classifiers/"):
                    d1 = dict()
                    d1["name"] = file[:-10]
                    d1["type"] = "VectorLayer"
                    d1["tags"] = ["classifier"]
                    list.append(d1)
                study_area["layers"] = list

                for file in os.listdir(f"{input_dir}/disturbances/"):
                    d1 = dict()
                    d1["name"] = file[:-10]
                    d1["type"] = "DisturbanceLayer"
                    d1["tags"] = ["disturbance"]
                    list.append(d1)
                study_area["layers"] = list

                json.dump(study_area, json_file, indent=4)

        get_study_area()

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/disturbances/")):
            for file in files:
                fp = os.path.join(root, file)
                Rasters.append(fp)
                paths.append(fp)

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/classifiers/")):
            for file in files:
                fp1 = os.path.join(root, file)
                Rasters.append(fp1)
                paths.append(fp1)

        for root, dirs, files in os.walk(
            os.path.abspath(f"{input_dir}/miscellaneous/")
        ):
            for file in files:
                fp2 = os.path.join(root, file)
                paths.append(fp2)

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/templates/")):
            for file in files:
                fp3 = os.path.join(root, file)
                paths.append(fp3)

        for root, dirs, files in os.walk(os.path.abspath(f"{input_dir}/db/")):
            for file in files:
                fp4 = os.path.join(root, file)
                paths.append(fp4)

            # copy files to input directory
            for i in paths:
                shutil.copy2(i, (f"{input_dir}"))

        # delete folders from input directory
        shutil.rmtree((f"{input_dir}/disturbances/"))
        shutil.rmtree((f"{input_dir}/templates/"))
        shutil.rmtree((f"{input_dir}/classifiers/"))
        shutil.rmtree((f"{input_dir}/miscellaneous/"))
        shutil.rmtree((f"{input_dir}/db/"))
