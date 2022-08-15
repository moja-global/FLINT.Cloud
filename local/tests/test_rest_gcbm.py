from distutils.command.upload import upload
from pkg_resources import yield_lines
import pytest
import requests
import zipfile
import os
import shutil


@pytest.fixture(autouse=True)
def create_demo_files():
    """ This fixture creates a test_files under local/tests by extracting \
        GCBM_New_Demo_Run.zip from /FLINT.CLOUD for testing """
    path_parent = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path_parent)
    path_parent = os.path.dirname(path_parent)
    os.chdir(path_parent)
    zip_dir2 = os.getcwd() + "/rest_api_gcbm/templates.zip"
    templates_dir = os.getcwd() + "/rest_api_gcbm/templates"
    path_parent = os.path.dirname(path_parent)
    os.chdir(path_parent)
    zip_dir = os.getcwd() + "/GCBM_New_Demo_Run.zip"
    test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/tests_files"
    test_templates_dir = (
        os.path.dirname(os.path.realpath(__file__)) + "/tests_templates"
    )
    unzipped_file = zipfile.ZipFile(zip_dir, "r")
    unzipped_file.extractall(test_files_dir)
    unzipped_file1 = zipfile.ZipFile(zip_dir2, "r")
    unzipped_file1.extractall(test_templates_dir)


