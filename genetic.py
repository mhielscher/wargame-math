#! /usr/bin/env python

"""
Very simple demo in which organisms try to minimise
the output value of a function
"""

from pygene.gene import FloatGene, FloatGeneMax
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
import time

from weapons import *

# Thoroughly seed the randomizer
if __name__ == "__main__":
    import random
    random.seed()
    f = open("/dev/urandom", "rb")
    rnd_str = f.read(8)
    random.seed(rnd_str)

def print_points(error, coef, fitness):
    print "Coefficients: %s" % (coef)
    total_diff = 0
    total_abs_diff = 0
    for name, data, target in weapons_data:
        fitn = fitness(data, coef, target)
        diff = target - fitn
        total_diff += diff
        total_abs_diff += abs(diff)
        print "%s: %f calc pts vs. %f target pts (%f delta)" % (name, fitn, target, diff)
    print "Max delta from target: %f" % (error)
    print "Mean difference: %f" % (total_diff/len(weapons_data))
    print "Mean abs difference: %f" % (total_abs_diff/len(weapon_data))

class CoefficientGene(FloatGene):
    """
    Gene which represents a coefficient for each term
    """
    # genes get randomly generated within this range
    randMin = -10.0
    randMax = 10.0
    
    # probability of mutation
    mutProb = 0.15
    
    # degree of mutation
    mutAmt = 0.2

class StatsSolver(Organism):
    """
    Implements the organism which tries
    to solve a quadratic equation
    """
    genome = {str(i): CoefficientGene for i in xrange(weapon_data_len)}
    
    def score(self, data, coefficients):
        equation = zip(data, coefficients)
        total = 0
        for term in equation:
            total += term[0] * term[1]
        return total

    def individual_fitness(self, data, coefficients, target):
        fitness_threshold = 0.25
        offset = abs(self.score(data, coefficients) - target)
        if offset > fitness_threshold:
            offset *= offset+(1-fitness_threshold)
        return offset

    def fitness(self):
        coefficients = [self[str(i)] for i in xrange(weapon_data_len)]
        
        total_fitness = 0
        for name, data, target in weapons_data:
            total_fitness = max(self.individual_fitness(data, coefficients, target), total_fitness)
        return total_fitness

    def __repr__(self):
        return "<fitness=%f>" % (
            self.get_fitness())


class QPopulation(Population):

    species = StatsSolver
    initPopulation = 2
    
    # cull to this many children after each generation
    childCull = 5

    # number of children to create after each generation
    childCount = 50


# create a new population, with randomly created members

pop = QPopulation()


# now a func to run the population
def main():
    target_fitness = 1.0
    try:
        timer_start = time.time()
        generations = 0
        while time.time() - timer_start < 120:
            # execute a generation
            pop.gen()
            generations += 1

            # and dump it out
            #print [("%.2f %.2f" % (o['x1'], o['x2'])) for o in pop.organisms]
            best = pop.organisms[0]
            print "fitness=%f" % (best.get_fitness())
            if best.get_fitness() < target_fitness:
                break

    except KeyboardInterrupt:
        pass
    print "Executed", generations, "generations"
    
    coefficients = [best[str(i)] for i in xrange(weapon_data_len)]
    print_points(best.get_fitness(), coefficients, best.individual_fitness)


if __name__ == '__main__':
    main()


