"""
A process to describe the treatment of a recurrence of oral cancer.

A person with an identified recurrence has undergone confirmatory diagnostic testing
and is now prescribed a course of treatment. They may be managed surgically, nonsurgically,
or palliatively. They may also receive no treatment. This program contains a
treatment assignment protocol (Recurflags) and a treatment protocol (Process).

Palliative and non-treated patients are managed in the "Terminal Disease" component
of the model. Their "end of life" time is assigned by 'Glb_CheckTime.py'.

"""

import random
from Glb_GenTime import GenTime
from Glb_CompTime import CompTime

class RecurTx:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
        
        self.tx_time_treatment = estimates.Tx_time_treatment.sample()
        self.Txprob = random.random()
        
    def Recurflags(self, entity):
        from Glb_Estimates import diriSample
        
        if hasattr(entity, 'prevRecur') == False:
            entity.prevRecur = 0
            
        # Has entity experienced previous recurrence?
        # NO
        if entity.prevRecur == 0:          
             # Treatment Type Flags
                 # 'surgery' - managed surgically
                 # 'nonsurgery' - managed without surgery
                 # 'palliative' - managed palliatively
                 # 'notx' - no treatment received
    
            # A 'names' vector for the dirichlet sampling process
            Txprob_names = ["Tx_probSurgery", "Tx_probNonsurgery", "Tx_probPalliative", "Tx_probNoTx"]
    
            # A 'values' vector for the dirichlet sampling process
            Txprob_probs = [self._estimates.Tx_recurrence_probSurgery.mean, 
                            self._estimates.Tx_recurrence_probNonsurgery.mean, 
                            self._estimates.Tx_recurrence_probPalliative.mean, 
                            self._estimates.Tx_recurrence_probNoTx.mean]
                                
             # Generate random value for treatment type
            diriSample(self._estimates, Txprob_names, Txprob_probs)      
                
            # Entity receives surgery alone
            if self.Txprob <= self._estimates.Tx_probSurgery:
                entity.tx_recur = 'Surgery'
                
            # Entity receives surgery + RT
            elif self._estimates.Tx_probSurgery \
                    < self.Txprob <= \
                    (self._estimates.Tx_probSurgery + self._estimates.Tx_probNonsurgery):
                entity.tx_recur = 'Nonsurgery'
                    
            # Entity receives other adjuvant treatment
            elif (self._estimates.Tx_probNonsurgery + self._estimates.Tx_probSurgery) <\
                    self.Txprob <= \
                    (self._estimates.Tx_probSurgery + self._estimates.Tx_probNonsurgery + 
                        self._estimates.Tx_probPalliative):
                entity.tx_recur = 'Palliative'
                
            # Entity receives other adjuvant treatment
            elif (self._estimates.Tx_probSurgery + self._estimates.Tx_probNonsurgery + 
                    self._estimates.Tx_probPalliative) < \
                    self.Txprob <= \
                    (self._estimates.Tx_probSurgery + self._estimates.Tx_probNonsurgery + 
                        self._estimates.Tx_probPalliative + self._estimates.Tx_probNoTx):
                entity.tx_recur = 'Notx'
        
            else:
                entity.currentState = "ERROR - Something has gone wrong in the treatment assignment process. Check 'SysP_RecurTx.py'"
                entity.stateNum = 99
        # END IF NO PREVIOUS RECURRENCE

        # YES
        elif entity.prevRecur == 1:
            # No additional steps needed to assign time
            pass

        else:
            entity.currentState = "ERROR - The entity has not been assigned a 'prevRecur' flag somehow. Check 'SysP_RecurTx.py'"
            entity.stateNum = 99

    def Process(self, entity):
        
        start = entity.allTime
        entity.time_Sysp = entity.allTime
   
        entity.stateNum = 4.0
        entity.currentState = "Post-treatment follow-up"
        entity.utility.append(("Recurrence Under Treatment", self._estimates.Util_Recur_Tx.sample(), entity.allTime))
        
        no2recur = 0

        # Has entity experienced previous recurrence?        
        if entity.prevRecur == 0:
            # No previous recurrence
            # What type of treatment does the entity receive?
            if entity.tx_recur == 'Surgery':
                entity.resources.append(("Treatment - Recurrence - Surgery", entity.allTime))
                entity.events.append(("Recurrence Surgery", entity.allTime))
                entity.time_Sysp += self.tx_time_treatment
                entity.utility.append(("Recurring Cancer In Remission", self._estimates.Util_Recur_FU.sample(), entity.allTime))
                
            elif entity.tx_recur == 'Nonsurgery':
                entity.resources.append(("Treatment - Recurrence - Nonsurgery", entity.allTime))
                entity.events.append(("Nonsurgical management of recurrence", entity.allTime))
                entity.time_Sysp += self.tx_time_treatment
                entity.utility.append(("Recurring Cancer In Remission", self._estimates.Util_Recur_FU.sample(), entity.allTime))
           
            # Palliative and non-treated entities enter the terminal disease state       
           
            elif entity.tx_recur == 'Palliative':
                entity.resources.append(("Treatment - Recurrence - Palliative", entity.allTime))
                entity.events.append(("Palliative care for recurrence", entity.allTime))            
                entity.stateNum = 5.0
                entity.currentState = "Terminal disease"
                no2recur = 1
                #entity.time_Sysp +=0.01 # No time elapses
                entity.utility.append(("Incurable disease", self._estimates.Util_Incurable.sample(), entity.allTime))
            
            elif entity.tx_recur == 'Notx':
                entity.resources.append(("Treatment - Recurrence - No Treatment", entity.allTime))
                entity.events.append(("No treatment for recurrence", entity.allTime))
                entity.stateNum = 5.0
                entity.currentState = "Terminal disease"
                no2recur = 1
                #entity.time_Sysp +=0.01 # No time elapses
                entity.utility.append(("Incurable disease", self._estimates.Util_Incurable.sample(), entity.allTime))
                
            else:
                entity.stateNum = 99
                entity.currentState = "Error: Entity has not been assigned a valid treatment"
                         
            # Schedule next event
            makeEvent = CompTime(self._estimates, self._regcoeffs)
            nextEvent = makeEvent.Process(entity, 'SecondEvent', 'SecondEvent_death')

            if nextEvent[0] < 3650:
                if nextEvent[1] == 1: #Event is recurrence
                    entity.time_Recurrence = start + nextEvent[0]
                    entity.time_DeadofDisease = 99999
                elif nextEvent[1] == 2: #Event is death
                    entity.time_Recurrence = 99999
                    entity.time_DeadofDisease = start + nextEvent[0]
                entity.prevRecur = 1
                                
                if nextEvent[0] < 90:
                # If next event occurs before three months
                    if nextEvent[1] == 1: #Entity dies before 90 days
                        entity.statenum = 5.0 # Entity is in EoL care state
                        entity.currentState = "End of life"
                        entity.endOfLife = 1
                    else: 
                        entity.stateNum = 4.0
                        entity.currentState = "Post-treatment follow-up"
                    entity.time_Sysp = entity.allTime + nextEvent[0]
                
            else:
                entity.time_DeadofDisease = 99999
                entity.time_Recurrence = 99999
                
            # Next event for those without treatment or managed palliatively will always be death from disease
            if no2recur == 1:
                entity.time_Recurrence = 99999
                entity.time_DeadofDisease = start + nextEvent[0]
        
            entity.recurrence = 0                   # Reset "active recurrence" flag
            entity.prevRecur = 1                    # Set "previous recurrence" flag
            entity.folupTime = 0                    # Reset follow-up time counter
        # END IF NO PREVIOUS RECURRENCE
    
        elif entity.prevRecur == 1:
            # YES
            entity.utility.append(("Second Recurrence Under Treatment", self._estimates.Util_2Recur_Tx.sample(), entity.allTime))
            entity.resources.append(("Treatment - Second Recurrence", entity.allTime))
            entity.events.append(("Treatment for Second Recurrence", entity.allTime))
            entity.time_Sysp += self.tx_time_treatment
            
            # Generate random time for death of disease or remission
            makeTime = GenTime(self._estimates, self._regcoeffs)
            makeTime.readVal(entity, 'TSRD')
            entity.time_DeadofDisease = start + makeTime.estTime()
            # If randomly drawn time is greater than 10 years, entity will go into remission
            if entity.time_DeadofDisease > 3650:
                entity.time_DeadofDisease = 99999
                
            entity.recurrence = 0                   # Reset "active recurrence" flag
            entity.folupTime = 0                    # Reset follow-up time counter
            
        else:
            entity.currentState = "ERROR: Entity does not have a 'prevRecur' flag. Check 'SysP_RecurTx.py'"
            entity.stateNum = 99