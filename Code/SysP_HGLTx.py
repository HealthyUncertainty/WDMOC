# -*- coding: utf-8 -*-
"""
A program to describe the treatment and recovery process for an incident Stage I oral cancer.
Entities with a diagnosed stage I cancer will be treated either surgically (with/without RT),
with some other treatment type (usually Chemo+RT), or may receive no treatment. Their
post-treatment survival is calculated based on treatment type, stage, and other individual
characteristics.

After recovery (from surgery, chemo, and/or RT), entities are routed to the follow-up 
surveillance model component. Entities with less than three months survival are routed to 
the "End of Life" component.

Time of recurrence and death of disease (without further treatment) are set here. As with 
"SysP_Followup", the base case of the model is using the date of DIAGNOSIS as the starting 
point, rather than the date cancer is developed. This is consistent with the use of 
retrospective survival data from diagnosed patients.

@author: icromwell
"""

class HGLTx:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

        self.tx_time_treatment = estimates.Tx_time_treatment.sample()
        
        self.prob_other_RT = estimates.Tx_other_RT.sample()
        self.prob_other_chemo = estimates.Tx_other_chemo.sample()

    def Process(self, entity):    
        
        # HGLs are assumed to have perfect survival after surgical treatment
        entity.time_DeadofDisease = 99999
        entity.time_Recurrence = 99999        

        entity.hadSurgery = 1                
        entity.resources.append(("Treatment - HGL - Surgery", entity.allTime))
        entity.events.append(("Treatment - HGL - Surgery", entity.allTime))
        
        entity.stateNum = 4.0
        entity.currentState = "Post-treatment follow-up"
        
        entity.time_Sysp += self.tx_time_treatment