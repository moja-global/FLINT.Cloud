import os
import shutil
import pathlib
import json

import rasterio


class GCBMList:
    """
    This is a base class for GCBM pre-processing scripts to use. It prevents users to do: <config>._append(<anything that is not a file>)
    """

    def __init__(self, files=dict(), config=[], category=None):
        # TODO: set simulation folder as global
        self.dirpath = "input/test-run"
        self.data = list()
        self.files = files
        self.config = config
        self.category = category

    def __iter__(self):
        return self.data

    def __getitem__(self, idx):
        return self.data[idx]

    def is_category(self, path):
        if self.category is None:
            raise NotImplementedError(
                "Please implement `is_category` method, which is used by _append() method"
            )
        else:
            return self.category in path

    # Unlike list.append() in Python, this returns a bool - whether the append was successful or not + checks if the file path is of the current category
    def _append(self, file_path):
        if self.is_category(file_path):
            self.data.append(file_path)
            return True
        return False

    def _update_config(self):
        for file in self.data:
            json_config_file = GCBMList.change_extension(file, ".json")
            json_filepath = os.path.join(self.dirpath, json_config_file)

            if json_config_file.name not in self.config:
                self.generate_config(file, json_config_file)
            else:
                with open(json_filepath, "r+") as _config:
                    json.dump(
                        self.files[file], _config, indent=4
                    )

    def _populate_config_with_hard_coded_config(
        self, config, hc_config, nodata
    ):
        # Note: hc_config => hard_coded_config
        for key in hc_config.keys():
            if key.startswith("_"):
                # the format is: _<key>_<obj>: <index> (index is useless here, TODO: remove it)
                original_key = key.split("_")[1]
                if hc_config[key] is None:
                    continue
                else:
                    config[original_key] = nodata
            else:
                config[key] = hc_config[key]
        return config

    def generate_config(self, file, json_config_file):
        filepath = os.path.join(self.dirpath, file)
        json_filepath = os.path.join(self.dirpath, json_config_file)

        mode = "w+"
        if os.path.exists(json_filepath):
            mode = "r+"

        # AO: disabling in favour of user defined attributes
        # hard_coded_path = f"hard_coded_values/{json_config_file}"
        # hard_coded_config = None
        # if os.path.exists(hard_coded_path):
        #     with open(hard_coded_path) as hard_coded_file:
        #         try:
        #             hard_coded_config = json.load(hard_coded_file)
        #         except json.decoder.JSONDecodeError as e:
        #             raise e

        with open(json_filepath, mode) as _file:
            if mode == "r+":
                config = json.load(_file)
            else:
                config = dict()

            # Defaults
            if ".tiff" in file:
                with rasterio.open(filepath) as raster_obj:
                    tr = raster_obj.transform
                    config["cellLatSize"] = tr[0]
                    config["cellLonSize"] = -tr[4]
                    config["nodata"] = raster_obj.nodata

                    config["blockLonSize"] = config["cellLonSize"] * 400
                    config["blockLatSize"] = config["cellLatSize"] * 400
                    config["tileLatSize"] = config["cellLatSize"] * 4000
                    config["tileLonSize"] = config["cellLonSize"] * 4000
                    config["layer_type"] = "GridLayer"
                    config["layer_data"] = "Byte"
                    # config["has_year"] = False
                    # config["has_type"] = False


                    # Now populate if hard_coded_config exists
                    # config = self._populate_config_with_hard_coded_config(
                    #     config, hard_coded_config, raster_obj.nodata
                    # )

                    print("Dumping config: ", config)
                    json.dump(config, _file, indent=4)

                    print(file)
                    self.files[file] = config
                    self.config.append(json_config_file.name)

        # AO: I think this has been replaced with _update_config
        # self.sync_config()

    def setattr(self, file, attributes):
        config = self.files[file]
        config["attributes"] = attributes

        if config["attributes"]["year"]:
            config["has_year"] = True

        self.files[file] = config
        self._update_config()

    @staticmethod
    def change_extension(file_path, new_extension):
        # TODO: let's use pathlib.Path everywhere, for now it's okay here
        pathlib_path = pathlib.Path(file_path)
        return pathlib_path.with_suffix(new_extension)


class GCBMDisturbanceList(GCBMList):
    def __init__(self, files, config):
        category = "disturbances"
        self.dirpath = "input/test-run"
        self.files = files
        self.config = config
        super().__init__(files=files, config=config, category=category)


class GCBMClassifiersList(GCBMList):
    def __init__(self, files, config):
        self.dirpath = "input/test-run"
        category = "classifiers"
        self.files = files
        self.config = config
        super().__init__(category=category)


class GCBMMiscellaneousList(GCBMList):
    def __init__(self, files, config):
        self.dirpath = "input/test-run"
        category = "miscellaneous"
        self.files = files
        self.config = config
        super().__init__(category=category)


