#!/usr/bin/python

import sys
import random
import signal
import simplejson

from weapons import *

def print_points(error, coef, fitness):
    print "Coefficients: %s" % (coef)
    total_diff = 0
    for name, data, target in weapons_data:
        fitn = fitness(data, coef, target)
        diff = target - fitn
        total_diff += diff
        print "%s: %f calc pts vs. %f target pts (%f delta)" % (name, fitn, target, diff)
    print "Max delta from target: %f" % (error)
    print "Mean difference: %f" % (total_diff/len(weapons_data))

class Linear:
    
    def score(self, data, coefficients):
        equation = zip(data, coefficients)
        total = 0
        for term in equation:
            total += term[0] * term[1]
        return total

    def individual_fitness(self, data, coefficients, target):
        offset = abs(self.score(data, coefficients) - target)
        if offset > 0.5:
            offset *= offset+0.5
        return max(0, offset-0.2);

    def fitness(self, coefficients):
        if len(coefficients) != data_len:
            print "Coefficients of wrong length: %d vs. %d" % (len(coefficients), data_len)
            print "Padding coefficients with 0's."
            coefficients += [0]*(len(data)-len(coefficients))
        
        total_fitness = 0
        for name, data, target in weapons_data:
            total_fitness += self.individual_fitness(data, coefficients, target)
        return total_fitness

    def twiddle(self, coefficients=None, tolerance=0.00001, minimum=0.75):
        if not coefficients:
            coef = [random.uniform(-1,1) for i in range(data_len)]
            print "Using random coefficients."
        else:
            coef = coefficients
            print "Using input coefficients."
        d_coef = [random.uniform(0,2) for i in range(data_len)]
        err = self.fitness(coef)
        best = (err, coef)
        print best[0]
        
        def sig_handler(signal, frame):
            print "Search interrupted."
            print_points(best[0], best[1], self.individual_fitness)
            sys.exit(0)
        signal.signal(signal.SIGINT, sig_handler)
        
        steps = 0
        prev_best_err = sys.maxint
        while abs(best[0] - prev_best_err) > tolerance or steps < 2000:
            prev_best_err = best[0]
            if not coefficients:
                coef = [random.uniform(-1,1) for i in range(data_len)]
            d_coef = [random.uniform(0,2) for i in range(data_len)]
            print "Redid d_coef"
            while sum(d_coef) > tolerance:
                for i in range(data_len):
                    coef[i] += d_coef[i]
                    err = self.fitness(coef)
                    if err < best[0]:
                        best = (err, coef)
                        d_coef[i] *= 1.1
                    else:
                        coef[i] -= 2*d_coef[i]
                        err = self.fitness(coef)
                        if err < best[0]:
                            best = (err, coef)
                            d_coef[i] *= 1.1
                        else:
                            coef[i] += d_coef[i]
                            d_coef[i] *= 0.9
                steps += 1
                if steps % 1000 == 0:
                    print "Twiddle #%d -> %f %f %f" % (steps, best[0], err, sum(d_coef))
        return coef
        
    def random_search(self, coef=None, minimum=1):
        if not coef:
            coef = [random.uniform(-1,1) for i in range(data_len)]
            print "Using random coefficients."
        else:
            print "Using input coefficients."
        err = self.fitness(coef)
        best = (err, coef)
        
        def sig_handler(signal, frame):
            print "Search interrupted."
            print_points(best[0], best[1], self.individual_fitness)
            sys.exit(0)
        signal.signal(signal.SIGINT, sig_handler)
        
        steps = 0
        while err > minimum:
            coef = [random.uniform(-1,1) for i in range(data_len)]
            err = self.fitness(coef)
            if err < best[0]:
                best = (err, coef)
            steps += 1
            if steps % 1000 == 0:
                print "Random search #%d -> %f %f" % (steps, best[0], err)
        return coef


