<h3> GCBM API Endpoints </h3>

### Create a new GCBM simulation

The title of a new simulation can be passed or the default title `simulation` will be used. (i.e the default title of the simulation is `simulation`, here the title `run4` is used)

| **Method** | **Endpoint** | **Response code** |
| ---------- | ------------ | ----------------- |
| POST       | `/gcbm/new`  | 200 OK (Success)  |

Example:

```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/new
```

Expected response (Success):

```json
{
  "data": "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
}
```

### Upload configuration files

Upload all of the files required to run the simulation.
| **Method** | **Endpoint** | **Response codes** |
|--- | ---| --- |
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

You can upload all the simulation files at once or upload them separately. To upload files separately follow the commands below.

### Upload Disturbances file

Upload Disturbances file to run the simulation.
| **Method** | **Endpoint** | **Response codes** |
|--- | ---| --- |
| POST| `/gcbm/upload/disturbances` | 200 OK (Success), 400 (Error) |

Example:

Go to the location of the unzipped file `GCBM_New_Demo_Run.zip`

```
cd path-to-unzipped-file
```

Upload all the files present in the disturbances folder.

```
curl -F disturbances='@disturbances/disturbances_2011_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2012_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2013_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2014_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2015_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2016_moja.tiff' \
		-F disturbances='@disturbances/disturbances_2018_moja.tiff' \
		-F title="run4" \
		http://localhost:8080/gcbm/upload/disturbances
```

Expected response (Success):

```json
{
  "data": "Disturbances file uploaded succesfully. Proceed to the next step."
}
```

### Upload Classifiers file

Upload Classifiers file to run the simulation.
| **Method** | **Endpoint** | **Response codes** |
|--- | ---| --- |
| POST| `/gcbm/upload/classifiers` | 200 OK (Success), 400 (Error) |

Example:

Go to the location of the unzipped file `GCBM_New_Demo_Run.zip`

```
cd path-to-unzipped-file
```

Upload all the files present in the disturbances folder.

```
curl -F classifiers='@classifiers/Classifier1_moja.tiff' \
		-F classifiers='@classifiers/Classifier2_moja.tiff' \
		-F title="run4" \
		http://localhost:8080/gcbm/upload/classifiers
```

Expected response (Success):

```json
{
  "data": "Classifiers file uploaded succesfully. Proceed to the next step."
}
```

### Upload Miscellaneous file

Upload Miscellaneous file to run the simulation.
| **Method** | **Endpoint** | **Response codes** |
|--- | ---| --- |
| POST| `/gcbm/upload/miscellaneous` | 200 OK (Success), 400 (Error) |

Example:

Go to the location of the unzipped file `GCBM_New_Demo_Run.zip`

```
cd path-to-unzipped-file
```

Upload all the files present in the disturbances folder.

```
curl -F miscellaneous='@miscellaneous/initial_age_moja.tiff' \
		-F miscellaneous='@miscellaneous/mean_annual_temperature_moja.tiff' \
		-F title="run4" \
		http://localhost:8080/gcbm/upload/miscellaneous
```

Expected response (Success):

```json
{
  "data": "Miscellaneous file uploaded succesfully. Proceed to the next step."
}
```

### Upload db file

Upload db file to run the simulation.
| **Method** | **Endpoint** | **Response codes** |
|--- | ---| --- |
| POST| `/gcbm/upload/db` | 200 OK (Success), 400 (Error) |

Example:

Go to the location of the unzipped file `GCBM_New_Demo_Run.zip`

```
cd path-to-unzipped-file
```

Upload all the files present in the disturbances folder.

```
curl -F db='@db/gcbm_input.db' \
		-F title="run4" \
		http://localhost:8080/gcbm/upload/db
```

Expected response (Success):

```json
{
  "data": "db file uploaded succesfully. Proceed to the next step."
}
```

### Run the simulation

After uploading your files, you can run the simulation through this endpoint.