class GCBMSimulation:
    def __init__(self):
        # create a global index
        self.dirpath = "input/test-run"
        self.files = {}

        # create sub-indices of different types
        self.config = list()
        self.parameters = []  # this is the input_db

        self.create_simulation_folder()
        self.create_file_index()

        self.classifiers = GCBMClassifiersList(files=self.files, config=self.config)
        self.disturbances = GCBMDisturbanceList(files=self.files, config=self.config)
        self.miscellaneous = GCBMMiscellaneousList(files=self.files, config=self.config)

    def create_simulation_folder(self):
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)


    def create_file_index(self):
        config_dir_path = "templates"
        assert os.path.isdir(
            config_dir_path
        ), f"Given config directory path: {config_dir_path} either does not exist or is not a directory."
        for dirpath, _, filenames in os.walk(config_dir_path):
            for filename in filenames:
                # Don't read any data, but create the json file
                abs_filepath = os.path.abspath(os.path.join(dirpath, filename))

                data = GCBMSimulation.safe_read_json(abs_filepath)

                # TODO: Discussion - should this be abs_filepath, or do we want just the filename?
                self.files[filename] = data

                # TODO: This should not happen here? maybe connect an endpoint directly to the sync_config method
                # self.sync_config(abs_filepath)

                # AO: sync_config is a write method, saving the current config
                # state file - doing dumb copy until implemented.
                sim_filepath = os.path.join(self.dirpath, filename)
                shutil.copy(abs_filepath, sim_filepath)

    # file_path: disturbances (NOT MUST), classifiers (MUST), miscellaneous (MUST)
    def add_file(self, file_path: str):
        """
        This function:

            1. Checks if the given file is one of the categories: registers, classifiers, and miscellaneous.
            2. The provided file path to the buffer, and updates the config (JSON).

        Parameters
        ==========
        1. file_path (str), no default
        """

        # TODO: update to accept input from Flask endpoint
        filename = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(self.dirpath, filename))

        if self.disturbances._append(filename):
            self.disturbances._update_config()
            return
        if self.classifiers._append(filename):
            self.classifiers._update_config()
            return
        if self.miscellaneous._append(filename):
            self.miscellaneous._update_config()
            return
        # TODO: Add covariates here

        # TODO
        # self._save(file_path)

    def sync_config(self, file_path):
        def _write_to_file(file_path, data):
            with open(file_path, "w+") as _file:
                _file.write(data)

        data = GCBMSimulation.safe_read_json(file_path)

        if self.files[file_path] != data:
            # Means data has changed, so update the file_path
            _write_to_file(file_path, data)
            # Also update the dict
            self.files[file_path] = data

    # TODO (@ankitaS11): We can just have these as class methods later, this will reduce the redundancy in the code later
    def update_disturbance_config(self):
        self.disturbances._update_config()

    def set_disturbance_attributes(self, file, payload):
        self.disturbances.setattr(file, payload)

    def update_classifier_config(self):
        self.classifiers._update_config()

    def set_classifier_attributes(self, file, payload):
        self.classifiers.setattr(file, payload)

    def update_miscellaneous_config(self):
        self.miscellaneous._update_config()

    def set_miscellaneous_attributes(self, file, payload):
        self.miscellaneous.setattr(file, payload)

    @staticmethod
    def safe_read_json(path):

        # TODO: add read method for gcbm_config.cfg and logging.conf
        if ".cfg" in path:
            filename = os.path.join('input/test-run', "gcbm_config.cfg")
            shutil.copy(path, filename)
            return {}
        if ".conf" in path:
            filename = os.path.join('input/test-run', "logging.conf")
            shutil.copy(path, filename)
            return {}

        # check JSON
        if ".json" not in path:
            raise UserWarning(f"Given path {path} not a valid json file")
            return {}

        # Make sure it's a file and not a directory
        if not os.path.isfile(path):
            raise UserWarning(
                f"Got a directory {path} inside the config directory path, skipping it."
            )
            return {}
        with open(path, "r") as json_file:
            data = json.load(json_file)
        return data


if __name__ == "__main__":
    sim = GCBMSimulation()
    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2011.tiff")
    sim.set_disturbance_attributes("disturbances_2011.tiff", {"year": 2011, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2012.tiff")
    sim.set_disturbance_attributes("disturbances_2012.tiff",
                                  {"year": 2012, "disturbance_type": "Wildfire", "transition": 1})


    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2013.tiff")
    sim.set_disturbance_attributes("disturbances_2013.tiff",
                                    {"year": 2013, "disturbance_type": "Mountain pine beetle — Very severe impact", "transition": 1})

    # TODO: Check how to handle multiple attributes entries (L442-451 of `app.py:master`)
    # sim.set_disturbance_attributes("disturbances_2013.tiff",
    #                                 {"year": 2013, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2014.tiff")
    sim.set_disturbance_attributes("disturbances_2014.tiff",
                                    {"year": 2014, "disturbance_type": "Mountain pine beetle — Very severe impact", "transition": 1})

    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2015.tiff")
    sim.set_disturbance_attributes("disturbances_2015.tiff",
                                    {"year": 2015, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2016.tiff")
    sim.set_disturbance_attributes("disturbances_2016.tiff",
                                   {"year": 2016, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/GCBM_New_Demo_Run/disturbances/disturbances_2018.tiff")
    sim.set_disturbance_attributes("disturbances_2018.tiff",
                                    {"year": 2018, "disturbance_type": "Wildfire", "transition": 1})

    # TODO: classifiers don't have 'year' attributes
    sim.add_file("tests/GCBM_New_Demo_Run/classifiers/Classifier1.tiff")
    # sim.set_classifier_attributes("classifier1.tiff",
    #                               {"1": "TA", "2": "BP", "3": "BS", "4": "JP", "5": "WS", "6": "WB", "7": "BF", "8": "GA"})

    sim.add_file("tests/GCBM_New_Demo_Run/classifiers/Classifier2.tiff")
    # sim.set_classifier_attributes("classifier1.tiff",
    #                              {"1": "5", "2": "6", "3": "7", "4": "8"})

    sim.add_file("tests/GCBM_New_Demo_Run/db/gcbm_input.db")
    sim.add_file("tests/GCBM_New_Demo_Run/miscellaneous/initial_age.tiff")
    sim.add_file("tests/GCBM_New_Demo_Run/miscellaneous/mean_annual_temperature.tiff")
