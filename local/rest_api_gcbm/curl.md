<h3> GCBM API Endpoints </h3>

### Create a new GCBM simulation
The title of a new simulation can be passed or the default title `simulation` will be used. (i.e the default title of the simulation is `simulation`, here the title `run4` is used)

| **Method** | **Endpoint** | **Response code** | 
|---  | ---| --- |
| POST| `/gcbm/new` | 200 OK (Success) |


Example:
```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/new
```

Expected response (Success):
```json
{
  "data":  "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload." 
}
```

### Upload configuration files 
Upload all of the files required to run the simulation.
| **Method** | **Endpoint** | **Response codes** | 
|---  | ---| --- |
| POST| `/gcbm/upload` | 200 OK (Success), 400 (Error) |

Example:

Go to the location of the unzipped file `GCBM_New_Demo_Run.zip`

```
cd path-to-unzipped-file
```

All the inputs are uploaded via a `POST` request

```
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

Expected response (Success):
```json
{
  "data": "All files uploaded succesfully. Proceed to the next step of the API at gcbm/dynamic."
}
```

### Run the simulation 
After uploading your files, you can run the simulation through this endpoint.

| **Method** | **Endpoint** | **Response code** | 
|---  | ---| --- |
| POST | `/gcbm/dynamic` | 200 OK (Success) |


Example:

```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/dynamic
```

Expected response (Success):
```json
{
  "status": "Run started"
}
```

### Get status of the simulation 

| **Method** | **Endpoint** | **Response code** | 
|---  | ---| --- |
| POST | `/gcbm/status` | 200 OK (Success) |


```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/status
```


Expected response (In progress):
```json
{
  "finished": "In Progress"
}
```

Expected response (When simulation completes):
```json
{
  "finished": "Output is ready to download at gcbm/download"
}
```

### Download the result of simulation 
| **Method** | **Endpoint** | **Response code** | 
|---  | ---| --- |
| POST | `/gcbm/download` | 200 OK (Success) |

A file named `output.zip` will be obtained. This file contains the outputs generated, which can be analysed on unzipping.

```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/download -L -o run4.zip
```

### List all of the simulations 
| **Method** | **Endpoint** | **Response code** | 
|---  | ---| --- |
| GET | `/gcbm/list` | 200 OK (Success) |

```
curl http://localhost:8080/gcbm/list
```

Expected response (Success):
```json
{
  "data": ["run4"],
  "message": "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download."
}
```
