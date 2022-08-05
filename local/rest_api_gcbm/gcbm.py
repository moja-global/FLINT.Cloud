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

    def _append(self, file_path, check=True):
        # Unlike list.append() in Python, this returns a bool - whether the append was successful or not + checks if the file path is of the current category
        if check:
            if self.is_category(file_path):
                self.data.append(file_path)
                return True
            return False
        else:
            self.data.append(file_path)
            return True

    def _update_config(self):
        json_paths = {}
        for file in self.data:
            json_config_file = GCBMList.change_extension(file, ".json")
            json_filepath = os.path.join(self.dirpath, json_config_file)

            if json_config_file.name not in self.config:
                self.generate_config(file, json_config_file)
            else:
                # TODO: This is not required I guess
                with open(json_filepath, "w+") as _config:
                    json.dump(
                        self.files[file], _config, indent=4
                    )
            json_paths[file] = json_filepath 
        return json_paths

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
        # if os.path.exists(json_filepath):
        #     mode = "w+"

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
        # Output paths are returned to keep track
        json_paths = self._update_config()
        return json_paths

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
        self.config_dir_path = "templates"
        self.files = {}
        
        # Tracks the output path for the input received through `add_file` method
        self.json_paths = {}

        # TODO: Once categories are changed from strings to Enums, we should find a better way to have supported categories
        self.supported_categories = ["classifiers", "disturbances", "miscellaneous"]

        # create sub-indices of different types
        self.config = list()
        self.parameters = []  # this is the input_db

        self.create_simulation_folder()
        self.create_file_index()

        self.classifiers = GCBMClassifiersList(files=self.files, config=self.config)
        self.disturbances = GCBMDisturbanceList(files=self.files, config=self.config)
        self.miscellaneous = GCBMMiscellaneousList(files=self.files, config=self.config)

    def create_simulation_folder(self):
        for dir_path in [self.dirpath, self.config_dir_path]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)


    def create_file_index(self):
        assert os.path.isdir(
            self.config_dir_path
        ), f"Given config directory path: {self.config_dir_path} either does not exist or is not a directory."
        for dirpath, _, filenames in os.walk(self.config_dir_path):
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
    def add_file(self, file_path: str, category: str = ""):
        """
        This function:

            1. Checks if the given file is one of the categories: registers, classifiers, and miscellaneous.
            2. The provided file path to the buffer, and updates the config (JSON).

        Parameters
        ==========
        1. file_path (str), no default
        2. category (str), default = "", if skipped - then the categories will be deduced from the file path 
        """

        # TODO: update to accept input from Flask endpoint
        # FIXME: The flask end point should do the pre-processing to be able to only pass the `file_path` as a string
        # TODO: update in app.py to send valid data to add_file
        filename = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(self.dirpath, filename))

        def _disturbance(filename, check=True):
            if self.disturbances._append(filename, check):
                self.disturbances._update_config()
                
        def _classifier(filename, check=True):
            if self.classifiers._append(filename, check):
                self.classifiers._update_config()

        def _miscellaneous(filename, check=True):
            if self.miscellaneous._append(filename, check):
                self.miscellaneous._update_config()

        if category != "":
            if category == "disturbances":
                _disturbance(filename, check=False)
            elif category == "classifiers":
                _classifier(filename, check=False)
            elif category == "miscellaneous":
                _miscellaneous(filename, check=False)
            else:
                # We can also raise an error here
                raise UserWarning(f"Given category {category} not supported, supported categories are: {disturbances, classifiers, miscellaneous}")
        else:
            print(f"Category wasn't provided, attempting to deduce it from the file path: {file_path}")
            if self.disturbances._append(filename):
                self.disturbances._update_config()
                return
            if self.classifiers._append(filename):
                self.classifiers._update_config()
                return
            if self.miscellaneous._append(filename):
                self.miscellaneous._update_config()
                return 
            print(f"Couldn't deduce a valid from the file path {file_path}, supported categories: {self.supported_categories}")


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
        self.json_paths.update(self.disturbances._update_config())


    def set_disturbance_attributes(self, file_path, payload):
        self.json_paths.update(self.disturbances.setattr(file_path, payload))


    def update_classifier_config(self):
        self.json_paths.update(self.classifiers._update_config())


    def set_classifier_attributes(self, file_path, payload):
        self.json_paths.update(self.classifiers.setattr(file_path, payload))


    def update_miscellaneous_config(self):
        self.json_paths.update(self.miscellaneous._update_config())


    def set_miscellaneous_attributes(self, file_path, payload):
        self.json_paths.update(self.miscellaneous.setattr(file_path, payload))


    # TODO: category should be an enum instead of a string to avoid any mistakes
    def set_attributes(self, category: str, file_path: str, payload: dict):
        base_path = os.path.basename(file_path)
        if category == "disturbances":
            self.set_disturbance_attributes(base_path, payload)
        elif category == "classifiers":
            self.set_classifier_attributes(base_path, payload)
        elif category == "miscellaneous":
            self.set_miscellaneous_attributes(base_path, payload)
        else:
            raise UserWarning(f"Expected a valid category name out of {self.supported_categories}, but got {category}")


    @staticmethod
    def safe_read_json(file_path):

        # TODO: add read method for gcbm_config.cfg and logging.conf
        if ".cfg" in file_path:
            filename = os.path.join('input/test-run', "gcbm_config.cfg")
            shutil.copy(file_path, filename)
            return {}

        if ".conf" in file_path:
            filename = os.path.join('input/test-run', "logging.conf")
            shutil.copy(file_path, filename)
            return {}

        # check JSON
        if ".json" not in file_path:
            raise UserWarning(f"Given path {file_path} not a valid json file")

        # Make sure it's a file and not a directory
        if not os.path.isfile(file_path):
            raise UserWarning(
                f"Got a directory {file_path} inside the config directory path, skipping it."
            )
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data


