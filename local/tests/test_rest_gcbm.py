import pytest
import requests

class TestApiFlintGCBM:

    @pytest.fixture
    def base_endpoint(self):
        """ Port 8080 of the docker container is mapped to 8080 on the \
        ubuntu machine running the action, api testing is performed at port 8080"""
        self.ENDPOINT = "http://localhost:8080/"
        yield self.ENDPOINT
    
    @pytest.fixture
    def help_endpoint(self):
        self.ENDPOINT = "http://localhost:8080/help/"
        yield self.ENDPOINT
    
    @pytest.fixture
    def gcbm_endpoint(self):
        self.ENDPOINT = "http://localhost:8080/gcbm/"
        yield self.ENDPOINT

    def test_spec(self, base_endpoint):
        spec_endpoint = base_endpoint + "spec"
        spec_response = requests.get(spec_endpoint)
        assert spec_response.status_code == 200  

    def test_check(self, base_endpoint):
        check_endpoint = base_endpoint + "check"
        check_response = requests.get(check_endpoint)
        assert check_response.status_code == 200
        assert check_response.text == "Checks OK"
    
    def test_status(self, gcbm_endpoint):
        status_endpoint = gcbm_endpoint + "status"
        data = {
            "title" : "run4"
        }
        status_response = requests.post(status_endpoint, json=data)
        assert status_response.status_code == 200
        assert status_response.json().get("finished") == "In Progress"

    def test_list(self, gcbm_endpoint):
        list_endpoint = gcbm_endpoint + "list"
        list_response = requests.get(list_endpoint)
        assert list_response.status_code == 200

    def test_version(self, base_endpoint):
        version_endpoint = base_endpoint + "version"
        version_response = requests.get(version_endpoint)
        assert version_response.status_code == 200
    
    def test_help_all(self, help_endpoint):
        help_endpoint = help_endpoint + "all"
        help_response = requests.get(help_endpoint)
        assert help_response.status_code == 200
    
    def test_help_random_arg(self, help_endpoint):
        random_arg = 'test'
        help_endpoint = help_endpoint + random_arg
        help_response = requests.get(help_endpoint)
        assert help_response.status_code == 200
        assert help_response.json()["data"]["response"] == f"Unknown section '{random_arg}' in the --help-section option\n"

    def test_new(self, gcbm_endpoint):
        new_endpoint = gcbm_endpoint + "new"
        new_response = requests.post(new_endpoint)
        assert new_response.status_code == 200
    
    def test_dynamic(self, gcbm_endpoint):
        dynamic_endpoint = gcbm_endpoint + "dynamic"
        dynamic_response = requests.post(dynamic_endpoint)
        assert dynamic_response.status_code == 200
        assert dynamic_response.json().get("status") == "Run started"
    
    def test_missing_configuration_file(self, gcbm_endpoint):
        data = { }
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, data=data)
        assert upload_response.status_code == 400
        assert upload_response.json().get("error") == "Missing configuration file"
