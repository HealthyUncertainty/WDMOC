# -*- coding: utf-8 -*-
"""
The progression of an OPL to stage I cancer, or spontaneously resolving

@author: icromwell
"""

from Glb_GenTime import GenTime

class OPLProg:
    
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs        
    
    def Process(self, entity): 
        # If this person doesn't already have the 'natHist' list created, create it for them
        if getattr(entity, "natHist", 0) == 0:                     
             entity.natHist = []
             
        if hasattr(entity, 'age') == 0:
            entity.age = entity.startAge

        gentime = GenTime(self._estimates, self._regcoeffs)
                
        # Randomly sample two competing TTE risks      
        # Time to OPL progression to cancer        
        gentime.readVal(entity, 'OPL_prog')
        t_OPL_StageOne = gentime.estTime()
        # Time to OPL spontaneously resolving        
        t_OPL_NED = self._estimates.NatHist_timeOPL_NED.sample()
    
        # Schedule the event that happens first
        if t_OPL_StageOne < t_OPL_NED:                              
            entity.nh_status = 2.0
            entity.nh_time += t_OPL_StageOne
            entity.natHist.append(("Stage 1", entity.nh_status, entity.nh_time))
        else:                                                          
            entity.nh_status = 0.0
            entity.nh_time += t_OPL_NED
            entity.natHist.append(("NED", entity.nh_status, entity.nh_time))


############################################################################################
# VARIABLES CREATED IN THIS STEP
#   
# None