| **Method** | **Endpoint**    | **Response code** |
| ---------- | --------------- | ----------------- |
| POST       | `/gcbm/dynamic` | 200 OK (Success)  |

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

| **Method** | **Endpoint**   | **Response code** |
| ---------- | -------------- | ----------------- |
| POST       | `/gcbm/status` | 200 OK (Success)  |

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

| **Method** | **Endpoint**     | **Response code** |
| ---------- | ---------------- | ----------------- |
| POST       | `/gcbm/download` | 200 OK (Success)  |

A file named `output.zip` will be obtained. This file contains the outputs generated, which can be analysed on unzipping.

```
curl -d "title=run4" -X POST http://localhost:8080/gcbm/download -L -o run4.zip
```

### Get Config mean annual temperature moja file

| **Method** | **Endpoint**      | **Response code** |
| ---------- | ----------------- | ----------------- |
| POST       | `/gcbm/getConfig` | 200 OK (Success)  |

```
curl -F file_name="mean_annual_temperature_moja" \
                                -F title="run4" \
                                http://localhost:8080/gcbm/getConfig

```

Expected response (Success):

```json
{"data":{
        "blockLatSize":0.1,"blockLonSize":0.1,"cellLatSize":0.00025,
        "cellLonSize":0.00025,"layer_data":"Float32","layer_type":"GridLayer",
        "nodata":32767.0,"tileLatSize":1.0,"tileLonSize":1.0
        }
}
```

### Get Config internal_variables file

| **Method** | **Endpoint**      | **Response code** |
| ---------- | ----------------- | ----------------- |
| POST       | `/gcbm/getConfig` | 200 OK (Success)  |

```
curl -F file_name="internal_variables" \
                        -F title="run4" \
                        http://localhost:8080/gcbm/getConfig

```

Expected response (Success):

```json
{"data":{
        "Variables":{
                        "LandUnitId":-1,"LocalDomainId":1,"age":0,"age_class":0,"blockIndex":0,
                        "cellIndex":0,"classifier_set":{},"current_land_class":"FL","historic_land_class":"FL",
                        "is_decaying":true,"is_forest":true,"landUnitArea":0,"landUnitBuildSuccess":true,
                        "localDomainId":0,"peatlandId":-1,"regen_delay":0,"run_delay":false,"run_moss":false,
                        "run_peatland":false,"simulateLandUnit":true,
                        "spatialLocationInfo":{
                                "flintdata":{"library":"internal.flint","settings":{},"type":"SpatialLocationInfo"}
                                },
                        "spinup_moss_only":false,"tileIndex":0,"unfccc_land_class":"UNFCCC_FL_R_FL"
                }
        }
}
```


### Get Config localdomain file

| **Method** | **Endpoint**      | **Response code** |
| ---------- | ----------------- | ----------------- |
| POST       | `/gcbm/getConfig` | 200 OK (Success)  |

```
curl -F file_name="localdomain" \
                -F title="run4" \
                http://localhost:8080/gcbm/getConfig

```

Expected response (Success):

```json
{"data":{"Libraries":{"moja.modules.cbm":"external","moja.modules.gdal":"external"},
        "LocalDomain":{"end_date":"2021/01/01","landUnitBuildSuccess":"landUnitBuildSuccess",
                "landscape":{"num_threads":4,"provider":"RasterTiled",
                "tile_size_x":1.0,"tile_size_y":1.0,
                "tiles":[{"index":12674,"x":-106,"y":55}],
                "x_pixels":4000,"y_pixels":4000},
                "sequencer":"CBMSequencer","sequencer_library":"moja.modules.cbm",
                "simulateLandUnit":"simulateLandUnit","start_date":"2010/01/01",
                "timing":"annual","type":"spatial_tiled"}}} 
```

### List all of the simulations

| **Method** | **Endpoint** | **Response code** |
| ---------- | ------------ | ----------------- |
| GET        | `/gcbm/list` | 200 OK (Success)  |

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
