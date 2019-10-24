# -*- coding: utf-8 -*-
"""
The natural history of oral cancer progression

This file sequences the development of oral cancer from full health through to death of untreated metastatic disease. The events
are output to a list called 'natHist' which contains the hypothetical sequence of health events that a person would experience
if not for the intervention of the health care system.

The sequence of events:

    1 - Aparently healthy person develops OPL
    
    2 - OPL may:
        a) progress to stage I cancer
        b) spontaneously resolve
        
    3 - Stage I cancer may:
        a) progress to stage II cancer
        b) be detected symptomatically
        
    4 - Stage II cancer may:
        a) progress to stage III cancer
        b) be detected symptomatically
        
    5 - Stage III cancer may:
        a) progress to stage IV cancer
        b) be detected symptomatically
        
    6 - Stage IV cancer may:
        a) kill the affected person
        b) be detected symptomatically
        
@author: icromwell
"""

import numpy

class NatHistOCa:
    
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
        self.timehorizon = estimates.timehorizon.sample()*365
    
    def Process(self, entity, natHist):   
           
        if getattr(entity, "natHist", 0) == 0:                     # If this person doesn't already have the 'natHist' field created, create it for them
            entity.natHist = []
        
        from NatHist_DevOPL import DevOPL                     # Assign OPL status based on age/sex prevalence
        devopl = DevOPL(self._estimates, self._regcoeffs)
        devopl.Process(entity)
        
        entity.horizon_censor = 0
        if entity.natHist_deathAge > self.timehorizon:
            entity.natHist_deathAge = self.timehorizon
            entity.horizon_censor = 1
        
        "Assign oral cancer progression dates"
        
        while entity.nh_det == 0:
                                         
            #1 - Person does not have OPL
            if entity.nh_status == 0.0:
                entity.natHist.append(("Natural Death", 9.0, entity.natHist_deathAge))         # No events besides natural death occur
                break
            
            #2 - OPL may progress to stage I cancer or spontaneously resolve
                    
            elif entity.nh_status == 1.0:
                from NatHist_OPLProg import OPLProg
                oplprog = OPLProg(self._estimates, self._regcoeffs)
                oplprog.Process(entity)
                
            elif entity.nh_status == 0.9:                                                        # Resolved OPL
                entity.natHist.append(("Natural Death", 9.0, entity.natHist_deathAge))         # Next (and final) event is natural death
                break
                               
            #3 - Undetected cancer may progress or be detected symptomatically
                    
            elif (entity.nh_status > 1.0) & (entity.nh_status != 9.0):
                from NatHist_UnDet import UnDet
                undet = UnDet(self._estimates, self._regcoeffs)
                undet.Process(entity)
                
            elif entity.nh_status == 9.0:                                                       # Detected cancer, no more natural history events
                break
            
            else: 
                entity.stateNum = 99
                entity.currentState = "Natural History status (nh_status) was improperly assigned. Check NatHist_OralCancer"
                break

        natHist.append(entity.natHist)
        #natHistAr = numpy.asarray(entity.natHist)                     # Convert 'natHist' into numPy array
        #numpy.save('natHistAr', natHistAr)                            # Export array to the working directory so it can be read by other programs
    
            
############################################################################################
# VARIABLES CREATED IN THIS STEP
#   
# None