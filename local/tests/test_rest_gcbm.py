import pytest
import requests
import zipfile
import tempfile
import os

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
    
    @pytest.fixture
    def yield_title(self):
        yield "testtitle"

    @pytest.fixture(scope="module")
    def create_demo_files(self):
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        zip_dir = os.getcwd() + '/GCBM_Demo_Run.zip'
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/tests_files'
        unzipped_file = zipfile.ZipFile(zip_dir, 'r')
        unzipped_file.extractall(test_files_dir)
    
    @pytest.fixture
    def yield_config_files(self):
        config_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/tests_files/config'
        files = []

        for file in os.listdir(config_files_dir):
            if file.endswith(".json"):
                temp = ('config_files',(file,open(config_files_dir + '/' + file,'rb'),'application/json'))
                files.append(temp)
            elif file.endswith(".cfg"):
                temp = ('config_files',(file,open(config_files_dir + '/' + file,'rb'),'application/octet-stream'))
                files.append(temp)
        
        yield files
        
    @pytest.fixture
    def yield_input_files(self):
        input_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/tests_files/layers/tiled'
        files = []

        for file in os.listdir(input_files_dir):
            if file.endswith(".tiff"):
                temp = ('input',(file,open(input_files_dir + '/' + file,'rb'),'image/tiff'))
                files.append(temp)
            elif file.endswith(".json"):
                temp = ('input',(file,open(input_files_dir + '/' + file,'rb'),'application/json'))
                files.append(temp)

        yield files

    @pytest.fixture
    def yield_db_file(self):
        db_dir = os.path.dirname(os.path.realpath(__file__)) + '/tests_files/input_database'
        files = []

        for file in os.listdir(db_dir):
            if file.endswith(".db"):
                temp = ('db',(file,open(db_dir + '/' + file,'rb'),'application/octet-stream'))
                files.append(temp)
        
        yield files
    
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
        assert status_response.json().get("finished") != "In Progress"

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

    def test_new(self, gcbm_endpoint, yield_title):
        new_endpoint = gcbm_endpoint + "new"
        data = {
            'title' : yield_title
        }
        new_response = requests.post(new_endpoint, data=data)
        assert new_response.status_code == 200
        
    def test_missing_configuration_file(self, gcbm_endpoint, yield_title):
        data = { 
            'title' : yield_title,
        }
        files = []
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, data=data, files=files)
        assert upload_response.status_code == 400
        assert upload_response.json().get("error") == "Missing configuration file"
    
    def test_upload(self, yield_title, yield_config_files, yield_input_files, yield_db_file, gcbm_endpoint):
        upload_files = yield_config_files + yield_input_files + yield_db_file
        data = {
            'title' : yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_missing_input(self, yield_title, gcbm_endpoint, yield_config_files):
        data = {
            'title' : yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, files=yield_config_files, data=data)
        assert upload_response.status_code == 400
        assert upload_response.json().get("error") == "Missing input"  

    def test_missing_database(self, yield_title, gcbm_endpoint, yield_config_files, yield_input_files):
        data = {
            'title' : yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, files=yield_config_files + yield_input_files, data=data)
        assert upload_response.status_code == 400
        assert upload_response.json().get("error") == "Missing database"
    
    def test_dynamic(self, gcbm_endpoint, yield_title):
        data = {
            'title' : yield_title,
        }
        dynamic_endpoint = gcbm_endpoint + "dynamic"
        dynamic_response = requests.post(dynamic_endpoint, data=data)
        assert dynamic_response.status_code == 200
        assert dynamic_response.json().get("status") == "Run started"
    
    def test_download(self, gcbm_endpoint, yield_title):
        data = {
            'title' : yield_title,
        }
        download_endpoint = gcbm_endpoint + "download"
        download_response = requests.post(download_endpoint, data=data)
        assert download_response.status_code == 200
