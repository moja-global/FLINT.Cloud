# FLINT.Cloud
 
### GCBM local-run REST API Setup  
 
Run the GCBM local-run container by pushing the following command:

```bash
docker-compose up
```

Navigate to http://localhost:8080/ in the browser. You can stop the running container by pushing the following command:

```bash
docker-compose down
```

Currently the REST API has the following endpoints available for access:-
 
|      Endpoint     | Functionality | Method | 
| :----------------: | :----------------: | :----------------: | 
|   **\help\all**    | This endpoint produces a help message with information on all options for moja.CLI | `GET`
|   **\help\arg**    |  This endpoint produces a help message with information on option arg for moja.CLI. | `GET`
|   **\gcbm\new**    |  This endpoint creates a new directory to store input and output files of the simulation. Parameter to be passed in the body is the title of the new simulation or default value simulation will be used.   | `POST` |
|  **\gcbm\upload**  | This endpoint is used to upload the input files: config_files, input and database. Remember to upload the files in the body from the GCBM folder which is available in the root of this repository for setup and use. A directory /input will be created to store the specified files. | `POST` |
| **\gcbm\run**  |  This endpoint runs simulation in a thread and generates an output zip file in /output directory. The process may take a while. Parameter is the title of the simulation. | `POST` |
|  **\gcbm\status**  | This endpoint is employed to check the status of the simulation. It sends a message 'Output is ready to download' to notify that the output zip file is generated. Parameter is the title of the simulation. | `POST`
|  **\gcbm\download**  | This endpoint is used to download the output zip file. Parameter is the title of the simulation. | `POST`
|  **\gcbm\list**  | This endpoint retrieves the complete list of simulations that are created using /new.  | `GET`

The inputs are contained in `GCBM_Demo_Run.zip`, present in the root of the directory. This file must be unzipped for further usage.

<h3> Once the container is up and running, the following methods can be used to interact with the endpoints </h3>

1. A sample Postman collection is available [here](https://github.com/nynaalekhya/FLINT.Cloud/blob/local-gcbm-run/rest_local_run/local_run.postman_collection). Import the collection to Postman and run the endpoints.

2. The endpoints can be interacted with using `cURL`. 
curl is used in command lines or scripts to transfer data. Find out more about curl [here](https://curl.se/). Commands using cURL can be found [here](curl.md)