class Nonlinear:
    def score(self, data, coefficients, exponents):
        equation = zip(data, coefficients, exponents)
        total = 0
        for term in equation:
            total += term[0] * (term[1] ** term[2])
        return total

    def individual_fitness(self, data, coefficients, exponents, target):
        offset = abs(score(data, coefficients, exponents) - target)
        if offset > 0.5:
            offset *= offset+0.5
        return max(0, offset-0.2);

    def fitness(self, coefficients, exponents):
        if len(coefficients) != data_len or len(exponents) != data_len:
            print "Coefficients/exponents of wrong length: %d/%d vs. %d" % (len(coefficients), len(exponents), data_len)
            return sys.maxint
        
        total_fitness = 0
        for name, data, target in weapons_data:
            total_fitness += individual_fitness(data, coefficients, exponents, target)
        return total_fitness

    def twiddle(self, coefficients=None, exponents=None, tolerance=0.00001, minimum=0.75):
        if not coefficients:
            coef = [random.uniform(-1,1) for i in range(data_len)]
            print "Using random coefficients."
        else:
            coef = coefficients
            print "Using input coefficients."
        if not exponents:
            exp = [random.uniform(-3,3) for i in range(data_len)]
            print "Using random exponents."
        else:
            exp = exponents
            print "Using input exponents."
        
        d_coef = [random.uniform(0,2) for i in range(data_len)]
        d_exp = [random.uniform(0,2) for i in range(data_len)]
        err = fitness(coef, exp)
        best = (err, coef, exp)
        print best[0]
        
        def sig_handler(signal, frame):
            print "Search interrupted."
            print "Exponents: %s" % (best[2])
            finish(best[1], self.individual_fitness)
            print_points(best[0], best[1], self.individual_fitness)
            sys.exit(0)
        signal.signal(signal.SIGINT, sig_handler)
        
        steps = 0
        prev_best_err = sys.maxint
        while abs(best[0] - prev_best_err) > tolerance or steps < 2000:
            prev_best_err = best[0]
            if not coefficients:
                coef = [random.uniform(-1,1) for i in range(data_len)]
            if not exponents:
                exp = [random.uniform(-1,1) for i in range(data_len)]
            d_coef = [random.uniform(0,2) for i in range(data_len)]
            d_exp = [random.uniform(0,2) for i in range(data_len)]
            print "Redid d_coef and d_exp"
            while sum(d_coef) > tolerance or sum(d_exp) > tolerance:
                for i in range(data_len):
                    coef[i] += d_coef[i]
                    exp[i] += d_exp[i]
                    err = fitness(coef, exp)
                    if err < best[0]:
                        best = (err, coef, exp)
                        d_coef[i] *= 1.1
                        d_exp[i] *= 1.1
                    else:
                        coef[i] -= 2*d_coef[i]
                        exp[i] -= 2*d_exp[i]
                        err = fitness(coef, exp)
                        if err < best[0]:
                            best = (err, coef, exp)
                            d_coef[i] *= 1.1
                            d_exp[i] *= 1.1
                        else:
                            coef[i] += d_coef[i]
                            exp[i] += d_exp[i]
                            d_coef[i] *= 0.9
                            d_exp[i] *= 0.9
                steps += 1
                if steps % 1000 == 0:
                    print "Twiddle #%d -> %f, %f, %f, %f" % (steps, best[0], err, sum(d_coef), sum(d_exp))
        return coef, exp
        
    def random_search(self, coefficients=None, exponents=None, minimum=0.75):
        if not coefficients:
            coef = [random.uniform(-1,1) for i in range(data_len)]
        if not exponents:
            exp = [random.uniform(-1,1) for i in range(data_len)]
            d_coef = [random.uniform(0,2) for i in range(data_len)]
            d_exp = [random.uniform(0,2) for i in range(data_len)]
        err = fitness(coef, exp)
        best = (err, coef, exp)
        
        def sig_handler(signal, frame):
            print "Search interrupted."
            print "Exponents: %s" % (best[2])
            print_points(best[0], best[1], self.individual_fitness)
            sys.exit(0)
        signal.signal(signal.SIGINT, sig_handler)
        
        steps = 0
        while err > minimum:
            coef = [random.uniform(-1,1) for i in range(data_len)]
            exp = [random.uniform(-3,3) for i in range(data_len)]
            err = fitness(coef, exp)
            if err < best[0]:
                best = (err, coef, exp)
            steps += 1
            if steps % 1000 == 0:
                print "Random search #%d -> %f, %f, %f" % (steps, best[0], err)
        return coef, exp

if __name__ == "__main__":
    random.seed()
    f = open("/dev/urandom", "rb")
    rnd_str = f.read(8)
    random.seed(rnd_str)
    
    model = Linear()
    #model = Nonlinear()
    
    if len(sys.argv) > 1:
        coefficients = simplejson.loads(sys.argv[1])
    else:
        coefficients = None
        coefficients = model.random_search()
    #print model.twiddle(coefficients)
    #print model.random_search(coefficients)
    print "----"
    print_points(model.fitness(coefficients), coefficients, model.individual_fitness)




