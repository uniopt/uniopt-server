# -*- coding: utf-8 -*-
import copy
from abc import abstractmethod
import random

import numpy as np

from .util import GeneticHistory, normalise
from ..common import *


class GeneticAlgorithm:
    """ A class for a generic genetic algorithm
    """
    def __init__(self,
                 population_size=50,
                 nb_generations=20,
                 mutation_size=1,
                 mutation_probability=0.3,
                 crossover_probability=0.5,
                 selection_size=20,
                 seed=1234,
                 verbose=0):
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
        >>> from libevolve.ga import GeneticAlgorithm
        >>> ga = GeneticAlgorithm(population_size=10, nb_generations=15, mutation_size=1, mutation_probability=0.9)
        """
        self.selection_size = selection_size
        self.population_size = population_size
        self.nb_generations = nb_generations
        self.mutation_size = mutation_size
        self.mutation_probability = mutation_probability
        self.crossover_probability = crossover_probability

        self.verbose = verbose
        self.seed = seed
        self.rs = random.Random(seed)
        self.parameters = None
        self.fitness_function = None
        self.objective_weights = None
        self.history = GeneticHistory()
    @abstractmethod
    def _mutate(self,population,size):
        """
        :param population:
        :returns: A list of varied individuals that have had changes in there genes .
        """

        offsprings = population
        for ind in offsprings:
            for i in range(1,len(ind)):
                if random.random()<self.mutation_probability:
                    ind[i] =self.parameters[i].get_rand_value()


        return offsprings
    @abstractmethod
    def _crossover(self, population):
        """ The Crossover operator is analogous to reproduction and biological crossover.
            In this more than one parent is selected and one or more off-springs are produced using the genetic material of the parents.
            Crossover is usually applied in a GA with a high probability – pc
        :param population

        the current generation parents

        :return offsprings

        the offsprings of the current generation
        """

        size = len(population)
        ind = population[0]
        for i in range(1,size,2):
            if random.random()<self.crossover_probability:
                index_1 = random.randint(0,len(ind)-1)
                population[i - 1][index_1:], population[i][index_1:] = population[i][index_1:], population[i - 1][
                                                                                                index_1:]



    @abstractmethod
    def natural_selection(self, population,*args, **kwargs):
        """ Perform genetic natural selection

        population : list
            list of individuals
        fitness_fitness_scores : list
            list of fitness scores lists
        args : list
            other un named arguments
        kwargs : dict
            other named arguments

        Returns
        -------
        list
            list of chosen individuals
        """

        k = self.selection_size
        population.sort(reverse=True)
        population =  population[:k]
        population = [copy.copy(ind) for ind in population]
        return population

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

        Examples
        ----------
        >>> from libevolve.ga import GeneticAlgorithm
        >>> from libevolve.common import *
        >>> ga = GeneticAlgorithm(population_size=10, nb_generations=15, mutation_size=1, mutation_probability=0.9)
        >>> best_solution, best_score, history = ga.evolve()
        """
        best_solution, best_score = None, 0.0
        self.parameters = parameters
        nb_params = len(parameters)
        nb_objectives = len(objective_weights)
        param_names = [p.name for p in parameters]
        population = []
        self.objective_weights = objective_weights

        # generate initial population
        for _ in range(self.population_size):
            ind = Individual(parameters, seed=self.rs.randint(0, 9999999999))
            population.append(ind)

        current_generation = population

        current_generation_fitness = [[] for _ in range(nb_objectives)]

        for ind in current_generation:
            dict_of_params= { chr(ord('a')+i) : ind[i] for i in range(1, len(ind) ) }
            ind_fitness = self.objective_weights[0]*fitness_function(**dict_of_params)
            ind[0] = ind_fitness

        for generation_idx in range(self.nb_generations):
            """
            select
            """
            offsprings =self.natural_selection(current_generation)
            """
            cross over
            """
            self._crossover(offsprings)
            """
            mutate
            """
            size = random.randint(0,len(offsprings))

            offsprings = self._mutate(population,size)

            current_generation = offsprings


            best_solution = current_generation[0]
            
            for ind in current_generation:
                dict_of_params= { chr(ord('a')+i) : ind[i] for i in range(1, len(ind) ) }
                ind_fitness = self.objective_weights[0]*fitness_function(**dict_of_params)
                ind[0]= ind_fitness
        return best_solution

