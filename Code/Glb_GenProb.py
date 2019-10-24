# -*- coding: utf-8 -*-
"""
A function to randomly sample probability estimates from the output of a 
logistic regression model.

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
simulated. Using those values, it returns an estimate of the probability of each category
of the outcome being estimated.

It is important to note that the name of the parameter must match EXACTLY (including being
case-sensitive) between how it appears in the entity and how it appears in the Excel table.
For example, the parameter "smokeStatus" must be the same as "entity.smokeStatus" or the
function will return an error.

The function will also return an error if the entity does not have all of the Factors
that are loaded into the regression. So, for example, if the entity does not have a value
for "smokeStatus", the function will return an error.

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

    def sample(self, entity, param):
        
        # Is the parameter being estimated contained within the Excel sheet?
        if param in self._regcoeffs:
   
            # The sum of the coefficients starts at zero
            coeff = 0
            probestimates = []
     
            # For a given factor of a parameter within the Excel sheet
            for factor in regcoeffs[param].keys():
                
                if factor == 'Category':
                    pass
                
                # Identify values for all coefficients
                elif factor in entity.__dict__.keys():   
                    value = getattr(entity, factor)
                    
                    if regcoeffs[param][factor]['vartype'] == 2:
                        coeff += regcoeffs[param][factor]['mean'] * value
                    else:
                        coeff += regcoeffs[param][factor][value]['mean']
            
                # If the entity doesn't have the required factor    
                elif factor not in entity.__dict__.keys():                                  
                    entity.stateNum = 99
                    entity.currentState = "Error - could not estimate %s as entity is missing %s"%(param, factor)                
                
            # Identify the intercept
            for category_name, value in regcoeffs[param]['Category'].items():
                if not isinstance(value, dict):
                    continue
                Mu = value['mean'] + coeff
                probestimates.append((category_name, math.exp(Mu)/(1 - math.exp(Mu))))
                
        return samp_value
   
for category_name, value in regcoeffs[param]['Category'].items():
    catval = [category_name, value]
    print(catval)             
                
                
                    # Produce an estimate of time from the regression
                    mu = Intercept + coeff         
                    prob = math.exp(mu)
                    
                    probestimates.append(())
                 
            estimate_time = numpy.random.weibull(shape)*scale
            return estimate_time

        else:
            entity.stateNum = 99
            entity.currentState = "Error - tried to produce a time estimate for a variable that does not exist"