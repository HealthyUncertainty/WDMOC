# -*- coding: utf-8 -*-
"""
OPL Follow-up and management.

People with detected OPLs are periodically re-evaluated for evidence of progression to cancer. The person is periodically biopsied.
If cancer has developed, the person is referred for pathology.

@author: icromwell
"""

import random

class OPLManage:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs        

        self.general_appInt = int(estimates.OPLfu_appint.sample())        
        self.sensitivity = estimates.OPLfu_sensitivity.sample()
        self.specificity = estimates.OPLfu_specificity.sample()


    def Process(self, entity):
        entity.OPLdetected = 1
        from Glb_CancerFlags import CancerFlags
        cancerflags = CancerFlags(entity, self._estimates)        
        appInt = self.general_appInt

        if entity.time_Sysp > entity.allTime:
            # Have not yet reached next system process event, do nothing
            pass
        
        else:        
            "How long has the entity been undergoing OPL surveillance?"
            if hasattr(entity, 'time_OPLfu') == False:
                entity.time_OPLfu = 0
            else:   # If follow-up >5y, return to regular screening
                if entity.time_OPLfu > 1825:
                    entity.OPLStatus = 9                 
                    entity.stateNum = 1.0
                    entity.currentState = "1.0 - Undergoing regular dental screening"
                else:
                    entity.time_OPLfu += appInt
            
            if getattr(entity, "count_BiopsyInt", 0) == 0:              # If this person doesn't already have the 'count_BiopsyInt' field created, create it for them
                entity.count_BiopsyInt = 0                              # Start a count for the screening interval
                
            if getattr(entity, "OPLscreenInt", 0) == 0:                     # If this person doesn't already have the 'OPLscreenInt' field created, create it for them
                entity.OPLscreenInt = random.randint(1,10)                        # The dentist screens for cancer at a random constant frequency
                                
            if entity.count_BiopsyInt < entity.OPLscreenInt:                         # If the biopsy interval has not yet been reached
                entity.count_BiopsyInt += 1                             # Add running count to the number of follow-up appointments before biopsy
                entity.resources.append(("OPL surveillance appointment", entity.allTime))          # Enter appointment into resources list
                
                if entity.hasCancer == 0:                                       # If the person does not have cancer, re-evaluate them at the next appointment
                    falsePos = random.random()
                    if falsePos > self.specificity:
                        # Visual screen returns false positive, sent for biopsy
                        entity.resources.append(("Biopsy", entity.allTime))
                        entity.count_BiopsyInt = 0  # Reset biopsy count
                    entity.time_Sysp += appInt
                    
                else:                                                           
                    # If a person has cancer, it is visually inspected and may yield a false negative
                    falseNeg = random.random()
                    if falseNeg > self.sensitivity:
                        entity.time_Sysp += appInt
    
                    else:
                        # True positive, cancer is detected and referred for treatment                    
                        entity.resources.append(("Biopsy", entity.allTime))                                # Add biopsy into resources list
                        entity.events.append(("Cancer first detected at OPL followup", entity.allTime))
                        entity.cancer_screenDetected = 1
                        entity.cancerDetected = 1
                        entity.time_cancerDetected = entity.allTime                  # The time at which the entity's cancer was detected
                        entity.stateNum = 3.0
                        cancerflags.Process(entity)                                  # Apply some basic treatment flags to detected cancer
                        entity.currentState = "3.0 - Invasive cancer detected"
                
            else:                                                       # Once the biopsy interval is reached
                entity.count_BiopsyInt = 0                                  #Reset biopsy counter
                entity.resources.append(("OPL surveillance appointment", entity.allTime))          # Enter appointment into resources list
                entity.resources.append(("Biopsy", entity.allTime))                                # Add biopsy into resources list
                
                if entity.hasCancer == 1:
                    entity.events.append(("Cancer first detected at regular biopsy", entity.allTime))
                    entity.cancer_screenDetected = 1
                    entity.cancerDetected = 1
                    entity.time_cancerDetected = entity.allTime                          # The time at which the entity's cancer was detected
                    entity.stateNum = 3.0
                    entity.currentState = "3.0 - Invasive cancer detected"
                    cancerflags.Process(entity)                           # Apply some basic treatment flags to detected cancer
                    
                else:
                    #OPL is biopsied - no cancer detected
                    entity.time_Sysp += appInt

####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   count_BiopsyInt - a counter for the number of appointments since last biopsy
#   OPLScreenInt - the screening interval between biopsies            