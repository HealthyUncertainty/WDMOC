# -*- coding: utf-8 -*-
"""
Returning for regular post-treatment follow-up appointments.

The entity returns regularly to have their surgical site inspected, and will have
periodic biopsies, lab tests, and imaging done to investigate the presence of progression.

Follow-up is scheduled more frequently at first, and then gradually decreased. After ten
years, the person is assumed to be in remission (i.e., eventually dies from natural causes).

N.B.: Because the rates of recurrence are taken from *detected* cancers in the base case, 
this program does not actually simulate the process of detecting a cancer - cancers are 
assumed to be detected at the time of recurrence. The process is coded anyway to allow 
for the possibility of using other sources of data (e.g., clinical trial data) to investigate
cost-effectiveness scenarios regarding different recurrence- and followup-relevant policy
changes.

@author: icromwell
"""

class Followup:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

        self.appInt_0to3 = estimates.Folup_time_appInt0to3.sample()
        self.appInt_3to5 = estimates.Folup_time_appInt3to5.sample()
        self.appInt_5to10 = estimates.Folup_time_appInt5to10.sample()

    def Process(self, entity):
        
        if entity.time_Sysp > entity.allTime:
            # Have not yet reached next system process event, do nothing
            pass
        
        else:
        
            if hasattr(entity, "recurrence") == False:
                entity.recurrence = 0
        
            if hasattr(entity, "time_Folup") == False:
                entity.stateNum = 99;
                entity.currentState = "ERROR: The entity was not assigned a valid follow-up time in the 'IncidentCancer' process"
            
            # Assign Utility
            
            if entity.cancerStage == 'I' or entity.cancerStage == 'HGL':
                entity.utility.append(("Followup for Stage I cancer", self._estimates.Util_StageI_FU.sample(), entity.allTime))
            elif entity.cancerStage == 'II':
                entity.utility.append(("Followup for Stage II cancer", self._estimates.Util_StageII_FU.sample(), entity.allTime))
            elif entity.cancerStage == 'Adv':
                entity.utility.append(("Followup for Advanced cancer", self._estimates.Util_Advanced_FU.sample(), entity.allTime))
            elif entity.cancerStage == 'Recur':
                entity.utility.append(("Followup for Recurring cancer", self._estimates.Util_Recur_FU.sample(), entity.allTime))
            else:
                entity.stateNum = 99
                entity.currentState = "Error - Followup - entity does not have valid stage - see Sysp_Followup.py"
            # Follow-up appointments        
            # If fewer than 3 years have elapsed
            
            if entity.time_Folup <= 3*365.25:                              
                entity.resources.append(("Follow-up appointment - 1 to 3", entity.allTime))        
        
                if entity.recurrence == 1:
                    entity.events.append(("Detected recurrence", entity.allTime))     
                    entity.cancerStage = "recur"            # Entity has a detected recurrence
                    entity.stateNum = 3.0               # Entity returns for diagnostic workup and possible treatment
                    
                else:
                    entity.time_Folup += self.appInt_0to3
                    entity.time_Sysp += self.appInt_0to3
                    
            # If between 3 and 5 years have elapsed
        
            elif 3*365 < entity.time_Folup <= 5*365.25:
                entity.resources.append(("Follow-up appointment - 3 to 5", entity.allTime))        
        
                if entity.recurrence == 1:
                    entity.events.append(("Detected recurrence", entity.allTime))            
                    entity.cancerStage = "recur"            # Entity has a detected recurrence
                    entity.stateNum = 3.0               # Entity returns for diagnostic workup and possible treatment
                    
                else:
                    entity.time_Folup += self.appInt_3to5
                    entity.time_Sysp += self.appInt_3to5
        
            # If between 5 and 10 years have elapsed
        
            elif 5*365 < entity.time_Folup <= 10*365.25:
                entity.resources.append(("Follow-up appointment - 5 to 10", entity.allTime))        
        
                if entity.recurrence == 1:     
                    entity.events.append(("Detected recurrence", entity.allTime))                         
                    entity.cancerStage = "recur"            # Entity has a detected recurrence
                    entity.stateNum = 3.0               # Entity returns for diagnostic workup and possible treatment
                    
                else:
                    entity.time_Folup += self.appInt_5to10
                    entity.time_Sysp += self.appInt_5to10
                    
            # If more than 10 years have elapsed
            
            elif entity.time_Folup >= 10*365.25:
                entity.resources.append(("Follow-up appointment - final", entity.allTime))        
                entity.events.append(("Entity's cancer is in remission", entity.allTime))
                entity.utility.append(("Cancer in remission", self._estimates.Util_Remission.sample(), entity.allTime))
                
                entity.stateNum = 4.8           # Entity is in remission and receives no more care
                entity.currentState = "Remission"        
                entity.cancerDetected == 9      # Cancer is in remission and so no further clinical events are scheduled
                entity.time_deadOfDisease = 777777   # Death from disease set to implausibly high value
                entity.time_Recurrence = 666666     # Future recurrence set to implausble date
                entity.time_Sysp = 555555           # No future system process events occur
        

####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   None