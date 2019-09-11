from EPinterface.EPHelper import EnergyPlusHelper
from flask_restful import Resource, Api
from flask import request, make_response, jsonify
import requests
import os

ep = None
modify_key, modify_name, modify_field, modify_min, modify_max, modify_step, output =  ([] for i in range(7))

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
        output_path = response['output_path'] if 'output_path' in response else os.path.dirname(idf_path)
        ep = EnergyPlusHelper(idf_path="%s" % idf_path,
                      output_path="%s/out" % output_path)
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
        global modify_key, modify_name, modify_field, modify_min, modify_max, modify_step, GA_params
        data = request.get_json()
        modify_key = data['modify_key']
        modify_name = data['modify_name']
        modify_field = data['modify_field']
        modify_min = data['modify_min']
        modify_max = data['modify_max']
        modify_step = data['modify_step']
        url = "http://127.0.0.1:5000/GA/createparams"
        data = {'modify_name': modify_name, 'modify_min': modify_min,
         'modify_max': modify_max, 'modify_step': modify_step}
        response = requests.post(url, json=data)

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

class EPSetOutput(Resource):
    """
    api controller of the path [/EP/objects/set_output]
    """
    def get(self):
        return make_response(jsonify("Should call with a POST request"), 405)
    def post(self):
        global output
        data = request.get_json()
        output = data['output']
        return make_response("", 200)

class EPGetOutput(Resource):
    """
    api controller of the path [/EP/objects/get_output]
    """
    def get(self):
        global ep, output
        if not output:
            return make_response("You cannot get output value before setting what to track via\
                [/EP/objects/set_output]",403)
        result = ep.get_output_var(output)
        result = {'result':result[0]}
        return make_response(jsonify(result), 200)

    def post(self):
        return make_response(jsonify("Should call with a GET request"), 405)

class EPSimulate(Resource):
    """
    api controller of the path [/EP/run]
    """
    def get(self):
        global ep
        ep.run_idf()
        return make_response("", 200)

    def post(self):
        return make_response(jsonify("Should call with a GET request"), 405)