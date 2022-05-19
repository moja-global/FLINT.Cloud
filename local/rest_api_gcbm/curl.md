<h3> Endpoints </h3>

1.  `/gcbm/new/` 

    The title of a new simulation can be passed or the default title `simulation` will be used. (i.e the default title of the simulation is `simulation`, here the title `run4` is used)

    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/new
    ````

2. `/gcbm/upload`

    Go to the location of the unzipped file `GCBM_Demo_Run.zip`

    ```
        cd path-to-unzipped-file
    ```

    All the inputs are uploaded via a `POST` request
    ```
        curl -F config_files='@config/variables.json' \
            -F config_files='@config/spinup.json' \
            -F config_files='@config/provider_config.json' \
            -F config_files='@config/pools_cbm.json' \
            -F config_files='@config/modules_output.json' \
            -F config_files='@config/modules_cbm.json' \
            -F config_files='@config/logging.conf' \
            -F config_files='@config/localdomain.json' \
            -F config_files='@config/internal_variables.json' \
            -F config_files='@config/gcbm_config.cfg' \
            -F input='@layers/tiled/bounding_box.tiff' \
            -F input='@layers/tiled/Classifier1_moja.json' \
            -F input='@layers/tiled/Classifier1_moja.tiff' \
            -F input='@layers/tiled/Classifier2_moja.json' \
            -F input='@layers/tiled/Classifier2_moja.tiff' \
            -F input='@layers/tiled/disturbances_2011_moja.json' \
            -F input='@layers/tiled/disturbances_2011_moja.tiff' \
            -F input='@layers/tiled/disturbances_2012_moja.json' \
            -F input='@layers/tiled/disturbances_2012_moja.tiff' \
            -F input='@layers/tiled/disturbances_2013_moja.json' \
            -F input='@layers/tiled/disturbances_2013_moja.tiff' \
            -F input='@layers/tiled/disturbances_2014_moja.json' \
            -F input='@layers/tiled/disturbances_2014_moja.tiff' \
            -F input='@layers/tiled/disturbances_2015_moja.json' \
            -F input='@layers/tiled/disturbances_2015_moja.tiff' \
            -F input='@layers/tiled/disturbances_2016_moja.json' \
            -F input='@layers/tiled/disturbances_2016_moja.tiff' \
            -F input='@layers/tiled/disturbances_2018_moja.json' \
            -F input='@layers/tiled/disturbances_2018_moja.tiff' \
            -F input='@layers/tiled/initial_age_moja.json' \
            -F input='@layers/tiled/initial_age_moja.tiff' \
            -F input='@layers/tiled/mean_annual_temperature_moja.json' \
            -F input='@layers/tiled/mean_annual_temperature_moja.tiff' \
            -F input='@layers/tiled/study_area.json' \
            -F input='@input_database/gcbm_input.db' \
            -F db='@input_database/gcbm_input.db' \
            -F title="run4" \
            http://localhost:8080/gcbm/upload

    ```
3. `/gcbm/dynamic`

    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/dynamic
    ```

4. `/gcbm/status`
    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/status
    ```
5. `/gcbm/download`
    A file named `output.zip` will be obtained. This file contains the outputs generated, which can be analysed on unzipping.
    
    ```
        curl -d "title=run4" -X POST http://localhost:8080/gcbm/download -L -o output.zip
    ```
6. `/gcbm/list`
    ```
        curl http://localhost:8080/gcbm/list
    ```
