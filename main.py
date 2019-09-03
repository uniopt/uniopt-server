
from flask import Flask, request, make_response, jsonify
from flask.json import jsonify
from flask_restful import Resource, Api

import unioptapi

from EPinterface.EPHelper import EnergyPlusHelper
import os
app = Flask(__name__)
api = Api(app)
ep = None
modify_key, modify_name, modify_field, modify_min, modify_max, modify_step =  ([] for i in range(6))


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

class EPInit(Resource):
    """
    api controller of the path [/EP/init] which gets the idf stucture into the memory

    request should be POST only with a body JSON 'idf_path' containing a valid path for an
    idf file

    """
    def get(self):
        return make_response(jsonify("Should call with a POST request with the idf\
 path in the JSON body"), 405)
    def post(self):
        global ep
        response = request.get_json()
        idf_path = response['idf_path']
        ep = EnergyPlusHelper(idf_path="%s" % idf_path,
                      output_path="%s/out" % os.path.dirname(idf_path))
        return make_response("", 200)

class EPGetObjects(Resource):
    """
    api controller of the path [/EP/objects/all] which retrieves the objects of the idf file

    """

    def get(self):
        global ep
        objects = ep.get_all_objects()
        return make_response(jsonify(objects), 200)

class EPSetModifyObjects(Resource):
    """
    api controller of the path [/EP/objects/set_modify] which retrieves the objects of the idf file
    request should be in POST only objects in a json index key and name in 'modify_key'
    and 'modify_name' and fields in 'modify_field' and Min, Max 'modify_min' 'modify_max' 
    in arrays with respect to the order.
    """
    def get(self):
        return make_response(jsonify("Should call with a POST request with the array of\
 objects in a json index key and name in 'modify_key' and 'modify_name' and fields in\
 'modify_field' and Min, Max in arrays"), 405)
    def post(self):
        global modify_key, modify_name, modify_field, modify_min, modify_max, modify_step
        response = request.get_json()
        modify_key = response['modify_key']
        modify_name = response['modify_name']
        modify_field = response['modify_field']
        modify_min = response['modify_min']
        modify_max = response['modify_max']
        modify_step = response['modify_step']
        #TODO: send those to the GA algorithm
        return make_response("", 200)

class EPModifyObjects(Resource):
    """
    api controller of the path [/EP/objects/modify] which edits the objects of the idf file
    request should be POST only with a JSON body of arrays key and name in 'modify_key' and
    'modify_name' and fields names in 'modify_field' and values to edit in  'modify_val'
    with respect to the order
    """
    def get(self):
        return make_response(jsonify("Should call with a POST request with the array of\
 objects in a json body key and name in 'modify_key' and 'modify_name' and fields in 'modify_field'\
 and values to add 'modify_val' with respect to the order"), 405)
    def post(self):
        global ep
        global modify_key, modify_name, modify_field
        if not modify_key:
            return make_response("You cannot modify objects before setting what to modify via\
                [/EP/objects/set_modify]",403)
        response = request.get_json()
        modify_val = response['modify_val']
        ep.set_field_val(modify_key, modify_name, modify_field, modify_val)
        return make_response("", 200)

api.add_resource(ApiRoot, '/uniopt')
api.add_resource(ApiVer, '/uniopt/api')
api.add_resource(EPInit, '/EP/init')
api.add_resource(EPGetObjects, '/EP/objects/all')
api.add_resource(EPSetModifyObjects, '/EP/objects/set_modify')
api.add_resource(EPModifyObjects, '/EP/objects/modify')

if __name__ == '__main__':
    app.run(debug=True)
