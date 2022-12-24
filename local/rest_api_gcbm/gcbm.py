from typing import Dict, Any

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
                    json.dump(self.files[file], _config, indent=4)
            json_paths[file] = json_filepath
        return json_paths

    def generate_config(self, file, json_config_file):
        filepath = os.path.join(self.dirpath, file)
        json_filepath = os.path.join(self.dirpath, json_config_file)

        mode = "w+"

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
                    # TODO: Should we add these if year/type aren't provided in attributes?
                    # config["has_year"] = False
                    # config["has_type"] = False

                    json.dump(config, _file, indent=4)

                    self.files[file] = config
                    self.config.append(json_config_file.name)

    @staticmethod
    def _search_in_attributes(input_dict: Dict[str, Any], to_find: str):
        for key, val in input_dict.items():
            if key == to_find:
                return val
            if isinstance(val, dict):
                return GCBMList._search_in_attributes(val, to_find)
        return None

    def setattr(self, file, attributes, category):
        config = self.files[file]
        config["attributes"] = attributes

        for key, output_key in zip(
            ["year", f"{category}_type"], ["has_year", "has_type"]
        ):
            val = GCBMList._search_in_attributes(attributes, key)
            if val:
                config[output_key] = True

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
        category = "disturbance"
        self.dirpath = "input/test-run"
        self.files = files
        self.config = config
        super().__init__(files=files, config=config, category=category)


class GCBMclassifierList(GCBMList):
    def __init__(self, files, config):
        self.dirpath = "input/test-run"
        category = "classifier"
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


class GCBMDatabase:
    def __init__(self):
        self.files = []
        self.config = [{"SQLite": {}}]

    def _append(self, file_path, check=True):
        if check:
            if ".db" in file_path:
                self.files.append(file_path)
                return True
            else:
                return False
        else:
            self.files.append(file_path)
            return True

    def _update_config(self):
        for idx, _ in enumerate(self.config):
            self.config[idx]["SQLite"] = {"path": self.files[idx], "type": "SQLite"}


