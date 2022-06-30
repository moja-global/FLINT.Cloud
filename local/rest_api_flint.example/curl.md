# Endpoints

- ## `/version`

    Outputs the version number of moja.CLI.

    ```bash
        curl -X GET http://0.0.0.0:8080/version
    ```

- ## `/point`

    Runs point example and outputs point_example.csv as an attachment to be downloaded.

    Navigate to `rest_api_flint.example` folder.

    You can create new file in `config` folder by updating the values of `point_example.json` file

    ```bash
        curl -X POST -H "Content-Type: application/json" -d @config/NEW_FILE_NAME.json  http://0.0.0.0:8080/point
    ```

    or (2nd)

    ```bash
        curl -X POST -H "Content-Type: application/json" -d @config/point_example.json http://0.0.0.0:8080/point
    ```

    Following command uses default json data, just as the 2nd command does.

    ```bash
        curl -X POST -H "Content-Type: application/json" -d ""  http://0.0.0.0:8080/point
    ```

    The output file for default data is [`default_point_output.csv`](output/default_point_output.csv)

- ## `/rothc`

    Runs rothc example and outputs point_rothc_example.csv as an attachment to be downloaded.

    Navigate to `rest_api_flint.example` folder.

    You can create new file in `config` folder by updating the values of `point_rothc_example.json` file

    ```bash
        curl -X POST -H "Content-Type: application/json" -d @config/NEW_FILE_NAME.json  http://0.0.0.0:8080/rothc
    ```

    or (2nd)

    ```bash
        curl -X POST -H "Content-Type: application/json" -d @config/point_rothc_example.json http://0.0.0.0:8080/rothc
    ```

    Following command uses default json data, just as the 2nd command does.

    ```bash
        curl -X POST -H "Content-Type: application/json" -d ""  http://0.0.0.0:8080/rothc
    ```

    The output file for default data is [`default_point_output.csv`](output/default_point_rothc_output.csv)
