# -*- coding: utf-8 -*-
"""
A function to randomly sample time-to-event values from the output of a regression model.

The program reads the regression output from an Excel table. The table contains the following
information:

    Parameter   - the name of the parameter
    Factor      - the coefficient within the regression
    VarType     - the type of variable the coefficient is coded as
                    1: categorical
                    2: continuous
                    3: dummy (no reference value)
    Level       - the value of the factor (i.e., 0/1, A/B/C, etc.)
    Mean        - the mean estimate of the coefficient
    SE          - the standard error of the estimate of the mean
    
This data is stored in a dictionary called 'regcoeffs' (the name is arbitrary).

When the funciton is called, it looks up the Level for each coefficient in the entity being
simulated. Based on the level, it randomly draws (from a normal distribution) a value for
the coefficient based on the mean and SE. A similar process occurs for the intercept. The
sum of the samples estimates for the intercept and the coefficients are log-transformed into
an estimate of time-to-event.

It is important to note that the name of the parameter must match EXACTLY (including being
case-sensitive) between how it appears in the entity and how it appears in the Excel table.
For example, the parameter "age" must be the same as "entity.age" or the
function will return an error.

The function will also return an error if the entity does not have all of the Factors
that are loaded into the regression. So, for example, if the entity does not have a value
for "age", the function will return an error.

@author: icromwell

Code provided by Stavros Korokithakis of Stochastic Technologies (www.stavros.io)
"""

import math
import numpy

"Define a function to draw estimates of time based on the regression coefficients"

class GenTime:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

    def readVal(self, entity, param):
        
        # Is the parameter being estimated contained within the Excel sheet?
        if param in self._regcoeffs:
   
            # The sum of the coefficients starts at zero
            coeff = 0
     
            # For a given factor of a parameter within the Excel sheet
            for factor in self._regcoeffs[param].keys():      
                
                # Identify the intercept
                if factor == 'Intercept':            
                    Intercept = self._regcoeffs[param]['Intercept']['mean']
                    
                # Identify the shape parameter from the output                 
                elif factor == 'Sigma':                
                    Sigma = self._regcoeffs[param]['Sigma']['mean']
                
                # Identify values for all other coefficients
                elif factor in entity.__dict__.keys():   
                    value = getattr(entity, factor)
                    
                    if self._regcoeffs[param][factor]['vartype'] == 2:
                        coeff += self._regcoeffs[param][factor]['mean'] * value
                    else:
                        coeff += self._regcoeffs[param][factor][value]['mean']
            
                # If the entity doesn't have the required factor    
                elif factor not in entity.__dict__.keys():                                  
                    entity.stateNum = 99
                    entity.currentState = "Error - could not estimate %s as entity is missing %s"%(param, factor)
                
            # Produce an estimate of time from the regression
            mu = Intercept + coeff         
            shape = 1/Sigma
            scale = math.exp(mu)
            
            self.mu = mu
            self.shape = shape
            self.scale = scale
            
        else:
            entity.stateNum = 99
            entity.currentState = "Error - tried to produce a time estimate for a variable that does not exist"
            
    # Randomly sample an event time for the entity from a Weibull distribution            
    def estTime(self):                 
        estimate_time = numpy.random.weibull(self.shape)*self.scale
        return estimate_time

    # Estimate the probability (CDF) of being alive at a given time
    def estProb(self, time):
        estimate_probability = numpy.math.exp(-(time/self.scale)**self.shape)
        return estimate_probability