class GCBMSimulation:
    def __init__(self):
        # create a global index
        self.dirpath = "input/test-run"
        self.config_dir_path = "templates"
        self.files = {}

        # Tracks the output path for the input received through `add_file` method
        self.json_paths = {}

        # TODO: Once categories are changed from strings to Enums, we should find a better way to have supported categories
        self.supported_categories = ["classifier", "disturbance", "miscellaneous", "db"]

        # create sub-indices of different types
        self.config = list()
        self.parameters = []  # this is the input_db

        self.create_simulation_folder()
        self.create_file_index()

        self.classifier = GCBMclassifierList(files={}, config=self.config)
        self.disturbance = GCBMDisturbanceList(files={}, config=self.config)
        self.miscellaneous = GCBMMiscellaneousList(files={}, config=self.config)
        self.db = GCBMDatabase()

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

    def _insert_sql_data(self):
        data = {}
        # Question to Andrew: there will always be one database file that will be uploaded, right?
        # in the app.py, L266, we loop through {input_dir}/db/ folder, and keep overwriting the data["Providers"]["SQLite"]
        # so only one file's data is stored (that is the last one from os.listdir)
        for file_path in self.db.files:
            data["path"] = os.path.abspath(file_path)
            data["type"] = "SQLite"
        return data

    def _insert_categories_data(self):
        data = []
        for category in self.supported_categories:
            # We have handled SQL in _insert_sql_data()
            if category == "db":
                continue
            for file_path in getattr(self, category).data:
                dict_category = {}
                dict_category["name"] = file_path.strip(".tiff")
                dict_category["layer_path"] = os.path.abspath(file_path)
                # Question to Andrew: since  suffix is gone for the file paths, this (layer_prefix) is not required, right?
                dict_category["layer_prefix"] = dict_category["name"]
                data.append(dict_category)
        return data

    def _fill_sizes(self, data, keys):
        # TODO: We need to assert that all files have the same data... @ankitaS11
        visited = {x: False for x in keys}
        for key in keys:
            if visited[key]:
                continue
            for val in self.classifier.files.values():
                if key in val:
                    data["Providers"]["RasterTiled"][key] = val[key]
                    visited[key] = True
        return data

    def _generate_provider_config(self, dirpath: str):
        with open(f"{dirpath}/provider_config.json", "r+") as provider_config:
            data = json.load(provider_config)

            provider_config.seek(0)
            data["Providers"]["SQLite"] = self._insert_sql_data()
            data["Providers"]["RasterTiled"]["layers"] = self._insert_categories_data()
            self._fill_sizes(data, ["cellLonSize", "cellLatSize", "blockLonSize", "blockLatSize", "tileLatSize", "tileLonSize"])

            json.dump(data, provider_config, indent=4)

    def _generate_modules_cbm_config(self, dirpath: str):
        with open(f"{dirpath}/modules_cbm.json", "r+") as modules_cbm_config:
            data = json.load(modules_cbm_config)
            modules_cbm_config.seek(0)
            data["Modules"]["CBMDisturbanceListener"]["settings"]["vars"] = [os.path.splitext(path)[0] for path in self.disturbance.data]
            json.dump(data, modules_cbm_config, indent=4)

    def _add_variables(self, dirpath: str):
        with open(f"{dirpath}/variables.json", "r+") as variables_config:
            data = json.load(variables_config)
            variables_config.seek(0)
            for category in self.supported_categories:
                if category == "db":
                    continue
                for path in getattr(self, category).data:
                    name = os.path.splitext(path)[0]
                    data["Variables"][name] = {
                        "transform": {
                            "library": "internal.flint",
                            "type": "LocationIdxFromFlintDataTransform",
                            "provider": "RasterTiled",
                            "data_id": name
                        }
                    }
            json.dump(data, variables_config, indent=4)

    # file_path: disturbance (NOT MUST), classifier (MUST), miscellaneous (MUST)
    def add_file(self, file_path: str, category: str = ""):
        """
        This function:

            1. Checks if the given file is one of the categories: registers, classifier, and miscellaneous.
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
            if self.disturbance._append(filename, check):
                self.json_paths.update(self.disturbance._update_config())

        def _classifier(filename, check=True):
            if self.classifier._append(filename, check):
                self.json_paths.update(self.classifier._update_config())

        def _miscellaneous(filename, check=True):
            if self.miscellaneous._append(filename, check):
                self.json_paths.update(self.miscellaneous._update_config())

        def _db(filename, check=True):
            if self.db._append(filename, check):
                # This just stores, and doesn't write anything yet...
                self.db._update_config()

        if category != "":
            if category == "disturbance":
                _disturbance(filename, check=False)
            elif category == "classifier":
                print("Found it here: ", filename)
                _classifier(filename, check=False)
            elif category == "miscellaneous":
                _miscellaneous(filename, check=False)
            elif category == "db":
                _db(filename, check=False)
            else:
                raise ValueError(
                    f"Given category {category} not supported, supported categories are: {self.supported_categories}"
                )
        else:
            deduced_category = ""
            if self.disturbance._append(filename):
                self.json_paths.update(self.disturbance._update_config())
                deduced_category = "disturbance"
            elif self.classifier._append(filename):
                self.json_paths.update(self.classifier._update_config())
                deduced_category = "classifier"
            elif self.miscellaneous._append(filename):
                self.json_paths.update(self.miscellaneous._update_config())
                deduced_category = "miscellaneous"
            elif self.db._append(filename):
                self.db._update_config()
                deduced_category = "db"
            else:
                raise ValueError(
                    f"Couldn't deduce a valid from the file path {file_path}, supported categories: {self.supported_categories}"
                )
            print(
                    f"Category wasn't provided, deduced category: {deduced_category} it from the file path: {file_path}"
            )

    def generate_configs(self):
        self._generate_provider_config(self.dirpath)
        self._generate_modules_cbm_config(self.dirpath)
        self._add_variables(self.dirpath)

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
        self.json_paths.update(self.disturbance._update_config())

    def update_classifier_config(self):
        self.json_paths.update(self.classifier._update_config())

    def update_miscellaneous_config(self):
        self.json_paths.update(self.miscellaneous._update_config())

    # TODO: category should be an enum instead of a string to avoid any mistakes
    def set_attributes(self, category: str, file_path: str, payload: dict):
        base_path = os.path.basename(file_path)
        if category == "disturbance":
            self.disturbance.setattr(
                file=base_path, attributes=payload, category=category
            )
        elif category == "classifier":
            self.classifier.setattr(
                file=base_path, attributes=payload, category=category
            )
        elif category == "miscellaneous":
            self.miscellaneous.setattr(
                file=base_path, attributes=payload, category=category
            )
        else:
            raise ValueError(
                f"Expected a valid category name out of {self.supported_categories}, but got {category}. Note that setting attributes for a database file is not supported."
            )

    @staticmethod
    def safe_read_json(file_path):

        # TODO: add read method for gcbm_config.cfg and logging.conf
        if ".cfg" in file_path:
            filename = os.path.join("input/test-run", "gcbm_config.cfg")
            shutil.copy(file_path, filename)
            return {}

        if ".conf" in file_path:
            filename = os.path.join("input/test-run", "logging.conf")
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
    sim.add_file(
        "tests/reference/test_data/new_demo_run/disturbances_2011.tiff", category="disturbance"
    )
    # sim.set_attributes("disturbances_2011.tiff", {"year": 2011, "disturbance_type": "Wildfire", "transition": 1})
    sim.set_attributes(
        category="disturbance",
        file_path="disturbances_2011.tiff",
        payload={"year": 2011, "disturbance_type": "Wildfire", "transition": 1},
    )

    sim.add_file(
        "tests/reference/test_data/new_demo_run/disturbances_2012.tiff", category="disturbance"
    )
    sim.set_attributes(
        file_path="disturbances_2012.tiff",
        category="disturbance",
        payload={"year": 2012, "disturbance_type": "Wildfire", "transition": 1},
    )

    sim.add_file("tests/reference/test_data/new_demo_run/disturbances_2013.tiff")
    # sim.set_attributes(
    #     file_path="disturbances_2013.tiff",
    #     category="disturbance",
    #     payload={
    #         "year": 2013,
    #         "disturbance_type": "Mountain pine beetle — Very severe impact",
    #         "transition": 1,
    #     },
    # )

    # TODO: Check how to handle multiple attributes entries (L442-451 of `app.py:master`)
    sim.set_attributes(
        file_path="disturbances_2013.tiff",
        category="disturbance",
        payload={
            "1": {
                "year": 2013,
                "disturbance_type": "Mountain pine beetle — Very severe impact",
                "transition": 1,
            },
            "2": {"year": 2013, "disturbance_type": "Wildfire", "transition": 1},
        },
    )

    sim.add_file("tests/reference/test_data/new_demo_run/disturbances_2014.tiff")
    sim.set_attributes(
        file_path="disturbances_2014.tiff",
        category="disturbance",
        payload={
            "year": 2014,
            "disturbance_type": "Mountain pine beetle — Very severe impact",
            "transition": 1,
        },
    )

    sim.add_file("tests/reference/test_data/new_demo_run/disturbances_2015.tiff")
    sim.set_attributes(
        file_path="disturbances_2015.tiff",
        category="disturbance",
        payload={"year": 2015, "disturbance_type": "Wildfire", "transition": 1},
    )

    sim.add_file("tests/reference/test_data/new_demo_run/disturbances_2016.tiff")
    sim.set_attributes(
        file_path="disturbances_2016.tiff",
        category="disturbance",
        payload={"year": 2016, "disturbance_type": "Wildfire", "transition": 1},
    )

    sim.add_file("tests/reference/test_data/new_demo_run/disturbances_2018.tiff")
    sim.set_attributes(
        file_path="disturbances_2018.tiff",
        category="disturbance",
        payload={"year": 2018, "disturbance_type": "Wildfire", "transition": 1},
    )

    # TODO: classifier don't have 'year' attributes
    sim.add_file("tests/reference/test_data/new_demo_run/Classifier1.tiff", category="classifier")
    sim.set_attributes(
        file_path="Classifier1.tiff",
        category="classifier",
        payload={
            "1": "TA",
            "2": "BP",
            "3": "BS",
            "4": "JP",
            "5": "WS",
            "6": "WB",
            "7": "BF",
            "8": "GA",
        },
    )

    sim.add_file("tests/reference/test_data/new_demo_run/Classifier2.tiff", category="classifier")
    sim.set_attributes(
        file_path="Classifier2.tiff",
        category="classifier",
        payload={"1": "5", "2": "6", "3": "7", "4": "8"},
    )

    sim.add_file(
        "tests/reference/test_data/new_demo_run/initial_age.tiff", category="miscellaneous"
    )
    sim.add_file(
        "tests/reference/test_data/new_demo_run/mean_annual_temperature.tiff",
        category="miscellaneous",
    )

    # TODO: make it work
    sim.add_file("tests/reference/test_data/new_demo_run/gcbm_input.db")
    sim.generate_configs()
