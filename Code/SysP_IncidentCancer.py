# -*- coding: utf-8 -*-
"""
A parent program to co-ordinate the treatment of various oral cancers by stage. It reads the stage information
of incoming incident cancers, does a diagnostic workup, and then directs them to the appropriate treatment.

@author: icromwell
"""

class IncidentCancer:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

    def Process(self, entity):       
        if getattr(entity, "sympt", 0) == 1:                        # People who present through symptoms have to get a biopsy before their workup
            entity.resources.append(("Biopsy", entity.allTime))              # Add biopsy into resources list
            entity.sympt = 9                                            # Set symptomatic flag to placeholder value
    
        "Diagnostic workup of incoming cancer"
        entity.resources.append(("Diagnostic Workup", entity.allTime))

        # Determine treatment eligibility for first cancers
        if hasattr(entity, 'tx_prim') == False: 
            from Glb_CancerFlags import CancerFlags
            cancerflags = CancerFlags(entity, self._estimates)
            cancerflags.Process(entity)                         # Apply some disease and treatment flags 
 
        entity.time_Folup = 0        # Set (or reset, in the case of recurrence) the follow-up clock
        
        "Treat cancer by stage"
        
        # High grade lesion
        if entity.cancerStage =='HGL':
            entity.firstcancer = 'HGL'
            from SysP_HGLTx import HGLTx
            hgltx = HGLTx(self._estimates, self._regcoeffs)
            hgltx.Process(entity)
        
        # Stage I
        elif entity.cancerStage == 'I':
            entity.firstcancer = 'I'
            from SysP_StageOneTx import StageOneTx
            stageonetx = StageOneTx(self._estimates, self._regcoeffs)
            stageonetx.Process(entity)
            
        # Stage II
        elif entity.cancerStage == 'II':
            entity.firstcancer = 'II'
            from SysP_StageTwoTx import StageTwoTx
            stagetwotx = StageTwoTx(self._estimates, self._regcoeffs)
            stagetwotx.Process(entity)
                        
        # Advanced (III/IV)
        elif entity.cancerStage == 'Adv':
            entity.firstcancer = 'Adv'
            from SysP_StageAdvTx import StageAdvTx
            stageadvtx = StageAdvTx(self._estimates, self._regcoeffs)
            stageadvtx.Process(entity)
                      
        # Recurrence        
        elif entity.cancerStage == 'Recur':
            entity.time_recur = entity.allTime
            from SysP_RecurTx import RecurTx
            recurtx = RecurTx(self._estimates, self._regcoeffs)
            recurtx.Recurflags(entity)
            recurtx.Process(entity)
                    
        else:
            entity.stateNum = 99
            entity.currentState = "Error - the entity's cancer was not assigned a valid stage number - see Sysp_IncidentCancer.py"

####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   folupTime - the amount of time an entity has been undergoing post-treatment followup