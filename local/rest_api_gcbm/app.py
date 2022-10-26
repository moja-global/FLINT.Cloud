from flask_restful import Api
from gcbm_simulation.routes import initialize_routes
from flask import Flask
import os

app = Flask(__name__)
api = Api(app)

initialize_routes(api)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

