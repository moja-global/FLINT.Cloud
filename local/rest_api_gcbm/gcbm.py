import os
import pathlib
import json

import rasterio


class GCBMList:
    """
    This is a base class for GCBM pre-processing scripts to use. It prevents users to do: <config>._append(<anything that is not a file>)
    """
    def __init__(self, files=dict(), config=[], category=None):
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
            raise NotImplementedError("Please implement `is_category` method, which is used by _append() method")
        else:
            return self.category in path

    # Unlike list.append() in Python, this returns a bool - whether the append was successful or not + checks if the file path is of the current category
    def _append(self, file_path):
        if self.is_category(file_path):
            self.data.append(file_path)
            return True
        return False

    def _update_config(self):
        for raster_file_path in self.data:
            json_config_file_path = GCBMList.change_extension(raster_file_path, ".json")

            if json_config_file_path.name not in self.config:
                self.generate_config(os.path.abspath(raster_file_path), json_config_file_path)
            else:
                with open(f"templates/config/{json_config_file_path.name}", "r+") as _file:
                    json.dump(self.files[os.path.abspath(raster_file_path)], _file, indent=4)

    def generate_config(self, file_path, json_config_file_path):
        mode = "w+"
        if os.path.exists(f"templates/config/{json_config_file_path}"):
            mode = "r+"

        with open(f"templates/config/{json_config_file_path.name}", mode) as _file:
            if mode == "r+":
                config = json.load(_file)
            else:
                config = dict()
            with rasterio.open(file_path) as disturbance:
                tr = disturbance.transform
                config["cellLatSize"] = tr[0]
                config["cellLonSize"] = -tr[4]
                config["nodata"] = disturbance.nodata

            config["blockLonSize"] = config["cellLonSize"] * 400
            config["blockLatSize"] = config["cellLatSize"] * 400
            config["tileLatSize"] = config["cellLatSize"] * 4000
            config["tileLonSize"] = config["cellLonSize"] * 4000
            config["layer_type"] = "GridLayer"
            config["layer_data"] = "Byte"
            config["has_year"] = False
            config["has_type"] = False

            json.dump(config, _file, indent=4)

            self.files[file_path] = config
            self.config.append(json_config_file_path.name)

        # TODO:
        # self.sync_config()

    def setattr(self, file, attributes):
        file = os.path.abspath(file)
        config = self.files[file]
        config["attributes"] = attributes

        if (config["attributes"]["year"]):
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
        self.files = files
        self.config = config
        super().__init__(files=files, config=config, category=category)


class GCBMClassifiersList(GCBMList):
    def __init__(self, files, config):
        category = "classifiers"
        self.files = files
        self.config = config
        super().__init__(category=category)


class GCBMMiscellaneousList(GCBMList):
    def __init__(self, files, config):
        category = "miscellaneous"
        self.files = files
        self.config = config
        super().__init__(category=category)


class GCBMSimulation:
    def __init__(self):
        # create a global index
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
        if not os.path.exists("templates/config"):
            os.makedirs("templates/config/")

    def create_file_index(self):
        config_dir_path = "templates/config"
        assert os.path.isdir(config_dir_path), f"Given config directory path: {config_dir_path} either does not exist or is not a directory."
        for dirpath, _, filenames in os.walk(config_dir_path):
            for filename in filenames:
                # Don't read any data, but create the json file
                abs_filepath = os.path.abspath(os.path.join(dirpath, filename))

                data = GCBMSimulation.safe_read_json(abs_filepath)

                # TODO: Discussion - should this be abs_filepath, or do we want just the filename?
                self.files[abs_filepath] = data

                # TODO: This should not happen here? maybe connect an endpoint directly to the sync_config method
                # self.sync_config(abs_filepath)

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
        if self.disturbances._append(file_path):
            self.disturbances._update_config()
            return
        if self.classifiers._append(file_path):
            self.classifiers._update_config()
            return
        if self.miscellaneous._append(file_path):
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
        if ".json" not in path:
            raise UserWarning(f"Given path {path} not a json file")
            return {}
        # Make sure it's a file and not a directory
        if not os.path.isfile(path):
            raise UserWarning(f"Got a directory {path} inside the config directory path, skipping it.")
            return {}
        with open(path, 'r') as json_file:
            data = json.load(json_file)
        return data


if __name__ == "__main__":
    sim = GCBMSimulation()
    sim.add_file("disturbances/disturbances_2011_moja.tiff")
    sim.add_file("classifiers/classifier1_moja.tiff")
    sim.add_file("miscellaneous/initial_age_moja.tiff")
    # this^ generates disturbances_2011_moja.json file, which will contain the metadata from .tiff

    # Sample payload to test
    # If you want to add something of your own to the json file above, you can do this:
    payload = {
        "year": 2012,
        "disturbance_type": "Wildfire",
        "random_thing": [1,2,3,4],
        "transition": 1
    }
    sim.set_disturbance_attributes("disturbances/disturbances_2011_moja.tiff", payload)
    sim.set_classifier_attributes("classifiers/classifier1_moja.tiff", payload)
    sim.set_miscellaneous_attributes("miscellaneous/initial_age_moja.tiff", payload)