class NSGA_II(GeneticAlgorithm):
    """
        A class of generic NSGA-II genetic algorithm
    """
    def __init__(self,population_size=50,
                 nb_generations=20,
                 mutation_size=1,
                 mutation_probability=0.3,
                 crossover_probability=0.5,
                 selection_size=20,
                 seed=9999999999,
                 verbose=0):
        """
    Initialise a new instance of the `NSGA_II` class

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
        >>> from libevolve.ga import *
        >>> ga = NSGA_II(population_size=10, nb_generations=15, mutation_size=1, mutation_probability=0.9)

        """

        super().__init__(population_size=population_size,
                 nb_generations=nb_generations,
                 mutation_size=mutation_size,
                 mutation_probability=mutation_probability,
                 crossover_probability=crossover_probability,
                 selection_size=selection_size,
                 seed=seed,
                 verbose=verbose)
    def evolve(self, parameters, fitness_function, objective_weights,tournament_size=5,k=5, *args, **kwargs):
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

        Examples
        ----------
        >>> from libevolve.ga import GeneticAlgorithm
        >>> from libevolve.common import *
        >>> ga = NSGA_II(population_size=10, nb_generations=15, mutation_size=1, mutation_probability=0.9)
        >>> best_solution, best_score, history = ga.evolve()
        """
        best_solution, best_score = None, 0.0
        self.parameters = parameters
        self.fitness_function = fitness_function
        self.objective_weights = objective_weights
        nb_params = len(parameters)
        nb_objectives = len(objective_weights)
        param_names = [p.name for p in parameters]
        population = []

        # generate initial population
        for _ in range(self.population_size):
            ind = Individual(parameters, seed=self.rs.randint(0, 9999999999))
            population.append(ind)

        current_generation = population

        current_generation_fitness = [[] for _ in range(nb_objectives)]
        offsprings = self._fast_non_dominated_sort(current_generation)
        current_generation= self._crowding_distance(offsprings)

        for generation_idx in range(self.nb_generations):
            """
                Select Parents by Rank and Distance and Sort by rank and Distance 
                functions discriminate members of the population 
                first by rank (order of dominated precedence of the front to which the solution belongs) 
                and then distance within the front 
            """

            """
            select
            """
            parents = self.natural_selection(current_generation,tournament_size,k)

            while(len(parents)<self.population_size):
                """
                cross over
                """
                parents = parents+ self._crossover(parents)
                """
                mutate
                """
                size = random.randint(0,len(parents))

                parents = parents + self._mutate(population,size)

            current_generation = current_generation + parents
            """
            Fast Non Dominated Sort
            """

            offsprings = self._fast_non_dominated_sort(current_generation)
            """
            Crowding Distance 
            """

            offsprings = self._crowding_distance(offsprings)

            offsprings.sort()

            current_generation = offsprings[0:self.population_size]

            best_solution = current_generation[0]

        return best_solution, best_score, self.history

    def _crowding_distance(self,front):
        """
        This function calculates the average distance between members of each front on the front itself
        Parameters
        ----------
        :front list of individals with their rank values

        Returns
        -------
        all individuals with their crowding distance
        """
        distance = [0 for i in range(0, len(front))]
        size = len(self.fitness_function)+2
        for obj_fun in range(2,size):
            front = np.array(front)
            front_1 = np.sort(front[:,obj_fun])
            mn_value = front_1[0]
            mx_value = front_1[-1]
            front_1_index = np.argsort(np.array(front[:,obj_fun]))
            distance[0]=4444444444444444
            distance[len(front)-1]=4444444444444444
            for pos in range(1,len(front_1)-1):
                if((front_1[pos + 1] - front_1[pos - 1])==0 and (mx_value - mn_value)==0):
                    distance[pos]+=0
                else:
                    distance[pos] = distance[pos] + (front_1[pos + 1] - front_1[pos - 1]) / (mx_value-mn_value)

        re_sort_order = np.argsort(front_1_index)
        for index in re_sort_order:
            if(index is not np.NaN):
                front[index,1] = distance[index]

        front = [list(ind) for ind in front]
        return front

    def _dominant(self,ind1,ind2):
        """
        This function determine which individual dominant the other.
        Parameters
        ----------
        ind1
        ind2

        Returns
        -------
        if the first individual dominat the second one or not
        """
        for obj_score in range(2,2+len(self.fitness_function)):
            if(ind1[obj_score]>=ind2[obj_score]):
                continue
            else: return False
        return True

    def _fast_non_dominated_sort(self, population):
        """
        The function orders the population into a hierarchy of non-dominated Pareto fronts.
        Parameters
        ----------
        population

        Returns
        -------

        """
        population = self.Evaulate(population,self.fitness_function)
        Dominent = {tuple(ind):[] for ind in population}
        front = [[]]
        Dominent_count = {tuple(ind):0 for ind in population}
        rank = {tuple(ind): -1 for ind in population}

        for ind_1 in range(0, len(population)):
            Dominent[tuple(population[ind_1])] = []
            Dominent_count[tuple(population[ind_1])] = 0
            for ind_2 in range(0, len(population)):
                if (self._dominant(population[ind_1],population[ind_2])):
                    if population[ind_2] not in Dominent[tuple(population[ind_1])]:
                        Dominent[tuple(population[ind_1])].append(population[ind_2])
                else:
                    Dominent_count[tuple(population[ind_1])] = Dominent_count[tuple(population[ind_1])] + 1
            if Dominent_count[tuple(population[ind_1])] == 0:
                rank[tuple(population[ind_1])] = 0
                if population[ind_1] not in front[0]:
                    front[0].append(population[ind_1])

        itre = 0
        while (front[itre] != []):
            Q = []
            for p in front[itre]:
                for q in Dominent[tuple(p)]:
                    Dominent_count[tuple(q)] = Dominent_count[tuple(q)] - 1
                    if (Dominent_count[tuple(q)] == 0):
                        rank[tuple(q)] = itre + 1
                        if q not in Q:
                            Q.append(q)

            itre = itre + 1
            front.append(Q)
        del front[len(front) - 1]
        population = []
        for front_i in front:
            for ind in front_i:
                ind[0] = rank[tuple(ind)]
                population.append(ind)
        return population

    def Evaulate(self, population,fitness_function):
        """
        This function computes the the fitness scores for each individual in the population
        Parameters
        ----------
        population
        fitness_function

        Returns
        -------

        """
        for ind in population:
            iter = 2
            for obj_fn in fitness_function:
                size = 2+len(self.fitness_function)
                dict_of_params = {chr(ord('a') + i): ind[i] for i in range(size, len(ind))}
                ind[iter]=obj_fn(**dict_of_params)*self.objective_weights[iter]
                iter +=1
        return population
    def natural_selection(self,individuals,tournsize,k):
        """Select the best individual among *tournsize* randomly chosen
            individuals, *k* times. The list returned contains
            references to the input *individuals*.

            :param individuals: A list of individuals to select from.

            :param k: The number of individuals to select.

            :param tournsize: The number of individuals participating in each tournament.

            :returns: A list of selected individuals.
            This function uses the :func:`~random.choice` function from the python base

            :mod:`random` module.
            """
        chosen = []
        for i in range(k):
            aspirants = [random.choice(individuals) for i in range(tournsize)]
            aspirants.sort(reverse=True)
            for ind in aspirants:
                chosen.append(ind)
        return chosen

    def _mutate(self,population,size):
        """
                :param population:
                :returns: A list of varied individuals that have had changes in there genes .
        """
        offsprings = population
        for ind in offsprings:
            if random.random() < self.mutation_probability:
                index = random.randint(3,len(ind)-1)
                ind[index] = self.parameters[index].get_rand_value()
        return offsprings

    def _crossover(self, population):
        """ The Crossover operator is analogous to reproduction and biological crossover.
            In this more than one parent is selected and one or more off-springs are produced using the genetic material of the parents.
            Crossover is usually applied in a GA with a high probability – pc
        :param population

        the current generation parents

        :return offsprings

        the offsprings of the current generation
        """
        size = len(population)
        ind = population[0]
        for i in range(1, size, 2):
            if random.random() < self.crossover_probability:
                index_1 = random.randint(3, len(ind)-1)
                population[i - 1][index_1:], population[i][index_1:] = population[i][index_1:], population[i - 1][index_1:]
        return population