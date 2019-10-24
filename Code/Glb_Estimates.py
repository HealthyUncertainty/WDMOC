# -*- coding: utf-8 -*-
"""
Import data from the Excel file in which model parameters are stored. Creates an object
called "estimates", which contains all of the model inputs in the following form:

    estimates.varname == 'name': <Estimate: type, mean, standard error>

IMPORTANT: If you want to use this file, you will have to make sure the Excel file is in the
            same directory as this file, or change the "load_workbook" path to the appropriate
            directory.

Variable Type:
    1 - Beta distributed (value between 0 and 1)
    2 - Normally distributed (value between negative and positive infinity)
    3 - Weibull distributed (value between 0 and infinity)
    4 - Gamma distributed (value between 0 and infinity)
    5 - Dirichlet distributed (create >2 probabilities that sum to 1.0 based on counts)
    6 - Log odds (import probability, convert to probability based on log-odds)
    7 - Exponential distribution (transition probability)
    8 - Beta distribution where values lie close to 1.0 or 0.0 (direct parameters)
    9 - Static value (i.e., does not vary)
    
Dirichlet-distributed variables must be 
    
Code provided by Stavros Korokithakis of Stochastic Technologies (www.stavros.io)

"""

import numpy
import math

class Estimates:                                    # An empty class to hold data
    pass

class Estimate:                                     # A class to process the data
    def __init__(self, etype, mean, se):
        self.type = etype                           # Define variable type
        self.mean = mean                            # Define mean value
        self.se = se                                # Define standard error

    def sample(self):                               # A function that checks variable type and samples a value accordingly
        if self.type == 1:                                              # Beta-distributed variables (probabilities)
            x = self.mean
            y = self.se
            # Parameterization of the beta distribution
            bdist_alpha = x*((x*(1-x)/y**2) - 1)
            bdist_beta = (1-x)*(x*(1-x)/y**2 - 1)
            
            samp_value = numpy.random.beta(bdist_alpha, bdist_beta)
            return samp_value
            
        elif self.type == 2:                                            # Normally-distributed variables
            samp_value = numpy.random.normal(self.mean, self.se)
            return abs(samp_value)
            
        elif self.type == 3:                                            # Weibull-distributed variables
            samp_value = numpy.random.weibull(self.mean, self.se)
            return samp_value
            
        elif self.type == 4:                                            # Gamma-distributed variables
            x = self.mean
            y = self.se
            gdist_shape = x**2/y**2                                    # A formula to produce the shape parameter
            gdist_scale = y**2/x                                       # A formula to produce the scale parameter
            samp_value = numpy.random.gamma(gdist_shape, gdist_scale)
            return samp_value
            
        elif self.type == 5:
            print("Variables of this type should use the 'dirisample' function")
            
        elif self.type == 6:
            x = self.mean
            y = self.se
            sampodds = numpy.random.normal(x, y)        # Randomly sample the log odds based on normally-distributed standard error
            samp_value = math.exp(sampodds)/(1 + math.exp(sampodds))    # Convert odds back to probability
            return samp_value
            
        elif self.type == 7:
            # Step 1: generate random estimate of the transition probability
            x = self.mean
            y = self.se
            bdist_alpha = x*((x*(1-x)/y**2) - 1)
            bdist_beta = (1-x)*(x/y**2*(1-x) - 1)
            est_tp = numpy.random.beta(bdist_alpha, bdist_beta)
            if est_tp < 1.0:
                pass
            else:
                est_tp = 0.9999
            
            # Step 2: generate random draw from exponential distribution
                # NOTE: probabilities must be entered into the table as year-long cycle lengths
            lmbd = -(math.log(1.0 - est_tp)/365.0)
            beta = 1/lmbd
            samp_value = numpy.random.exponential(beta)
            return samp_value
            
        elif self.type == 8:
            samp_value = numpy.random.beta(self.mean, self.se)
            return samp_value
            
        elif self.type == 9:
            samp_value = self.mean
            return samp_value
            
        else:
            print("Please specify a variable type in the input table")


    def __str__(self):
        return "<Estimate: %s, %s, %s>" % (self.type, self.mean, self.se)
    __repr__ = __str__
    
def diriSample(estimates, names, values):

    # A function that produces 'broken stick' estimates of probabilities from counts of >2 inputs           
    dirich = numpy.random.dirichlet(values)
    
    # Produce an estimate of each variable, and assign it the name from the "names" string    
    for i in range(0,len(values)):
        setattr(estimates, names[i], dirich[i])     
    
"""    
workbook = load_workbook('ImportTest.xlsx')
sheet = workbook.active

estimates = Estimates()

for line in sheet.rows:
    if not line[0].value:
        # There's no estimate name in this row.
        continue
    setattr(estimates, line[0].value, Estimate(line[1].value, line[2].value, line[3].value))

del(estimates.Parameter)

# To generate a sampled value from this function, the syntax is "estimates.varname.sample()"
"""