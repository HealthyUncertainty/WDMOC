# -*- coding: utf-8 -*-
"""
Generate some useful flags to use for assigning values to entities with newly-diagnosed cancer

Three types of treatment are possible:
    1. Surgical management alone
    2. Surgical management plus adjuvant RT
    3. Management that does not include surgery
Treatment type is assigned based on the underlying probability (by stage) of receiving each,
based on a Dirichlet process.

Newly-diagnosed cancers are grouped by stge (I/II/advanced). Stage I cancers that are detected
via screening may be classified as high-grade lesions (which includes CIS), and will be managed
purely surgically. Symptomatic cancers are assumed to be SCC, as are Stage II+ cancers detected
through screening.

"""

import random

class CancerFlags:
    def __init__(self, entity, estimates):
   
        self._estimates = estimates
       
        # Treatment Eligibility Flags
        
        self.Txprob = random.random()
        self.SCC = estimates.OPLfu_SCC.sample()
        
        # Treatment Type Flags
         # 'surgery' - no adjuvant RT or chemo
         # 'surgeryRT' - surgery and RT
         # 'other' - any treatment not involving surgery
         # 'notx' - no treatment received
     
    def Process(self, entity):
        entity.time_Cancer = entity.allTime
        
        from Glb_Estimates import diriSample
        # A 'names' vector for the dirichlet sampling process
        Txprob_names = ["Tx_probSurgery", "Tx_probSurgeryRT", "Tx_probOther"]
        
        # ASSIGN TREATMENT TYPE

        # Stage I Cancer
        if entity.cancerStage == 'I':
            if hasattr(entity, 'cancer_screenDetected') == True:
                HGL = random.random()
                if HGL > self.SCC:
                    entity.cancerStage = 'HGL'
                    entity.firstCancer = 'HGL'

            # A 'values' vector for the dirichlet sampling process
            Txprob_probs = [self._estimates.Tx_stageI_probSurgery.mean, 
                            self._estimates.Tx_stageI_probSurgeryRT.mean, 
                            self._estimates.Tx_stageI_probOther.mean]   
            
        # Stage II cancer
        elif entity.cancerStage == 'II':
            # A 'values' vector for the dirichlet sampling process
            Txprob_probs = [self._estimates.Tx_stageII_probSurgery.mean, 
                            self._estimates.Tx_stageII_probSurgeryRT.mean, 
                            self._estimates.Tx_stageII_probOther.mean]   
        
        # Advanced (STAGE III/IV) cancer
        elif entity.cancerStage == 'Adv':
            # A 'values' vector for the dirichlet sampling process
            Txprob_probs = [self._estimates.Tx_adv_probSurgery.mean, 
                            self._estimates.Tx_adv_probSurgeryRT.mean, 
                            self._estimates.Tx_adv_probOther.mean]   
                                
        # Every person with an HGL gets surgery        
        if entity.cancerStage == 'HGL':
            entity.tx_prim = 'Surgery'
        
        # Everyone else gets treatment assigned probabilistically    
        else:
            # Generate random value for treatment type
            diriSample(self._estimates, Txprob_names, Txprob_probs)      
                
            # Entity receives surgery alone
            if self.Txprob <= self._estimates.Tx_probSurgery:
                entity.tx_prim = 'Surgery'
                
            # Entity receives surgery + RT
            elif self._estimates.Tx_probSurgery \
                    < self.Txprob <= \
                    (self._estimates.Tx_probSurgeryRT + self._estimates.Tx_probSurgery):
                entity.tx_prim = 'SurgeryRT'
                    
            # Entity receives other adjuvant treatment
            elif (self._estimates.Tx_probSurgeryRT + self._estimates.Tx_probSurgery) <\
                    self.Txprob <= \
                    (self._estimates.Tx_probSurgeryRT + self._estimates.Tx_probSurgery + 
                        self._estimates.Tx_probOther):
                entity.tx_prim = 'Other'
                
            else:
                entity.currentState = "ERROR - Something has gone wrong in the treatment assignment process. Check 'Glb_CancerFlags'"
                entity.stateNum = 99
               
        "A count of the number of courses of RT/chemo"
        
        entity.RTCount = 0
        entity.chemoCount = 0

                
####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   hadSurgery - a flag for whether or not an entity has received surgical treatment
#   hadRT - a flag for whether or not an entity received radiotherapy
#   hadChemo - a flag for whether or not an entity received chemotherapy
#   txType - the type/combination of treatment the entity receives for their cancer
#   RTCount - a count of the number of times and entity has received RT
#   chemoCount - a count of the number of courses of chemotherapy the entity has received
                