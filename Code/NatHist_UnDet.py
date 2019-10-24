# -*- coding: utf-8 -*-
"""
Progression of undetected oral cancer. Cancers can either present symptomatically 
(i.e., person has pain or other symptoms that makes it possible for their lesion to
be detected through routine practice), or can progress to a more advanced stage. 
Stage 4 cancers can be fatal.

@author: icromwell
"""


class UnDet:

    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
        
        self.t_StageOne_Sympt = estimates.NatHist_timeSympt_stageone.sample()
        self.t_StageOne_StageTwo = estimates.NatHist_timeStageone_stagetwo.sample()
        
        self.t_StageTwo_Sympt = estimates.NatHist_timeSympt_stagetwo.sample()
        self.t_StageTwo_StageThree = estimates.NatHist_timeStagetwo_stagethree.sample()
        
        self.t_StageThree_Sympt = estimates.NatHist_timeSympt_stagethree.sample()
        self.t_StageThree_StageFour = estimates.NatHist_timeStagethree_stagefour.sample()
        
        self.t_StageFour_Sympt = estimates.NatHist_timeSympt_stagefour.sample()
    
    def Process(self, entity):    
        
        # If this person doesn't already have the 'natHist' field created, create it for them
        if hasattr(entity, "natHist") == 0:                     
             entity.natHist = []    
        
        while entity.nh_det == 0:
    
            "Stage One Cancers"    
            
            if entity.nh_status == 2.0:
                if self.t_StageOne_Sympt < self.t_StageOne_StageTwo:
                    entity.nh_status = 2.1
                    entity.nh_time += self.t_StageOne_Sympt
                    entity.natHist.append(("Detectable Stage 1", entity.nh_status, entity.nh_time))
                    entity.nh_det = 1
                    break
                else:
                    entity.nh_status = 3.0
                    entity.nh_time += self.t_StageOne_StageTwo            
                    entity.natHist.append(("Undetected Stage 2", entity.nh_status, entity.nh_time))
            
            "Stage Two Cancers"
            
            if entity.nh_status == 3.0:
                if self.t_StageTwo_Sympt < self.t_StageTwo_StageThree:
                    entity.nh_status = 3.1
                    entity.nh_time += self.t_StageTwo_Sympt            
                    entity.natHist.append(("Detectable Stage 2", entity.nh_status, entity.nh_time))
                    entity.nh_det = 1
                    break
                else:
                    entity.nh_status = 4.0
                    entity.nh_time += self.t_StageTwo_StageThree            
                    entity.natHist.append(("Undetected Stage 3", entity.nh_status, entity.nh_time))
            
            
            "Stage Three Cancers"
             
            if entity.nh_status == 4.0:   
                if self.t_StageThree_Sympt < self.t_StageThree_StageFour:
                    entity.nh_status = 4.1
                    entity.nh_time += self.t_StageThree_Sympt
                    entity.natHist.append(("Detectable Stage 3", entity.nh_status, entity.nh_time))
                    entity.nh_det = 1
                    break
                else:
                    entity.nh_status = 5.0            
                    entity.nh_time += self.t_StageThree_StageFour
                    entity.natHist.append(("Undetected Stage 4", entity.nh_status, entity.nh_time))
                    
                    
            "Stage Four Cancers"
            
            if entity.nh_status == 5.0:
                # Estimate age- and sex-specific time of death from undetected cancer
                # Calculate age at which entity will develop stage IV cancer
                nh_stIVage = (entity.startAge*365.25 - entity.nh_time)/365.25
                from NatHist_StageIVDeath import StageIVDeath
                deathtime = StageIVDeath(self._estimates)
                # Calculate time to death given entity sex and age
                t_StageFour_Death = deathtime.GenDTime(entity, nh_stIVage)
                
                if self.t_StageFour_Sympt < t_StageFour_Death:
                    entity.nh_status = 5.1            
                    entity.nh_time += self.t_StageFour_Sympt
                    entity.natHist.append(("Detectable Stage 4", entity.nh_status, entity.nh_time))
                    entity.nh_det = 1
                    break
                else:
                    entity.nh_status = 100
                    entity.nh_time += t_StageFour_Death
                    entity.natHist.append(("Dead of undetected oral cancer", entity.nh_status, entity.nh_time))
                    entity.nh_det = 1
                    break
