# This file tests the following GCBM simulations:
# 1. GCBM Belize with disturbances
# 2. GCBM Belize without disturbances
# 3. GCBM New Demo Run

import sys
sys.path.append("../")

import pytest

from gcbm import GCBMSimulation


belize_dict = {
    "classifiers": ["tiff/belize/LifeZone_moja.tiff"],
    "miscellaneous": ["tiff/belize/mean_annual_temperature_moja.tiff"],
}

new_demo_run_dict = {
    "disturbances": ["tiff/new_demo_run/disturbances_2011_moja.tiff", "tiff/new_demo_run/disturbances_2012_moja.tiff"],
    "classifiers": ["tiff/new_demo_run/Classifier1_moja.tiff"],
    "miscellaneous": ["tiff/new_demo_run/mean_annual_temperature_moja.tiff"],
}

def filter_input_dict(input_dict, if_disturbance):
    filtered_dict = input_dict
    if not if_disturbance:
        # Ignore disturbances from the dictionary
        filtered_dict = {k: v for k, v in input_dict.items() if k != "disturbances"}
    
    # Do sanity check on input dict
    def _sanity_check(dict):
        assert "classifiers" in list(dict.keys()) and "miscellaneous" in list(dict.keys()), f"classifiers and miscellaneous keys expected in the dict but got {dict.keys()} for simulation {simulation_name}"

    _sanity_check(filtered_dict)
    return filtered_dict


@pytest.mark.parametrize(
    "simulation_name, input_dict, if_disturbance",
    [
        ("belize", belize_dict, True),
        ("belize", belize_dict, False),
        ("new_demo_run", new_demo_run_dict, True),
        ("new_demo_run", new_demo_run_dict, False),
    ],
)
def test_simulation_add(simulation_name, input_dict, if_disturbance):
    import os

    filtered_dict = filter_input_dict(input_dict, if_disturbance)
    # Test that JSON files are generated for the configs of the simulation
    gcbm = GCBMSimulation()
    for key, val in filtered_dict.items():
        for path in val:
            gcbm.add_file(category=key, file_path=path)
            expected_path = "input/test-run/" + path.split("/")[-1]
            assert os.path.isfile(expected_path), f"Failed for {simulation_name}, expected {expected_path} to exist."


@pytest.mark.parametrize(
    "simulation_name, input_dict, if_disturbance",
    [
        ("belize", belize_dict, True),
        ("belize", belize_dict, False),
        ("new_demo_run", new_demo_run_dict, True),
        ("new_demo_run", new_demo_run_dict, False),
    ],
)
def test_simulation_set_attr(simulation_name, input_dict, if_disturbance):
    # Do sanity check on input dict
    def sanity_check(dict):
        assert "classifiers" in list(dict.keys()) and "miscellaneous" in list(dict.keys()), f"classifiers and miscellaneous keys expected in the dict but got {dict.keys()} for simulation {simulation_name}"

    # Assert if the json contains the expected data (payload)
    def check_data_in_json(json_path, expected_data):
        import json
        with open(json_path, "r") as json_file:
            json_obj = json.load(json_file)
            for key, val in expected_data.items():
                assert json_obj["attributes"][key] == val

    print(f"Starting test for simulation {simulation_name}")
    filtered_dict = input_dict
    if not if_disturbance:
        # Ignore disturbances from the dictionary
        filtered_dict = {k: v for k, v in input_dict.items() if k != "disturbances"}

    sanity_check(filtered_dict)

    # Test that JSON files are generated for the configs of the simulation
    import os
    sim = GCBMSimulation()
    for key, val in filtered_dict.items():
        for path in val:
            sim.add_file(category=key, file_path=path)
            payload = {"year": 2011, "disturbance_type": "Wildfire", "transition": 1}
            sim.set_attributes(category=key, file_path=path, payload=payload)
            check_data_in_json(json_path=sim.json_paths[os.path.basename(path)], expected_data=payload)
