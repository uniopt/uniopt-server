import operator
import random
import numpy
from deap import base
from deap import creator
from deap import tools
from libevolve.common._base import *
from random import Random


class SwarmOptimization:
    """ A class for a Swarm Optimization Algorithm
    """
    def __init__(self,
                 population_size=20,
                 nb_generations=25,
                 seed=1234):

        self.population_size = population_size
        self.nb_generations = nb_generations
        self.parameters = None
        self.speed_ranges = None
        self.fitness_function = None
        self.population = None
        self.phi1 = 2.0
        self.phi2 = 2.0
        self.objective_weights = None
        self.toolbox = None
        self.best = None
        self.stats = None
        self.logbook = None
        self.history = []
        self.seed = seed
        self.rs = Random(seed)

    def __generate_particel(self):
        """
        Private method to generate new particle in the start of optimization to generate first population
        """

        p = [x.get_rand_value() for x in self.parameters]
        self.history.append(p)
        part = creator.Particle(p)
        part.speed = [random.uniform(Min, Max) for Min, Max in self.speed_ranges]
        part.speedranges = self.speed_ranges
        return part

    def __update_particle(self, part, best):
        """
        Update the particle for the next generation

        :param part: list: of params(part) which is wanted to be updated
        :param best: list: best particle
        """
        u1 = [random.uniform(0, self.phi1) for _ in range(len(part))]
        u2 = [random.uniform(0, self.phi2) for _ in range(len(part))]
        v_u1 = map(operator.mul, u1, map(operator.sub, part.best, part))
        v_u2 = map(operator.mul, u2, map(operator.sub, best, part))

        part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))

        part[:] = list(map(operator.add, part, part.speed))

        for i, p in enumerate(part):
            if p > self.parameters[i].get_max_value():
                part[i] = self.parameters[i].get_max_value()
            elif p < self.parameters[i].get_min_value():
                part[i] = self.parameters[i].get_min_value()

        self.history.append(list(part))

    def __intialize_toolbox(self):
        """
        Toolbox Initialization
        """
        creator.create("FitnessMax", base.Fitness, weights=self.objective_weights)
        creator.create("Particle", list, fitness=creator.FitnessMax, speed=list,
                       speedranges=list, best=None)

        toolbox = base.Toolbox()
        toolbox.register("particle", self.__generate_particel)
        toolbox.register("population", tools.initRepeat, list, toolbox.particle)
        toolbox.register("update", self.__update_particle)
        toolbox.register("evaluate", self.fitness_function)

        self.toolbox = toolbox

    def __intialize_stats(self):
        """
            Just initialize Stats for the Swarm

        """
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)
        self.stats = stats

        logbook = tools.Logbook()
        logbook.header = ["gen", "evals"] + stats.fields
        self.logbook = logbook

    def __generate_population(self):
        """
            initialize Population
        """
        self.population = self.toolbox.population(n=self.population_size)

    def __intialize(self):
        """ Initialize toolbox , stats and population for the GA

        """

        self.__intialize_toolbox()
        self.__intialize_stats()
        self.__generate_population()

    def __pso_algorithm(self):
        """
        Particle Swarm optimization
        """
        self.best = None
        for g in range(self.nb_generations):
            for part in self.population:
                part.fitness.values = self.toolbox.evaluate(part)
                if not part.best or part.best.fitness < part.fitness:
                    part.best = creator.Particle(part)
                    part.best.fitness.values = part.fitness.values
                if not self.best or self.best.fitness < part.fitness:
                    self.best = creator.Particle(part)
                    self.best.fitness.values = part.fitness.values
            for part in self.population:
                self.toolbox.update(part, self.best)

            # Gather all the fitnesses in one list and print the stats
            self.logbook.record(gen=g, evals=len(self.population), **self.stats.compile(self.population))
            print(self.logbook.stream)

        return self.best, self.fitness_function(self.best), self.history

    def evolve(self, parameters, speedranges, fitness_function, objective_weights, *args, **kwargs):
        """ Perform evolution on the specified parameters and objective function

        parameters : list
            the set of evolutionary learning parameters
        fitness_function : function
            the fitness function. Expects named parameters that are equal or subset of the input parameters with the
            same names as specified in the input parameters. Must return an iterable.
        objective_weights : list
            the assigned weights to the fitness function output objective values. Positive values denote maximisation
            objective while negative values represent minimisation objective of the corresponding objective output.
        args : list
            other un named arguments
        kwargs : dict
            other named arguments

        Returns
        -------
        list
            set of best parameter values
        list
            set of fitness function scores for the best parameters
        GeneticHistory
            history of the genetic evolution
        """

        self.parameters = parameters
        self.speed_ranges = speedranges
        self.fitness_function = fitness_function
        self.objective_weights = objective_weights

        self.__intialize()
        self.__pso_algorithm()

        return self.fitness_function(self.best), self.best, self.history