if __name__ == "__main__":
    sim = GCBMSimulation()
    sim.add_file("tests/tiff/new_demo_run/disturbances_2011_moja.tiff")
    # sim.set_disturbance_attributes("disturbances_2011_moja.tiff", {"year": 2011, "disturbance_type": "Wildfire", "transition": 1})
    sim.set_attributes(category="disturbances", file_path="disturbances_2011_moja.tiff", payload={"year": 2011, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/tiff/new_demo_run/disturbances_2012_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2012_moja.tiff",
                                  {"year": 2012, "disturbance_type": "Wildfire", "transition": 1})


    sim.add_file("tests/tiff/new_demo_run/disturbances_2013_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2013_moja.tiff",
                                    {"year": 2013, "disturbance_type": "Mountain pine beetle — Very severe impact", "transition": 1})

    # TODO: Check how to handle multiple attributes entries (L442-451 of `app.py:master`)
    # sim.set_disturbance_attributes("disturbances_2013_moja.tiff",
    #                                 {"year": 2013, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/tiff/new_demo_run/disturbances_2014_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2014_moja.tiff",
                                    {"year": 2014, "disturbance_type": "Mountain pine beetle — Very severe impact", "transition": 1})

    sim.add_file("tests/tiff/new_demo_run/disturbances_2015_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2015_moja.tiff",
                                    {"year": 2015, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/tiff/new_demo_run/disturbances_2016_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2016_moja.tiff",
                                   {"year": 2016, "disturbance_type": "Wildfire", "transition": 1})

    sim.add_file("tests/tiff/new_demo_run/disturbances_2018_moja.tiff")
    sim.set_disturbance_attributes("disturbances_2018_moja.tiff",
                                    {"year": 2018, "disturbance_type": "Wildfire", "transition": 1})

    # TODO: classifiers don't have 'year' attributes
    sim.add_file("tests/tiff/new_demo_run/Classifier1_moja.tiff", category="classifiers")
    # sim.set_classifier_attributes("Classifier1_moja.tiff",
    #                               {"1": "TA", "2": "BP", "3": "BS", "4": "JP", "5": "WS", "6": "WB", "7": "BF", "8": "GA"})

    sim.add_file("tests/tiff/new_demo_run/Classifier2_moja.tiff", category="classifiers")
    # sim.set_classifier_attributes("Classifier2_moja.tiff",
    #                              {"1": "5", "2": "6", "3": "7", "4": "8"})

    sim.add_file("tests/tiff/new_demo_run/initial_age_moja.tiff", category="miscellaneous")
    sim.add_file("tests/tiff/new_demo_run/mean_annual_temperature_moja.tiff", category="miscellaneous")

    # TODO: make it work
    # sim.add_file("tests/reference/gcbm_new_demo_run/gcbm_input.db")
