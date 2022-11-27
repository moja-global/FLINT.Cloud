from flask import Flask
from flask_restful import Api
from Helpers.routes import endpoints


app = Flask(__name__)
api = Api()


endpoints(api=api)

if __name__ == "__main__":
    app.run(debug=True)
