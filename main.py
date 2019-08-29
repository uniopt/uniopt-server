
from flask import Flask, make_response, jsonify
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse

import unioptapi

from EPinterface.EPHelper import EnergyPlusHelper
import os
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()


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

class EPGetObjects(Resource):
    """
    api controller of the path [/EP/objects] which retrieves the objects of the idf file

    request should be POST only with a body variable idf_path containing a valid path for an
    idf file
    """
    def get(self):
        return make_response(jsonify("Should call with a POST request with the idf\
 path in the body"), 405)
    def post(self):
        parser.add_argument('idf_path', type=str)
        args = parser.parse_args()
        idf_path = args['idf_path']
        ep = EnergyPlusHelper(idf_path="%s" % idf_path,
                      output_path="%s/out" % os.path.dirname(idf_path))
        objects = ep.get_all_objects()
        return make_response(jsonify(objects), 200)

api.add_resource(ApiRoot, '/uniopt')
api.add_resource(ApiVer, '/uniopt/api')
api.add_resource(EPGetObjects, '/EP/objects')

if __name__ == '__main__':
    app.run(debug=True)
