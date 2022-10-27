from flask import Flask
from flask_restful import Api
from Endpoints.gcbm_endpoints import disturbance, Run, title, classifier, miscellaneous

app = Flask(__name__)
api = Api()

api.add_resource(disturbance, "/gcbm/upload/disturbances")
api.add_resource(title, "/gcbm/create")
api.add_resource(classifier, "/gcbm/upload/classifies")
api.add_resource(miscellaneous, "/gcbm/upload/miscellaneous")
api.add_resource(Run, "/gcbm/run")


if __name__ == "__main__":
    app.run(debug=True)
