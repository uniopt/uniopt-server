from flask import Flask, request, make_response, jsonify
from flask.json import jsonify, JSONEncoder
from flask_restful import Resource, Api
import unioptapi
import requests
from EPinterface.EPHelper import EnergyPlusHelper

from EvoGA.common._base import *
from EvoGA.ga._base import GeneticAlgorithm,NSGA_II

GA_params = None
GA = None
NSGAII = None
url_modify ="http://127.0.0.1:5000/EP/objects/modify"
url_simulate = "http://127.0.0.1:5000/EP/run"
url_output = "http://127.0.0.1:5000/EP/objects/get_output"

class CreateParams(Resource):
    def get(self):
        return make_response(jsonify("Should call with a POST request with the array of\
        objects in a json "), 405)

    def post(self):
        global GA_params
        response = request.get_json()
        modify_name = response['modify_name']
        modify_min = response['modify_min']
        modify_max = response['modify_max']
        modify_step = response['modify_step']
        zi = zip(modify_name, modify_min, modify_max, modify_step)
        params = []
        p = EvoFloatParam(name="Obj1")
        params.append(p)
        for name, min, max, step in zi:
            if step == 0:
                p = EvoIntParam(name, min, max)
            else:
                p = EvoFloatParam(name, min, max, step)
            params.append(p)
        GA_params = params
        return make_response("", 200)


class InitGA(Resource):

    def post(self):
        global GA

        data = request.get_json()
        population_size = data['population_size']
        nb_generations = data['nb_generations']

        GA = GeneticAlgorithm(population_size=population_size, nb_generations=nb_generations, verbose=False)
        return make_response("", 200)


class EvolveGA(Resource):

    def fit(self, **args):
        global url_modify, url_simulate, url_output
        ind = list(args.values())
        data = {'modify_val':ind }
        url = url_modify
        requests.post(url, json=data)

        url = url_simulate
        requests.get(url)

        url = url_output
        reqBack = requests.get(url)
        values = reqBack.json()['result']

        res = sum(values)/len(values)
        return res

    def post(self):
        data = request.get_json()
        objective_weights = data['objective_weights']

        global GA, GA_params
        best_solution = GA.evolve(parameters=GA_params, fitness_function=self.fit, objective_weights=objective_weights)

        dict = {'value': best_solution[0], 'ind': best_solution[1:]}
        return make_response(jsonify(dict), 200)
