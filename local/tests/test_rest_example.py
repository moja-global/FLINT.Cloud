import pytest
import requests
import json
import os
from pathlib import Path


class TestApiFlintExample:

    # this fixture is used to pass the base_endpoint to the other functions
    @pytest.fixture
    def base_endpoint(self):
        """ Port 8080 of the docker container is mapped to 8080 on the \
        ubuntu machine running the action, api testing is performed at port 8080"""
        self.ENDPOINT = "http://localhost:8080/"
        yield self.ENDPOINT

    def test_spec(self, base_endpoint):
        spec_endpoint = base_endpoint + "spec"
        spec_response = requests.get(spec_endpoint)
        assert spec_response.status_code == 200

    def test_version(self, base_endpoint):
        version_endpoint = base_endpoint + "version"
        version_response = requests.get(version_endpoint)
        assert version_response.status_code == 200

    def test_help_all(self, base_endpoint):
        """This test is to check the help endpoint with all argument"""
        help_all_endpoint = base_endpoint + "help/all"
        help_all_response = requests.get(help_all_endpoint)
        assert help_all_response.status_code == 200

    def test_help_arg(self, base_endpoint):
        """This test is to check the help endpoint with random i.e arg argument"""
        random_arg = "arg"
        help_random_endpoint = base_endpoint + "help/arg"
        help_random_endpoint = requests.get(help_random_endpoint)
        assert help_random_endpoint.status_code == 200
        assert (
            help_random_endpoint.json()["data"]["response"]
            == f"Unknown section '{random_arg}' in the --help-section option\n"
        )

    def test_point(self, base_endpoint):
        """This test is to test point endpoint with example data"""
        point_endpoint = base_endpoint + "point"
        directory_path = Path(os.getcwd())

        config_path = "rest_api_flint.example/config/point_example.json"

        with open(config_path) as data_file:
            data = json.load(data_file)

        config_string = json.dumps(data)
        point_response = requests.post(point_endpoint, data=config_string)
        assert point_response.status_code == 200

    def test_rothc(self, base_endpoint):
        """This test is to test rothc endpoint with example data"""
        rothc_endpoint = base_endpoint + "rothc"
        directory_path = Path(os.getcwd())

        config_path = "rest_api_flint.example/config/point_rothc_example.json"

        with open(config_path) as data_file:
            data = json.load(data_file)

        config_string = json.dumps(data)
        rothc_response = requests.post(rothc_endpoint, data=config_string)
        assert rothc_response.status_code == 200
