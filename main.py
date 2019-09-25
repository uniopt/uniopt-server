
from flask import Flask, request, make_response, jsonify
from flask.json import jsonify
from flask_restful import Resource, Api
import unioptapi
# from EvoGA_API import *
from deapAPI import *
from energyplus import *
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
api.add_resource(EPInit, '/EP/init')
api.add_resource(EPStart, '/EP/start')
api.add_resource(EPGetObjects, '/EP/objects/all')
api.add_resource(EPSetModifyObjects, '/EP/objects/set_modify')
api.add_resource(EPModifyObjects, '/EP/objects/modify')
api.add_resource(EPSetOutput, '/EP/objects/set_output')
api.add_resource(EPGetOutput, '/EP/objects/get_output')
api.add_resource(EPSimulate, '/EP/run')
api.add_resource(CreateParams, '/GA/createparams')
api.add_resource(InitGA, '/GA/initialize')
api.add_resource(EvolveGA, '/GA/evolve')

if __name__ == '__main__':
    app.run(debug=True)
