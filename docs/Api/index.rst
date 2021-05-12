.. _Api:

FLINT.Cloud API Docs
####################

This section guides first-time contributors through the v1 API consumed by FLINT.Cloud. Data is returned in JSON Format and HTTP response status codes have been desginated to declare Success or Failure.
The API is created using Flask and flask-restful. 

.. contents:: Table of contents
   :local:
   :backlinks: none
   :depth:


GCBM: New simulation
====================

.. http:get:: /gcbm/new/

Creates a new GCBM simulation by passing a title for the simulation in the request form-data. If the simulation is already existing, an error message is returned with 400 HTTP Status Code.

**Example request**:

    .. tabs::

        .. code-tab:: bash

            $ curl --location --request POST 'http://0.0.0.0:8080/gcbm/new' \
            --header 'Content-Type: application/json' \
            --header 'accept: application/json' \
            --form 'title="example_new_1"'


    **Example response**:

    .. sourcecode:: json

        {
            "data": "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
        }

    :Request FormData Object:

        * **title** (*string*) -- required title of simulation.

GCBM: Upload files to simulation
================================

.. http:get:: /gcbm/upload/

Upload input files for the GCBM simulation by passing the files as request FormData. If the upload has any issue, an error message is returned with 400 HTTP Status Code.

**Example request**:

    .. tabs::

        .. code-tab:: bash

            $ curl --location --request POST 'http://0.0.0.0:8080/gcbm/upload' \
            --header 'Content-Type: multipart/form-data; boundary=---011000010111000001101001' \
            --header 'accept: application/json' \
            --form 'db=@"/home/kalilinux/Documents/Medium_Local_Run/input_database/gcbm_input.db"' \
            --form 'title="example"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/provider_config.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/localdomain.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/logging.conf"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/modules_output.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/variables.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/spinup.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/pools_cbm.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/modules_cbm.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/internal_variables.json"' \
            --form 'config_files=@"/home/kalilinux/Documents/Medium_Local_Run/config/gcbm_config.cfg"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/study_area.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/LdSpp_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/LdSpp_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/LdSpp_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/initial_age_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/initial_age_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/initial_age_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb2000_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb2000_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb2000_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1999_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1999_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1992_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1992_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1992_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1990_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1990_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1990_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1999_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1996_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1996_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1996_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1994_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1994_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1994_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1993_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1993_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1993_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1995_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1995_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1995_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1991_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1991_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mpb1991_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mean_annual_temperature_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mean_annual_temperature_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/mean_annual_temperature_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_2000_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_2000_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_2000_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1995_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1995_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1995_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1994_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1994_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1994_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1993_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1993_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1993_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1992_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1992_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1992_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1991_moja.tiff.aux.xml"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1991_moja.tiff"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/fire_1991_moja.json"' \
            --form 'input=@"/home/kalilinux/Documents/Medium_Local_Run/layers/tiled/bounding_box.tiff"'


    **Example response**:

    .. sourcecode:: json

        {
            "data": "All files uploaded sucessfully. Proceed to the next step of the API at gcbm/dynamic."
        }

    :Request FormData Object:

        * **db** (*file*) -- required input db for gcbm (gcbm_input.db).
        * **title** (*string*) -- required title of simulation (this was set in /new).
        * **config_files** (*files*) -- required config_files (cgf and json files in config folder).
        * **input** (*string*) -- required input files (tiff and json files in layers/tiled folder).


GCBM: Run dynamic simulation
============================

.. http:get:: /gcbm/dynamic/

Run the GCBM simulation by passing the files as request FormData. 

**Example request**:

    .. tabs::

        .. code-tab:: bash

            $ curl --location --request POST 'http://0.0.0.0:8080/gcbm/dynamic' \
            --header 'Content-Type: application/json' \
            --header 'accept: application/json' \
            --form 'title="example_new_1"'


    **Example response**:

    .. sourcecode:: json

        {
            "data": {
                "execTime": 187.98220562934875,
                "exitCode": 0,
                "response": "Operation executed successfully. Downloadable links for input and output are attached in the response. Alternatively, you may also download this simulation input and output results by making a request at gcbm/download with the title in the body.",
                "urls": {
                    "input": "https://storage.googleapis.com/simulation_data_flint-cloud/simulations/simulation-loop/input.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=authentication-bucket%40flint-cloud.iam.gserviceaccount.com%2F20210506%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210506T201854Z&X-Goog-Expires=1800&X-Goog-SignedHeaders=host&X-Goog-Signature=9c8b3ff058646f1d5b6601cb9b68421e8ce11e9e71ced83fbc9948ba60de14620b8dd53a15e62e639153026de997bdce075580c79bb8d28b3dc7ddc8514a64cabe21ffb3e91e89e8dc554813327ae40621cc37abdb817c1267d374841ae4b4fa7cadf1740d27ceddcdd67e2cd876a36138565be9edf095d4b188485d8f0a5d3d2f503bd73e116558d05dbbfed7f71d092d1f8f0b18097e80d183a82ddc13bae78650fe062bfba554abf84a7784a00b1030951a0baedd47e83084dad231f1adc321f3eac934a74e9fc213027eb0a97ebc38a5ca7b6228b42a98bddcdd9f8891bfb80adfd9a5541cff024b1f00814c864d7c8ca9038ab9c82ab809c7cce3c5bd4e",
                    "message": "These links are valid only upto 15 mins. Incase the links expire, you may create a new request.",
                    "output": "https://storage.googleapis.com/simulation_data_flint-cloud/simulations/simulation-loop/output.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=authentication-bucket%40flint-cloud.iam.gserviceaccount.com%2F20210506%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210506T201854Z&X-Goog-Expires=1800&X-Goog-SignedHeaders=host&X-Goog-Signature=60b0679176a15ac87a1aef22c90d0082330122c0e06cd7289e65266839f76d1c2113d5c98a36f634c88256b91d0273755cd395e2a3f86664ea463f3313b37561f06d158443568826785d4794f67e72a0b2feaff451961b3dcab20ee57cb6eb9c0f4751f59b87324d0bc376058c11f576c8796f82ca64c209f9655ccc49fca005034b295d2196c80fd263b3eee9b51ce96f1e7100e63da09d81e765522254dc96868dbcb8a92766084f8bf394d2c0ad39bdc21ed551014225305df5fdf0456c0b0be961101e6a001923938ac966e1eca488bd92f777952e3f7cd18c1cf56ae33fa6a1b514f70d94d3b1e34258df58918e0b398f39c5eba1c1b08f39cb3e1b63b1"
                }
            }
        }

    :Request FormData Object:

        * **title** (*string*) -- required title of simulation (this was set in /new).


