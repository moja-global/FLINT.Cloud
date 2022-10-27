from flask_restful import Resource
import os
from threading import Thread
from Helpers.preprocess import (
    DisturbanceConfig,
    launch_run,
    ClassifierConfig,
    MiscellaneousConfig,
)
from Helpers.for_requests import (
    title_query,
    miscellaneous_query,
    disturbance_query,
    classifier_query,
)


class disturbance(Resource):
    def post(self):
        title = title_query().get("title") or "simulation"
        input_dir = f"{os.getcwd()}/input/{title}"
        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")
        if not os.path.exists(f"{input_dir}/disturbances"):
            os.makedirs(f"{input_dir}/disturbances")

        # store disturbances file in a new folder
        disturbances = disturbance_query()
        if not disturbances:
            return {"error": "Missing disturbances file"}, 400
        for file in disturbances.get("disturbances"):
            file.save(f"{input_dir}/disturbances/{file.filename}")
            try:
                disturb = DisturbanceConfig(
                    input_dir, file.filename, disturbances.get("attributes")
                )
                disturb()
            except Exception as e:
                return e
        disturb.flatten_directory("disturbances")
        return {
            "data": "Disturbances file uploaded succesfully. Proceed to the next step."
        }


class classifier(Resource):
    def post(self):
        # Get the title from the payload
        title = title_query().get("title") or "simulation"

        # Check for project directory else create one
        input_dir = f"{os.getcwd()}/input/{title}"
        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")

        # input files follow a strict structure
        if not os.path.exists(f"{input_dir}/classifiers"):
            os.makedirs(f"{input_dir}/classifiers")

        # store disturbances file in a new folder
        classifiers = classifier_query()
        if not classifiers:
            return {"error": "Missing classifiers file"}, 400

        for file in classifiers.get("classifiers"):
            file.save(f"{input_dir}/classifiers/{file.filename}")
            try:
                classify = ClassifierConfig(
                    input_dir, file.filename, classifiers.get("attributes")
                )
                classify()
            except Exception as e:
                return e
        classify.flatten_directory("classifiers")
        return {
            "data": "Classifiers file uploaded succesfully. Proceed to the next step."
        }


class Database(Resource):
    def post(self):
        pass


class miscellaneous(Resource):
    def post(self):
        # Get the title from the payload
        title = title_query().get("title") or "simulation"

        # Check for project directory else create one
        input_dir = f"{os.getcwd()}/input/{title}"
        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")

        # input files follow a strict structure
        if not os.path.exists(f"{input_dir}/miscellaneous"):
            os.makedirs(f"{input_dir}/miscellaneous")

        # store miscellaneous file in a new folder
        mis = miscellaneous_query()
        if not mis:
            return {"error": "Missing classifiers file"}, 400

        for file in mis.get("miscellaneous"):
            file.save(f"{input_dir}/miscellaneous/{file.filename}")
            try:
                miscel = MiscellaneousConfig(
                    input_dir, file.filename, mis.get("attributes")
                )
                miscel()
            except Exception as e:
                return e
        miscel.flatten_directory("miscellaneous")
        return {
            "data": "Classifiers file uploaded succesfully. Proceed to the next step."
        }


class title(Resource):
    def post(self):
        # Default title = simulation
        title = title_query().get("title") or "simulation"
        # Sanitize title
        title = "".join(c for c in title if c.isalnum())
        # input_dir = f"{title}"
        input_dir = f"{os.getcwd()}/input/{title}"
        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")
            message = "New simulation started. Please move on to the next stage for uploading files at /gcbm/upload."
        else:
            message = "Simulation already exists. Please check the list of simulations present before proceeding with a new simulation at gcbm/list. You may also download the input and output files for this simulation at gcbm/download sending parameter title in the body."

        return {"data": message}, 200


class Run(Resource):
    """THIS ENDPOINT WILL BE ABLE TO RUN A SIMULATION
    GOAL IS TO EQUIP IT TO BE ABLE TO RUN MORE THAN ONE SIMULATIONS AT A TIME"""

    def post(self):
        title = title_query().get("title") or "simulation"

        # Sanitize title
        title = "".join(c for c in title if c.isalnum())
        input_dir = f"{os.getcwd()}/input/{title}"

        if not os.path.exists(f"{input_dir}"):
            os.makedirs(f"{input_dir}")

        thread = Thread(
            target=launch_run, kwargs={"title": title, "input_dir": input_dir}
        )
        thread.start()

        return {"status": "Run started"}, 200
