<h3> Endpoints </h3>

1.  `/gcbm/new/`

    The title of a new simulation can be passed or the default title `simulation` will be used. (i.e the default title of the simulation is `simulation`, here the title `run4` is used)

    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/new
    ````

2. `/gcbm/upload`

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
3. `/gcbm/run`

    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/run
    ```

4. `/gcbm/status`
    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/status
    ```
5. `/gcbm/download`
    A file named `output.zip` will be obtained. This file contains the outputs generated, which can be analysed on unzipping.

    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/download -L -o run4.zip
    ```
6. `/gcbm/list`
    ```
        curl http://localhost:8080/gcbm/list
    ```