GCBM: Download simulation
=========================

.. http:get:: /gcbm/download/

Download the GCBM simulation input and output zipped folders by passing the files as request FormData. The downloadable links returned are only valid for 30 mins.

**Example request**:

    .. tabs::

        .. code-tab:: bash

            $ curl --location --request POST 'http://0.0.0.0:8080/gcbm/download' \
            --header 'Content-Type: multipart/form-data; boundary=---011000010111000001101001' \
            --header 'accept: application/json' \
            --form 'title="example_new_1"'


    **Example response**:

    .. sourcecode:: json

        {
            "input": "https://storage.googleapis.com/simulation_data_flint-cloud/simulations/simulation-simulations/examplenew1/input.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=authentication-bucket%40flint-cloud.iam.gserviceaccount.com%2F20210506%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210506T200813Z&X-Goog-Expires=1800&X-Goog-SignedHeaders=host&X-Goog-Signature=6bf4f1d50e2fd9b2b6453d245db5ed14e23074027f3d029f6a2873e42b555b15ee31b4cd7ca561910e882065fb05194a1c2af359577533b4f3efc4c8530e3fcd4a5ac06c64f9b7fef96fc574519e885f716ba6abb428eaf3cd3e1fb131d6d4c4ca3948bafc26f22c9497aabeb43efdcce261455ec4515335a126a953f4e2fe8e95821dd924e7bb745f7c2b46a1ae5815b82052adc7741ddd424c48f43ac7c53b18049132b4a4aaef05bc12f856cc8b9ecf78870029411baf4b2c87c57927ec8b56fce777108f9268073950047268b6a40813ef3a72600d5dae1c95360300e133df00e13669fa69a53b9f3e85683bf50f0833bb253831b8f09039bdcdba993112",
            "message": "These links are valid only upto 15 mins. Incase the links expire, you may create a new request.",
            "output": "https://storage.googleapis.com/simulation_data_flint-cloud/simulations/simulation-simulations/examplenew1/output.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=authentication-bucket%40flint-cloud.iam.gserviceaccount.com%2F20210506%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210506T200813Z&X-Goog-Expires=1800&X-Goog-SignedHeaders=host&X-Goog-Signature=233e90633d613ca6bd830682ec5014e9b89e9e28b1995cb04249e158ff0677cec730f342b17dfe1e99f5713a4f45024c94ad589387a0b7f627f24d65ce813220904ac707e110520a05b4bdec0c15043586e2bf395e4d41139d289caa52cc2255d0b279e314f51f16992132155d1a917ae6bc224cc796ac4cb52b8eeffc966f5aa064b8f2a92fbb575987b66f81dcf994f8d156568738dc076459af10ff35b0a865d5a7fc99fe43a8bf965006c110f13204adfa1934af87764b90924310785d6cab9a8b71bde49dd105d6b5da962f995ebfbec08a7ec5606514c500ecf5218b23c82ed5fa2e8f9259afe1008d19f9c2466c687ab1bd0c924eeb0e09e098479e1c"
        }

    :Request FormData Object:

        * **title** (*string*) -- required title of simulation (this was set in /new).



GCBM: List simulations
======================

.. http:get:: /gcbm/list/

List all the GCBM simulations. Before creating a new simulation, it might be a good idea to check whether the simulation alreadys exists or not using this endpoint. You may also utilize the title of the simulation available here to download results for that specific simulation.

**Example request**:

    .. tabs::

        .. code-tab:: bash

            $ curl --location --request POST 'http://0.0.0.0:8080/gcbm/download' \
            --header 'Content-Type: application/json' \
            --header 'accept: application/json' \


    **Example response**:

    .. sourcecode:: json

        {
            "data": [
                "simulation-example",
                "simulation-examplenew",
                "simulation-examplenew1",
                "simulation-localrun"
            ],
            "message": "To create a new simulation, create a request at gcbm/new. To access the results of the existing simulations, create a request at gcbm/download."
        }