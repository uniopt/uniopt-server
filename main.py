
from flask import Flask, make_response, jsonify
from flask.json import jsonify
from flask_restful import Resource, Api

import unioptapi

app = Flask(__name__)
api = Api(app)


class ApiRoot(Resource):
    """
    api controller of the path [/uniopt] which retrieves the api meta information
    """
    def get(self):
        root_data = {
            "name": "uniopt-api",
            "version": unioptapi.__version__
        }
        return make_response(jsonify(root_data), 200)


class ApiVer(Resource):
    """
    api controller of the path [/uniopt/api] which retrieves the api version
    """
    def get(self):
        return make_response(jsonify(unioptapi.__version__), 200)


api.add_resource(ApiRoot, '/uniopt')
api.add_resource(ApiVer, '/uniopt/api')


if __name__ == '__main__':
    app.run(debug=True)
