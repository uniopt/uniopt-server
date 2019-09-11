# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------------
# author     = "Sameh K. Mohamed"
# edit       = "Omar Farouk"
# copyright  = "Copyright 2019, The Project"
# credits    = ["Sameh K. Mohamed", "Omar Farouk"]
# license    = "MIT"
# version    = "0.0.0"
# maintainer = "Sameh K. Mohamed"
# email      = "sameh.kamaleldin@gmail.com", "omarfarouk.732@gmail.com"
# status     = "Development"
# -----------------------------------------------------------------------------------------
# Created by sameh at 2019-06-16
# Edited by Omar Farouk at 2019-06-26
# -----------------------------------------------------------------------------------------

from collections.abc import Iterable
from random import Random
import random
import numpy as np
from .util import GeneticHistory
from deap import base, algorithms, creator, tools


class GeneticAlgorithm:
    """ A class for a generic genetic algorithm
    """

    def __init__(self,
                 population_size=20,
                 nb_generations=20,
                 mutation_probability=0.3,
                 crossover_probability=0.5,
                 seed=1234,
                 verbose=True):
        """ Initialise a new instance of the `GeneticAlgorithm` class

        Parameters
        ----------
        population_size : int
            the population size
        nb_generations : int
            the number of generations
        mutation_size : int
            the number of genes to be mutated
        mutation_probability : float
            the probability of mutation for the chosen genes
        crossover_probability : float
            probability of crossover
        selection_size : int
            the size of natural selection group
        seed : int
            random seed
        verbose : int
            verbosity level

        Examples
        ----------
        >>> from libevolve.deap.ga import GeneticAlgorithm
        >>> ga = GeneticAlgorithm(population_size=10, nb_generations=15, mutation_probability=0.9)
        """

        self.population_size = population_size
        self.nb_generations = nb_generations
        self.mutation_probability = mutation_probability
        self.crossover_probability = crossover_probability
        self.crossover_func = tools.cxOnePoint
        self.selection_func = tools.selTournament
        self.sel_attr_dict = {'tournsize': 3}
        self.hof = None
        self.verbose = verbose
        self.seed = seed
        self.rs = Random(seed)
        self.parameters = None
        self.fitness_function = None
        self.objective_weights = None
        self.history = []

    def __mutate(self, individual, indpb):
        """ General Mutation for any Type of gene

        Parameters
        ----------
        individual : Iterable
            an individual in the population

        indpb : float between 0 and 1
            probability of mutation

        Returns
        -------
        Iterable
            The mutant Individual (Chromosome)

        """
        for i in range(len(individual)):
            if random.random() < indpb:
                individual[i] = self.parameters[i].get_rand_value()

        return individual,

    def __intialize_toolbox(self):
        """ Initialize The Toolbox for the GA

        Returns
        -------
        ToolBox
            for testing

        """
        creator.create("FitnessMax", base.Fitness, weights=self.objective_weights)
        creator.create("Individual", list, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()

        # Register Parameters to the GA
        for x in self.parameters:
            toolbox.register(x.name, x.get_rand_value)

        toolbox.register("individual", tools.initCycle, creator.Individual,
                         [toolbox.__getattribute__(x.name) for x in self.parameters], n=1)

        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.fitness_function)

        # Register the Cross-Over Function
        toolbox.register("mate", self.crossover_func)

        # Register the mutation Function
        toolbox.register("mutate", self.__mutate, indpb=self.mutation_probability)

        # Register the Selection Function
        toolbox.register("select", self.selection_func, **self.sel_attr_dict)

        # toolbox.decorate("mutate", self.history.decorator)

        self.toolbox = toolbox
        return toolbox

    def __intialize_stats(self):
        """
            Just initialize Stats for the GA

        Returns
        ----------
            stats
        """
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("max", np.max)

        self.stats = stats
        return stats

    def __gen_population(self):
        """
        initialize Population
        """
        his = []
        self.population = self.toolbox.population(n=self.population_size)
        print(type(self.population[0]))
        for x in self.population:
            his.append(list(x))
        self.history.append(his)

    def __intialize(self):
        """ Initialize toolbox , stats and population for the GA

        """
        self.__intialize_toolbox()
        self.hof = tools.HallOfFame(maxsize=1)
        self.__intialize_stats()
        self.__gen_population()

    def gen_algorithm(self, population, toolbox, cxpb, ngen, mutpb, stats=None, halloffame=None, verbose=True):
        """ Perform genetic algorithm

        population : list
            a list of of deap.creator.Individual
        ngen : int
            number of generations
        toolbox : deap.toolbox
            the toolbox must be initialized before calling the function
        cxpb : float
            probability of crossover
        mutpb : float
            probability of mutation

        stats : deap.tools.Statistics
            A Statistics object that is updated inplace
        halloffame : deap.tools.HallOfFame
            A HallOfFame object that will contain the best individuals
        verbose : boolean
            A HallOfFame object that will contain the best individuals


        Returns
        -------
        list
            set of best parameter values
        list
            set of fitness function scores for the best parameters
        GeneticHistory
            history of the genetic evolution
        """
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

        # Begin the generational process
        for gen in range(1, ngen + 1):

            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < cxpb:

                    toolbox.mate(child1, child2)

                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < mutpb:
                    toolbox.mutate(mutant)
                del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Select the next generation population
            population[:] = offspring
            his = []
            for x in offspring:
                his.append(list(x))
            self.history.append(his)

            # Update the statistics with the new population
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                print(logbook.stream)

        return population, logbook

    def evolve(self, parameters, fitness_function, objective_weights, *args, **kwargs):
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
        self.fitness_function = fitness_function
        self.objective_weights = objective_weights

        self.__intialize()

        self.gen_algorithm(self.population, self.toolbox, cxpb=self.crossover_probability,
                           stats=self.stats, mutpb=self.mutation_probability,
                           ngen=self.nb_generations, halloffame=self.hof, verbose=self.verbose)

        best_ind = self.hof[0]
        best_value = self.fitness_function(best_ind)
        return best_value, best_ind, self.history


class Classic_GA(GeneticAlgorithm):

    def __init__(self,
                 population_size=20,
                 nb_generations=20,
                 mutation_probability=0.3,
                 crossover_probability=0.5,
                 seed=1234,
                 verbose=True):

        super().__init__(population_size,
                         nb_generations,
                         mutation_probability,
                         crossover_probability,
                         seed,
                         verbose)


class Tour_cxTwo_GA(GeneticAlgorithm):
    def __init__(self,
                 population_size=20,
                 nb_generations=20,
                 mutation_probability=0.3,
                 crossover_probability=0.5,
                 seed=1234,
                 verbose=True):

        super().__init__(population_size,
                         nb_generations,
                         mutation_probability,
                         crossover_probability,
                         seed,
                         verbose)

        # when you want to make new type of genetic algorithm, you just make changes here
        self.crossover_func = tools.cxTwoPoint
        self.selection_func = tools.selTournament
        self.sel_attr_dict = {'tournsize': 3}