"""
Random linear, 5 minutes from scratch:
Best error: 1.153050
Coefficients: [0.5573967178413275, -0.245967908358125, -0.5498362981799243, 0.971219241759482, -0.6724595722143523, 0.6594512486697741, -0.6259973964587973, 0.6766713036039234, -0.2062069243861, 0.8066423485417189, -0.6207985121745452, 0.8804098721542193, 0.6811375852260939, 0.12167040150749142, -0.9474549834639128, 0.6389920643475606, -0.5762399841545247, -0.1413104225882762, 0.9191116117589331, 0.030391981532440715, -0.6153529061465073, 0.19430763183594446, 0.7459851963018063, -0.08957719315672685, 0.11835981151444708, -0.7526501693014995, -0.8213585169794269, -0.073964425583531, 0.18450471442520877, -0.22594403758182424, -0.048186230020906606, 0.8463764185249936, 0.16222292410678762, 0.42143880034642267, 0.1493949754677597]

Twiddle linear, 5 minutes from scratch:
Best error: 
Coefficients: 

Twiddle linear, until stable, from above random:
Best error: 0.623580
Coefficients: [0.5573967317904399, -0.2425509211500769, -0.5498182717852683, 0.9712189967378271, -0.6724529951798608, 0.6594516143979489, -0.6259973966749308, 0.659157734135824, -0.15730887482201916, 0.7340226599614111, -0.6230659382574052, 0.8804528368579138, 0.681585475910673, 0.1216704013741801, -0.9474549834638912, 0.897729583474905, -0.5776899887825211, -0.14130897811334897, 0.9188198774285434, 0.030387173100934382, -0.615354281511834, 0.19430763183594427, 0.6176491916450153, -0.09068779579037269, 0.17196426131849146, -0.7953495865862832, -0.8629120123206672, -0.07377503324407185, 0.18450471442521144, -0.2259393114304324, -0.0498279504143418, 0.8462510495388115, 0.16192003664471633, 0.42138705381201497, 0.14938030176186612]

Twiddle linear, until stable, from ??:
Best error: 0.594056
Coefficients: [0.5579355009914552, -0.24299999777323053, -0.5469939825303045, 0.972826920709591, -0.6719999993256927, 0.6589999980423987, -0.6270000025676189, 0.6512513917218573, -0.15686220390873268, 0.7268119157798343, -0.6219996009469975, 0.8800343398043475, 0.6820000421075856, 0.12200003623963265, -0.9417000016362054, 1.002974360921362, -0.5779001797836978, -0.1423000023652457, 0.9189983092733596, 0.029999771680560654, -0.6176820601178153, 0.19400000000000323, 0.6175311203664036, -0.09046839211574283, 0.18805201842896546, -0.7932258992209338, -0.8631000048287678, -0.07299996618002744, 0.18499663813269468, -0.22200000161672268, -0.047422525481179846, 0.8449976346074635, 0.16000074123108904, 0.4196793548111906, 0.14899992943635765]


Twiddle linear, latest:
Best error: 0.592519
Coefficients: [0.5579003396685076, -0.24259983320387815, -0.5468966372366523, 0.9729635853151729, -0.6719999738867345, 0.6589999992550457, -0.6270000153886274, 0.6512999996509868, -0.15694624295101084, 0.7248897776326051, -0.6211665338266634, 0.8800181438535677, 0.6822000130754932, 0.12200008671992624, -0.9417000000000071, 0.8557892141597758, -0.5772907396009691, -0.14230000217475497, 0.9189999169366563, 0.02995869459919074, -0.6176999774135185, 0.1940000000000003, 0.617475954825495, -0.09046759388914836, 0.18816482114479421, -0.7930461563733091, -0.8631004002268415, -0.0725922638530214, 0.18499999999999828, -0.22179995773509673, -0.04755159140410673, 0.8442625472474002, 0.15830921156878192, 0.41986692949605736, 0.14864667540791923]


Random linear, best max deviation for a single point value:
Best error: 0.238317
Coefficients: [0.3562316646829533, -0.19254440618896096, -0.898988792922286, -0.179468774651788, 0.286855078156417, 0.9324925204930115, -0.39991235066191955, 0.7453719878808887, 0.9512402475847488, 0.5223158093269609, 0.2544888422424818, -0.4803864745716231, 0.45182327633193875, 0.888010487582295, 0.13771862991256367, 0.12920427599026962, 0.26646805387472017, -0.11998776883866613, -0.3157863394097349, 0.4145587314232686, -0.5396404607862597, -0.20699858135851024, 0.12706847173552838, -0.8760270908850449, 0.13209053403889404, 0.5333395909631973, -0.9810388783254522, -0.4141351598117802, -0.1158573572206234, 0.7329550054423919, 0.76069330197601, -0.6265146181127192, -0.6278369957658332, -0.5855419394516743, 0.12348197297821661]

"""
