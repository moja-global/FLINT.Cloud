import pytest
import requests


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
        base_endpoint = base_endpoint + "all"
        base_response = request.get(base_endpoint)
        assert base_response.status_code == 200

    def test_help_random_arg(self, base_endpoint):
        random_arg = "click"
        base_endpoint = base_endpoint + random_arg
        base_response = requests.get(base_endpoint)
        assert help_response.status_code == 200
        assert (
            help_response.json()["data"]["response"]
            == f"Unknown section '{random_arg}' in the --help-section option\n"
        )