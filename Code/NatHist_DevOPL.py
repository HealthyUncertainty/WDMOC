# -*- coding: utf-8 -*-
"""
A program to assign risk category to a person with an OPL.

"""

from Glb_Estimates import diriSample

import random

################################################################################################

class DevOPL:
    
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

        self.screenInt = random.randint(1,10)                # The dentist screens for cancer at a random constant frequency
        self.hasOPL = random.random()                        # Generate random number for the chance of starting with OPL
        self.OPLRisk = random.random()                   
    
    def Process(self, entity):    
        if self.hasOPL < entity.probOPL:                        # If the random number lies beyond the prevalence estimate      
            entity.nh_status = 1.0                  # Trigger the rest of the natural history assignment process
            entity.OPLStatus = 1                    # Entity has an undetected OPL
            entity.hasOPL = 1
            entity.utility.append(("Undetected OPL", self._estimates.Util_OPL_Undetected.sample(), entity.allTime))
            
        else:
            entity.nh_status = 0.9                  # Bypass the natural history assignment process
            entity.OPLStatus = 0                    # Entity is disease free
        
        "Assign risk category of OPL progression"
        
        if entity.OPLStatus == 1:
            
            # A 'names' vector for the dirichlet sampling process
            OPLRiskGroup_names = ["OPLRisk_Low", "OPLRisk_Med", "OPLRisk_Hi"]
            # A 'values' vector for the dirichlet sampling process
            OPLRiskGroup_probs = [self._estimates.NatHist_OPLrisk_low.mean, self._estimates.NatHist_OPLrisk_med.mean, self._estimates.NatHist_OPLrisk_hi.mean]   
            
            diriSample(self._estimates, OPLRiskGroup_names, OPLRiskGroup_probs)      # Generate random value for OPL risk group  
                
            if self.OPLRisk <= self._estimates.OPLRisk_Low:      # Low risk group
                entity.OPLRisk = 'Lo'
            elif self.OPLRisk <= self._estimates.OPLRisk_Low + self._estimates.OPLRisk_Med:     # Medium risk group
                entity.OPLRisk = 'Med'
            elif self.OPLRisk > self._estimates.OPLRisk_Low + self._estimates.OPLRisk_Med:      # High risk group
                entity.OPLRisk = 'Hi'
            else:
                print("Something has gone wrong in the OPL risk assignment process")
                entity.currentState = "Error - something has gone wrong in the OPL risk assignment process, check NatHist_DevOPL.py"
                entity.stateNum = 99
    

# VARIABLES CREATED IN THIS STEP:
    # OPLRisk - a progression risk category based on LOH status (1 - low; 2 - medium; 3 - high)
    