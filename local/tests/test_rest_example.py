import pytest
import requests

'''
    Unit test cases are written for the rest_api_flint.example
'''


class TestApiFlint:

    @pytest.fixture
    def base_endpoint(self):
        #The port on which the docker container is running, is used here
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