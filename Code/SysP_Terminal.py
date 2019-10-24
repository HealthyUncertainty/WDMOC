# -*- coding: utf-8 -*-
"""
A program to describe the management of terminal disease. There are two possible types of
advanced disease care:

    1 - Not eligible for curative RT, but not yet at end-of-life
    
        These are typically people who have received no treatment, or are receiving palliative
        treatment.
    
    2 - Last three months of life (terminal)
    
        These people receive a generic "end of life" set of palliative treatments.        
        This component works on one-month "cycles". The cycle length was chosen arbitrarily.
        
Based on the entity's disease status, they will receive some sort of treatment that does not
prolong their life. The program tracks the number of months they remain in this terminal
state - this number is used for costing. The clock is advanced one month forward at the end
of each run. It is designed to work in conjunction with 'SysP_Followup'.

@author: icromwell
"""
class Terminal:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs

    def Process(self, entity):
        
        entity.time_Sysp = entity.allTime
           
        # Entities receiving no treatment OR palliative treatment (for recurrence)
        if hasattr(entity, 'endOfLife') == False:

            # Entities with recurrence may be palliative or NoTx        
            if hasattr(entity, 'recurrence') == True:
                entity.utility.append(("Incurable disease", self._estimates.Util_Incurable.sample(), entity.allTime))

                if entity.tx_recur == 'Palliative':
                    if hasattr(entity, "palliativeMonth") == False:
                        entity.palliativeMonth = 1
                    # Entity experiences spontaneous remission
                    if entity.palliativeMonth >= 520:                
                        entity.stateNum = 4.8           # Entity is in remission and receives no more care
                        entity.currentState = "Remission"        
                        entity.cancerDetected == 9      # Cancer is in remission and so no further clinical events are scheduled
                        entity.time_deadOfDisease = 777777   # Death from disease set to implausibly high value
                        entity.time_Recurrence = 666666     # Future recurrence set to impossible date
                    else:
                        entity.resources.append(("Treatment - Palliative", entity.allTime))
                        entity.events.append(("Palliative care - month%2.0f"%entity.palliativeMonth, entity.allTime))
                        entity.palliativeMonth +=1
    
                elif entity.tx_recur == 'Notx':
                    if hasattr(entity, "notxMonth") == False:
                        entity.notxMonth = 1
                    # Entity experiences spontaneous remission
                    if entity.notxMonth >= 520:                
                        entity.stateNum = 4.8           # Entity is in remission and receives no more care
                        entity.currentState = "Remission"        
                        entity.cancerDetected == 9      # Cancer is in remission and so no further clinical events are scheduled
                        entity.time_deadOfDisease = 777777   # Death from disease set to implausibly high value
                        entity.time_Recurrence = 666666     # Future recurrence set to impossible date
                    else:
                        entity.resources.append(("Treatment - Recurrence - No Treatment", entity.allTime))
                        entity.events.append(("Best supportive care - month%2.0f"%entity.notxMonth, entity.allTime))
                        entity.notxMonth += 1
                        
                entity.time_Sysp += 30                # Advance clock one month
            
            else:
                entity.stateNum = 99
                entity.currentState = "ERROR - Terminal Disease - entity is in the Terminal disease state, but has not recurred or been assigned an end of life flag. Check 'SysP_RecurTx' or 'Glb_Checktime'"
                print("Entity was not assigned an 'endOfLife' or 'recurrence' flag. Check 'SysP_RecurTx' or 'Glb_Checktime'")

        # END IF    

        # Entity is in last three months of life                
        elif hasattr(entity, 'endOfLife') == True:             
            #Terminal disease - end-of-life care
            entity.resources.append(("Treatment - End of Life", entity.allTime))
            entity.events.append(("End-of-life care", entity.allTime))
            entity.utility.append(("End of life", self._estimates.Util_EOL.sample(), entity.allTime))
            entity.allTime = entity.time_DeadofDisease      # Advance clock to death
        
        else:                                   # Error
            entity.stateNum = 99
            entity.currentState = "ERROR - Advanced Disease"
            print("Entity was not assigned an 'endOfLife' value. Check 'SysP_RecurTx' or 'Glb_Checktime'")
            

    
####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   adv_hadSalvage - flag indicating that the entity has received salvage surgery
#   adv_reirrad - flag indicating that the entity has received a second round of RT
#   adv_chemoCount - a counter for the number of cycles of advanced chemotherapy received
#   chemoLimit - the maximum number of cycles of chemo an entity can receive
#   EoLMonth - a counter to denote the number of months into the terminal phase an entity has come    
        