class TestApiFlintGCBM:
    @pytest.fixture
    def base_endpoint(self):
        """ Port 8080 of the docker container is mapped to 8080 on the \
        ubuntu machine running the action, api testing is performed at port 8080"""
        self.ENDPOINT = "http://localhost:8080/"
        yield self.ENDPOINT

    @pytest.fixture
    def help_endpoint(self):
        """This is the endpoint for the help page"""
        self.ENDPOINT = "http://localhost:8080/help/"
        yield self.ENDPOINT

    @pytest.fixture
    def gcbm_endpoint(self):
        """This is the endpoint for the gcbm action"""
        self.ENDPOINT = "http://localhost:8080/gcbm/"
        yield self.ENDPOINT

    @pytest.fixture
    def yield_title(self):
        """This would yield a title for the test"""
        yield "testtitle"

    @pytest.fixture
    def yield_templates_files(self):
        """ This fixture yields a list of config files to be uploaded to the server via \
            gcbm/upload endpoint. Check the local_run.postman_collection in local/rest_api_gcbm """
        template_files_dir = (
            os.path.dirname(os.path.realpath(__file__)) + "/tests_templates"
        )
        files = []

        for file in os.listdir(template_files_dir):
            if file.endswith(".json"):
                temp = (
                    "config_files",
                    (
                        file,
                        open(template_files_dir + "/" + file, "rb"),
                        "application/json",
                    ),
                )
                files.append(temp)
            elif file.endswith(".cfg"):
                temp = (
                    "templates",
                    (
                        file,
                        open(template_files_dir + "/" + file, "rb"),
                        "application/octet-stream",
                    ),
                )
                files.append(temp)

        yield files

        del template_files_dir

    @pytest.fixture
    def yield_classifiers_files(self):
        """ This fixture yields a list of classifiers files to be uploaded to the server via \
            gcbm/upload endpoint. Check the local_run.postman_collection in local/rest_api_gcbm """
        classifiers_files_dir = (
            os.path.dirname(os.path.realpath(__file__))
            + "/tests_files/GCBM_New_Demo_Run/classifiers"
        )
        print(classifiers_files_dir)
        files = []

        for file in os.listdir(classifiers_files_dir):
            if file.endswith(".tiff"):
                temp = (
                    "classifiers",
                    (
                        file,
                        open(classifiers_files_dir + "/" + file, "rb"),
                        "image/tiff",
                    ),
                )
                files.append(temp)

        yield files

    @pytest.fixture
    def yield_disturbances_files(self):
        """ This fixture yields a list of classifiers files to be uploaded to the server via \
            gcbm/upload endpoint. Check the local_run.postman_collection in local/rest_api_gcbm """
        disturbances_files_dir = (
            os.path.dirname(os.path.realpath(__file__))
            + "/tests_files/GCBM_New_Demo_Run/disturbances"
        )
        files = []

        for file in os.listdir(disturbances_files_dir):
            if file.endswith(".tiff"):
                temp = (
                    "disturbances",
                    (
                        file,
                        open(disturbances_files_dir + "/" + file, "rb"),
                        "image/tiff",
                    ),
                )
                files.append(temp)

        yield files

    @pytest.fixture
    def yield_miscellaneous_files(self):
        """ This fixture yields a list of classifiers files to be uploaded to the server via \
            gcbm/upload endpoint. Check the local_run.postman_collection in local/rest_api_gcbm """
        miscellaneous_files_dir = (
            os.path.dirname(os.path.realpath(__file__))
            + "/tests_files/GCBM_New_Demo_Run/miscellaneous"
        )
        files = []

        for file in os.listdir(miscellaneous_files_dir):
            if file.endswith(".tiff"):
                temp = (
                    "miscellaneous",
                    (
                        file,
                        open(miscellaneous_files_dir + "/" + file, "rb"),
                        "image/tiff",
                    ),
                )
                files.append(temp)

        yield files

    @pytest.fixture
    def yield_db_file(self):
        """ This fixture yields a db file to be uploaded to the server via \
            gcbm/upload endpoint. Check the local_run.postman_collection in local/rest_api_gcbm """
        db_dir = (
            os.path.dirname(os.path.realpath(__file__))
            + "/tests_files/GCBM_New_Demo_Run/db"
        )
        files = []

        for file in os.listdir(db_dir):
            if file.endswith(".db"):
                temp = (
                    "db",
                    (file, open(db_dir + "/" + file, "rb"), "application/octet-stream"),
                )
                files.append(temp)

        yield files

    def test_check(self, base_endpoint):
        """This would test the base_endpoint"""
        check_endpoint = base_endpoint + "check"
        check_response = requests.get(check_endpoint)
        assert check_response.status_code == 200
        assert check_response.text == "Checks OK"

    @pytest.mark.skip
    def test_spec(self, base_endpoint):
        """ This would test the spec endpoint \
            The spec endpoint now currently throws error as of writing this test """
        spec_endpoint = base_endpoint + "spec"
        spec_response = requests.get(spec_endpoint)
        assert spec_response.status_code == 500

    @pytest.mark.skip(reason="Test fails on CI")
    def test_list(self, gcbm_endpoint):
        """This would test the list endpoint"""
        list_endpoint = gcbm_endpoint + "list"
        list_response = requests.get(list_endpoint)
        assert list_response.status_code == 200

    def test_version(self, base_endpoint):
        """This would test the version endpoint"""
        version_endpoint = base_endpoint + "version"
        version_response = requests.get(version_endpoint)
        assert version_response.status_code == 200

    def test_help_all(self, help_endpoint):
        """This would test the help endpoint with 'all' argument"""
        help_endpoint = help_endpoint + "all"
        help_response = requests.get(help_endpoint)
        assert help_response.status_code == 200

    def test_help_random_arg(self, help_endpoint):
        """This would test the help endpoint with a random argument"""
        random_arg = "test"
        help_endpoint = help_endpoint + random_arg
        help_response = requests.get(help_endpoint)
        assert help_response.status_code == 200
        assert (
            help_response.json()["data"]["response"]
            == f"Unknown section '{random_arg}' in the --help-section option\n"
        )

    def test_new(self, gcbm_endpoint, yield_title):
        """ This test would create a new simulation under \
            the title provided by the yield_title fixture. """
        new_endpoint = gcbm_endpoint + "new"
        data = {"title": yield_title}
        new_response = requests.post(new_endpoint, data=data)
        assert new_response.status_code == 200

    # @pytest.mark.skip
    def test_missing_configuration_file(self, gcbm_endpoint, yield_title):
        """ This test would try to give false positive on \
            uploading without any config files """
        data = {
            "title": yield_title,
        }
        files = []
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, data=data, files=files)
        assert upload_response.status_code == 400
        assert upload_response.json().get("error") == "Missing configuration file"

    def test_upload(
        self,
        yield_title,
        yield_templates_files,
        yield_classifiers_files,
        yield_disturbances_files,
        yield_miscellaneous_files,
        yield_db_file,
        gcbm_endpoint,
    ):
        """ This test would upload the files provided by the \
            yield_classifiers_files, yield_disturbances_files, yield_miscellaneous_files and yield_db_file fixtures. \
            These files are needed for GCBM Implementation FLINT. """
        upload_files = (
            yield_templates_files
            + yield_classifiers_files
            + yield_disturbances_files
            + yield_miscellaneous_files
            + yield_db_file
        )
        data = {
            "title": yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_dynamic(self, gcbm_endpoint, yield_title):
        """ This test would check whether the dynamic endpoint \
            is working or not with the title provided by the \
            yield_title fixture. This test would start the GCBM \
            Dynamic Implementation of FLINT under the title provided \
            by yield_title fixture and already uploaded files."""
        data = {
            "title": yield_title,
        }
        dynamic_endpoint = gcbm_endpoint + "dynamic"
        dynamic_response = requests.post(dynamic_endpoint, data=data)
        assert dynamic_response.status_code == 200
        assert dynamic_response.json().get("status") == "Run started"

    def test_status(self, gcbm_endpoint, yield_title):
        """ This test would check whether the status endpoint \
            is working or not with the title provided by the \
            yield_title fixture. It returns the status of a simulation which \
            we already uploaded the files under the title by \
            yield_title fixutre. """
        status_endpoint = gcbm_endpoint + "status"
        data = {"title": yield_title}
        status_response = requests.post(status_endpoint, json=data)
        assert status_response.status_code == 200
        assert status_response.json().get("finished") == "In Progress"

    def test_upload_title(self, base_endpoint, yield_title):
        """ This test would check wheather the upload title \
            is working or not with the title provided by the \
            yield_title fixture. 
        """
        upload_title = base_endpoint + "upload/title"
        data = {
            "title": yield_title,
        }
        upload_reponse = requests.post(upload_title, json=data)
        assert upload_reponse.status_code == 200

    def test_gcbm_disturbances(
        self, gcbm_endpoint, yield_disturbances_files, yield_title
    ):
        """ This test would check wheather the upload disturbance  \
            is working or not by uploading a GCBM disturbance file \
            with yield_title. 
        """
        upload_files = yield_disturbances_files
        data = {
            "title": yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload/disturbances"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_gcbm_classifiers(
        self, gcbm_endpoint, yield_classifiers_files, yield_title
    ):
        """ This test would check wheather the upload classifiers \
            is working or not by uploading a GCBM classifiers file \
            with yield_title. 
        """
        upload_files = yield_classifiers_files
        data = {
            "title": yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload/classifiers"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_gcbm_miscellaneous(
        self, gcbm_endpoint, yield_miscellaneous_files, yield_title
    ):
        """ This test would check wheather the upload miscellaneous \
            is working or not by uploading a GCBM miscellaneous file \
            with yield_title. 
        """
        upload_files = yield_miscellaneous_files
        data = {
            "title": yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload/miscellaneous"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_gcbm_db(self, gcbm_endpoint, yield_db_file, yield_title):
        """ This test would check wheather the upload db \
            is working or not by uploading a GCBM db file \
            with yield_title. 
        """
        upload_files = yield_db_file
        data = {
            "title": yield_title,
        }
        upload_endpoint = gcbm_endpoint + "upload/db"
        upload_response = requests.post(upload_endpoint, files=upload_files, data=data)
        assert upload_response.status_code == 200

    def test_gcbm_tables(self, base_endpoint, yield_title):
        """This test case would check the get table method. \
           A title name would be sent in the URL params to locate \
           the database file.
        """
        data = {
            "title": yield_title,
        }
        table_endpoint = base_endpoint + f"upload/db/tables"
        upload_response = requests.post(table_endpoint, data=data)
        assert upload_response.status_code == 200

    @pytest.mark.skip(reason="Test fails on CI")
    def test_download(self, gcbm_endpoint, yield_title):
        """ This test would check the download endpoint. \
            In last tests, we uploaded the files under the title \
            run the GCBM Implementation FLINT and we would have been got the output in the \
            input/yield_title/output.zip ."""
        data = {
            "title": yield_title,
        }
        download_endpoint = gcbm_endpoint + "download"
        download_response = requests.post(download_endpoint, data=data)
        assert download_response.status_code == 200
