# GCBM REST API Setup

The simulation is currently supported on Linux/macOS. To run the GCBM simulation locally, execute the following steps:

1. Clone the `FLINT.Cloud` repository using the command:

  ```bash
  git clone https://github.com/moja-global/FLINT.Cloud.git
  ```

2. Navigate to the `rest_api_gcbm` directory: 
  ```bash
  cd FLINT.Cloud/local/rest_api_gcbm
  ```

3. Build the docker image with the image name `gcbm-api`:
  ```bash
  docker build --build-arg BUILD_TYPE=RELEASE --build-arg NUM_CPU=4 -t gcbm-api .
  ```

4. Create a container using the `gcbm-api` image and start it:
 ```bash
 docker run --rm -p 8080:8080 gcbm-api
 ```

Navigate to http://localhost:8080/ in the browser to test the various endpoints available.

## Endpoints

The GCBM REST API has the following endpoints available for access:
 
|      Endpoint     | Functionality | Method | 
| :----------------: | :----------------: | :----------------: | 
|   **/help/all**    | This endpoint produces a help message with information on all options for moja.CLI | `GET`
|   **/help/arg**    |  This endpoint produces a help message with information on option arg for moja.CLI. | `GET`
|   **/gcbm/new**    |  This endpoint creates a new directory to store input and output files of the simulation. Parameter to be passed in the body is the title of the new simulation or default value simulation will be used.   | `POST` |
|  **/gcbm/upload**  | This endpoint is used to upload the input files: config_files, input and database. Remember to upload the files in the body from the GCBM folder which is available in the root of this repository for setup and use. A directory /input will be created to store the specified files. | `POST` |
| **/gcbm/run**  |  This endpoint runs simulation in a thread and generates an output zip file in /output directory. The process may take a while. Parameter is the title of the simulation. | `POST` |
|  **/gcbm/status**  | This endpoint is employed to check the status of the simulation. It sends a message 'Output is ready to download' to notify that the output zip file is generated. Parameter is the title of the simulation. | `POST`
|  **/gcbm/download**  | This endpoint is used to download the output zip file. Parameter is the title of the simulation. | `POST`
|  **/gcbm/list**  | This endpoint retrieves the complete list of simulations that are created using /new.  | `GET`

The inputs are contained in `GCBM_New_Demo_Run.zip`, present in the root of the directory. This file must be unzipped for further usage. Once the container is up and running, the following methods can be used to interact with the endpoints:

1. A sample collection is available [in our Postaman collection](https://github.com/nynaalekhya/FLINT.Cloud/blob/local-gcbm-run/rest_local_run/local_run.postman_collection). Import the collection to Postman and run the endpoints.

2. The endpoints can be interacted with using `cURL`. `cURL` is used in command lines or scripts to transfer data. Find out more about curl [on the official website](https://curl.se/). Commands using `cURL` can be found [in our documentation](curl.md)

## Running a GCBM simulation

To run the endpoints and start a new GCBM simulation : 

1. Unzip `GCBM_New_Demo_Run` and open a terminal inside the folder and run the following curl commands:
 
2. Create a new simulation (the default title of the simulation is `simulation`; Here the title `run4` is used): 
   ```bash
   curl -d "title=run4" -X POST http://localhost:8080/gcbm/new
   ````

3. Upload the input files:
   ```bash
   curl -F disturbances='@disturbances/disturbances_2011_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2012_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2013_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2014_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2015_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2016_moja.tiff' \
        -F disturbances='@disturbances/disturbances_2018_moja.tiff' \
        -F classifiers='@classifiers/Classifier1_moja.tiff' \
        -F classifiers='@classifiers/Classifier2_moja.tiff' \
        -F db='@db/gcbm_input.db' \
        -F miscellaneous='@miscellaneous/initial_age_moja.tiff' \
        -F miscellaneous='@miscellaneous/mean_annual_temperature_moja.tiff' \
        -F title="run4" \
        http://localhost:8080/gcbm/upload
    ```

4. To start the simulation, run:
   ```bash
   curl -d "title=run4" -X POST http://localhost:8080/gcbm/run
   ```
   
   It should take around 35-40 minutes to finish running and even less depending on your local machine specifications. The end message should be `SQLite insert complete`. The message would be printed on the terminal used to execute Docker commands.
    
   
5. To download the simulation outputs, run the following curl command 3-5 minutes after the simulation has finished running:
   ```bash
   curl -d "title=run4" -X POST http://localhost:8080/gcbm/download -L -o run4.zip
   ```
