#! /usr/bin/env python

"""
Very simple demo in which organisms try to minimise
the output value of a function
"""

from pygene.gene import FloatGene, FloatGeneMax
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
import time
import sys

from weapons import *

# Thoroughly seed the randomizer
if __name__ == "__main__":
    import random
    random.seed()
    f = open("/dev/urandom", "rb")
    rnd_str = f.read(8)
    random.seed(rnd_str)

def print_points(error, values, score, outfile=sys.stdout):
    print >>outfile, "Values: %s" % (values)
    total_diff = 0
    total_abs_diff = 0
    for name, data, target in weapons_data:
        fitn = score(data, values[:len(values)/2], values[len(values)/2:])
        diff = target - fitn
        total_diff += diff
        total_abs_diff += abs(diff)
        print >>outfile, "%s: %.3f calc pts vs. %.3f target pts (%.3f delta)" % (name, fitn, target, diff)
    print >>outfile, "Max delta from target: %f" % (error)
    print >>outfile, "Mean difference: %f" % (total_diff/len(weapons_data))
    print >>outfile, "Mean abs difference: %f" % (total_abs_diff/len(weapons_data))

class CoefficientGene(FloatGene):
    """
    Gene which represents a coefficient for each term
    """
    # genes get randomly generated within this range
    randMin = -25.0
    randMax = 25.0
    
    # probability of mutation
    mutProb = 0.2
    
    # degree of mutation
    mutAmt = 0.15

class ExponentGene(FloatGene):
    randMin = -6.0
    randMax = 4.0
    mutProb = 0.2
    mutAmt = 0.21

class LinearStatsSolver(Organism):
    genome = {str(i): t for i, t in enumerate([CoefficientGene]*weapon_data_len)}
    
    def score(self, data, coefficients):
        equation = zip(data, coefficients)
        total = 0
        for term in equation:
            total += term[0] * term[1]
        return total

    def individual_fitness(self, data, coefficients, target):
        fitness_threshold = 0.25
        offset = abs(self.score(data, coefficients) - target)
        #if offset > fitness_threshold:
        #    offset *= offset+(1-fitness_threshold)
        return offset

    def fitness(self):
        coefficients = [self[str(i)] for i in xrange(weapon_data_len)]
        
        total_fitness = 0
        for name, data, target in weapons_data:
            total_fitness = max(self.individual_fitness(data, coefficients, target), total_fitness)
        #total_fitness = max(self.individual_fitness(data, coefficients, target) for name, data, target in weapons_data)
        return total_fitness

    def __repr__(self):
        return "<fitness=%f, coefficients=%s>" % (
            self.get_fitness(), [self[str(i)] for i in xrange(weapon_data_len)])

class PolynomialStatsSolver(Organism):
    # Combine two dicts, essentially [...] + [...] for dicts
    genome = {str(i): t for i, t in enumerate([CoefficientGene]*weapon_data_len + [ExponentGene]*weapon_data_len)}
    
    def score(self, data, coefficients, exponents):
        equation = zip(data, coefficients, exponents)
        total = 0
        for term in equation:
            try:
                total += term[1] * (term[0]**term[2])
            except ValueError: #invalid exponent
                pass
            except ZeroDivisionError:
                pass
        return total

    def individual_fitness(self, data, coefficients, exponents, target):
        fitness_threshold = 0.25
        offset = abs(self.score(data, coefficients, exponents) - target)
        if offset > fitness_threshold:
            offset *= offset+(1-fitness_threshold)
        return offset

    def fitness(self):
        coefficients = [self[str(i)] for i in xrange(weapon_data_len)]
        exponents = [self[str(i+weapon_data_len)] for i in xrange(weapon_data_len)]
        
        total_fitness = 0
        for name, data, target in weapons_data:
            total_fitness = max(self.individual_fitness(data, coefficients, exponents, target), total_fitness)
        return total_fitness

    def __repr__(self):
        return "<fitness=%f, coefficients=%s, exponents=%s>" % (
            self.get_fitness(), [self[str(i)] for i in xrange(weapon_data_len)], [self[str(i+weapon_data_len)] for i in xrange(weapon_data_len)])

class LinearPopulation(Population):

    species = LinearStatsSolver
    initPopulation = 5
    
    # cull to this many children after each generation
    childCull = 5

    # number of children to create after each generation
    childCount = 100
    
    numNewOrganisms = 5

class PolynomialPopulation(Population):

    species = PolynomialStatsSolver
    initPopulation = 4
    
    # cull to this many children after each generation
    childCull = 6

    # number of children to create after each generation
    childCount = 100
    
    numNewOrganisms = 2


# create a new population, with randomly created members

pop = PolynomialPopulation()


# now a func to run the population
def main():
    target_fitness = 0.1
    time_limit = 0
    try:
        timer_start = time.time()
        generations = 0
        while time_limit <= 0 or (time.time() - timer_start < time_limit):
            # execute a generation
            pop.gen()
            generations += 1

            # and dump it out
            #print [("%.2f %.2f" % (o['x1'], o['x2'])) for o in pop.organisms]
            best = pop.organisms[0]
            print "Generation %d, Fitness=%.4f" % (generations, best.get_fitness())
            if best.get_fitness() < target_fitness:
                break

    except KeyboardInterrupt:
        pass
    print "Executed %d generations (%f generations/sec)" % (generations, float(generations)/(time.time()-timer_start))
    
    values = [best[name] for name in best.genome]
    filename = "gen-%s.out" % (repr(timer_start)[-4:])
    print_points(best.get_fitness(), values, best.score, open(filename, 'w'))

if __name__ == '__main__':
    main()


