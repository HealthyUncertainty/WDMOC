# -*- coding: utf-8 -*-
"""
This file checks the passage of time at the beginning of each loop of 'Sequencer.py'. 
If events have occurred since the last check, (i.e., disease progression, aging, 
natural death, etc.) the appropriate changes are made to the entity's attributes.

@author: icromwell
"""

import numpy

def CheckTime(entity, estimates, natHist, QALY):
    
    "Update entity age"
    entity.age = entity.startAge + int(entity.allTime/365.25)
    
    "Check for natural death"
    if entity.allTime > entity.natHist_deathAge:
        entity.allTime = entity.natHist_deathAge
    if int(round((entity.allTime - entity.natHist_deathAge),3)) == 0:
        entity.allTime = entity.natHist_deathAge            # The simulation concludes with the entity's death            
        entity.time_death = entity.allTime                  # The time of death is recorded
        entity.death_type = 2                               # The entity has died of natural causes
        entity.death_desc = "Dead of Natural Causes"
        entity.stateNum = 100                               # The entity is dead
        entity.currentState = "Dead"
    
    else:
        
        # If the entity does not have detected disease, perform the natural history check
        if entity.cancerDetected == 0:                         
           
            # Load the array with the natural history events
            # The first row of the 'natHist' array is identified as the next event scheduled to occur
            if hasattr(entity, 'nhnum') == False:
                entity.nhnum = 0
                
            natHistAr = entity.natHist
            nextNatAr = natHistAr[entity.nhnum]                          
            
            # What is the next natural history event that is scheduled to occur?
            # When does that event occur?
            nextNat_status = float(nextNatAr[1])            
            nextNat_time = float(nextNatAr[2])
            
            # Which type of event occurs next, system process or natural history?
            if entity.time_Sysp <= nextNat_time:
                # The next event to occur is a system process event
                # Advance clock to next system process time
                entity.allTime = entity.time_Sysp
            
            else:
                # The next event to occur is a natural history event
                # Check: has the event occurred yet?            
                if entity.allTime >= nextNat_time:                 
                    
                    # The event has occurred, and is removed from the array so that the next event can take its place
                    entity.nhnum +=1
                    
                    # NED - No Evidence of Disease        
                    
                    if nextNat_status == 0.0:
                        entity.utility.append(("No disease", estimates.Util_Well.sample(), entity.allTime))
                        entity.OPLStatus = 0
                        entity.allTime = nextNat_time
                        #print("The entity's OPL resolves at %2.0f"%entity.allTime)
                        
                    # Oral Premalignancy            
                        
                    elif nextNat_status == 1.0: 
                        entity.utility.append(("Undetected OPL", estimates.Util_OPL_Undetected.sample(), entity.allTime))
                        entity.OPLStatus = 1                                
                        entity.time_OPL = nextNat_time
                        entity.allTime = nextNat_time
                        #print("The entity develops an OPL at %2.0f"%entity.allTime)
                        
                    elif nextNat_status == 1.1:
                        entity.utility.append(("Detected OPL", estimates.Util_OPL_Detected.sample(), nextNat_time))
                        entity.diseaseDetected = 1
                        entity.time_OPLDetected = nextNat_time
                        entity.stateNum = 2.0                    
                        entity.currentState = "2.0 - OPL Detected"
                        entity.allTime = nextNat_time
                        
                    # Stage I Cancer            
                        
                    elif nextNat_status == 2.0:
                        entity.utility.append(("Undetected Stage I", estimates.Util_StageI_Undetected.sample(), entity.allTime))
                        entity.hasCancer = 1                                # 'hasCancer' status changes to 1
                        entity.cancerStage = 'I'                            # the cancer is at Stage I
                        entity.OPLStatus = 9                                
                        entity.time_Cancer = nextNat_time                  # The time that the entity first developed cancer is recorded
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity has an undetected Stage I cancer")
                        
                    elif nextNat_status == 2.1:                         # If the entity has symptomatic stage 1 cancer...
                        entity.diseaseDetected = 1
                        entity.cancerDetected = 1
                        entity.sympt = 1
                        entity.time_cancerDetected = nextNat_time         # The time that the entity's cancer was detected is recorded
                        entity.stateNum = 3.0                               # The entity moves to the "detected cancer" state
                        entity.currentState = "Treatment for incident oral cancer"
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity's Stage I cancer has been detected symptomatically")
                
                    # Stage II Cancer
                        
                    elif nextNat_status == 3.0:                         # If the entity has stage 2 cancer...
                        entity.utility.append(("Undetected Stage II", estimates.Util_StageII_Undetected.sample(), entity.allTime))
                        entity.cancerStage = 'II'                              # the cancer is at Stage II
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity has an undetected Stage II cancer")
                        
                    elif nextNat_status == 3.1:                         # If the entity has symptomatic stage 2 cancer...
                        entity.diseaseDetected = 1
                        entity.cancerDetected = 1
                        entity.sympt = 1
                        entity.time_cancerDetected = nextNat_time         # The time that the entity's cancer was detected is recorded
                        entity.stateNum = 3.0                               # The entity moves to the "detected cancer" state
                        entity.currentState = "Treatment for incident oral cancer"
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity's Stage II cancer has been detected symptomatically")
                
                    # Stage III Cancer
                        
                    elif nextNat_status == 4.0:                         # If the entity has stage 3 cancer...
                        entity.utility.append(("Undetected Stage III", estimates.Util_StageIII_Undetected.sample(), entity.allTime))
                        entity.cancerStage = 'Adv'                              # the cancer is at Stage 3
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity has an undetected Stage III cancer")
                        
                    elif nextNat_status == 4.1:                         # If the entity has symptomatic stage 3 cancer...
                        entity.diseaseDetected = 1
                        entity.cancerDetected = 1
                        entity.sympt = 1
                        entity.time_cancerDetected = nextNat_time         # The time that the entity's cancer was detected is recorded
                        entity.stateNum = 3.0                               # The entity moves to the "detected cancer" state
                        entity.currentState = "Treatment for incident oral cancer"
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity's Stage III cancer has been detected symptomatically")
                
                    # Stage IV Cancer
                        
                    elif nextNat_status == 5.0:                         # If the entity has stage 4 cancer...
                        entity.utility.append(("Undetected Stage IV", estimates.Util_StageIV_Undetected.sample(), entity.allTime))
                        entity.timestageIV = nextNat_time
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity has an undetected Stage IV cancer")
                        
                    elif nextNat_status == 5.1:                         # If the entity has symptomatic stage 4 cancer...
                        entity.diseaseDetected = 1
                        entity.cancerDetected = 1
                        entity.sympt = 1
                        entity.time_cancerDetected = nextNat_time         # The time that the entity's cancer was detected is recorded
                        entity.stateNum = 3.0                               # The entity moves to the "detected cancer" state
                        entity.currentState = "Treatment for incident oral cancer"
                        entity.allTime = nextNat_time
                        #print(entity.allTime, "the entity's Stage IV cancer has been detected symptomatically")
                
                    # Dead of Disease                       
                    elif nextNat_status == 100:                         # If the entity will die of undetected stage 4 cancer...         
                        "The model assumes that undetected terminal stage IV disease is detected before death and treated as incurable"
                        entity.diseaseDetected = 1
                        entity.diagnosed = 1
                        entity.firstcancer = 'Terminal'
                        entity.cancerDetected = 1
                        entity.time_DeadofDisease = nextNat_time          # The time of death is assigned
                        entity.stateNum = 5.0               # Entity is in the "terminal disease" health state
                        entity.currentState = "Terminal disease"                
                        entity.endOfLife = 1
                        
                        """The time of cancer detection is 90 days before death or 
                            the time that the entity progresses to stage IV, 
                            whichever comes first"""
                        if (nextNat_time - entity.timestageIV) < 90:
                            entity.allTime = entity.timestageIV
                            entity.time_diagnosed = entity.allTime
                            entity.time_cancerDetected = entity.timestageIV
                        else:
                            entity.allTime = nextNat_time - 90                # Next event is scheduled as detection 90 days before death
                            entity.time_cancerDetected = nextNat_time - 90    
                        
                    # ERROR                       
                    else:
                        entity.NEstatus = nextNat_status                    
                        entity.stateNum = 99
                        entity.currentState = "ERROR - nextNat sequencing"
                        #print("Natural History events have been improperly sequenced. Check the 'Glb_CheckTime' process and inspect 'nextNat'")
                else:
                    # Advance clock to next natural history time
                    entity.allTime = nextNat_time

        elif entity.cancerDetected == 1:
            
            if hasattr(entity, 'time_DeadofDisease'):
                time_EOL = entity.time_DeadofDisease - 90     # Disease within last 3 months of life
            else:
                time_EOL = 99999    # If entity doesn't have DoD time, insert placeholder
                
            if hasattr(entity, 'time_Recurrence'):
                pass
            else:
                entity.time_Recurrence = 99999  # If entity doesn't have recurrence time, insert placeholder

            # Check for death from oral cancer            
            if entity.allTime >= entity.time_DeadofDisease:
                entity.allTime = entity.time_DeadofDisease          # The simulation concludes with the entity's death            
                entity.time_death = entity.time_DeadofDisease       # The time of death is recorded
                entity.death_type = 1                               # The entity has died of disease
                entity.death_desc = "Dead of Disease"
                entity.stateNum = 100                               # The entity is dead
                entity.currentState = "Dead"

            # If entity has reached end of life state (last 3 months of life)               
            elif entity.allTime >= time_EOL:                    # Entity is three months from death
                entity.stateNum = 5.0               # Entity is in the "terminal disease" health state
                entity.currentState = "End of Life"                
                entity.endOfLife = 1
                
            # Next system event is scheduled after entity's death from natural causes
            elif entity.time_Sysp >= entity.natHist_deathAge:
                entity.allTime = entity.natHist_deathAge

            # Recurrence (SEE FOOTNOTE 1)             
            # If recurrence happens before the next system process event
            elif entity.time_Sysp >= entity.time_Recurrence:
                
                if entity.time_Recurrence < time_EOL:   # Recurrence occurs before EOL
                    entity.allTime = entity.time_Recurrence
                    entity.time_Recurrence = 666666     # Future recurrence set to impossible date (SEE FOOTNOTE 2)     
                    entity.recurrence = 1               # Flag entity as having active recurrence                    
                    entity.cancerStage = "Recur"        # Entity has a detected recurrence
                    entity.stateNum = 3.0               # Entity returns for diagnostic workup and possible treatment
                    entity.currentState = "Treatment for recurrence"
                    
                elif entity.time_Recurrence >= time_EOL:    # EOL occurs before recurrence
                # If entity is currently more than 3 months from death, set next system process time as EOL date
                    entity.allTime = entity.time_EOL                
                    entity.time_Recurrence = 666666     # Future recurrence set to impossible date (SEE FOOTNOTE 2)
                    entity.stateNum = 5.0               # Entity is in the "terminal disease" health state
                    entity.currentState = "End of Life"                
                    entity.endOfLife = 1
               
                # ERROR                    
                else:
                    entity.stateNum = 99
                    entity.currentState = "ERROR - recurrence has not been scheduled properly - look at Glb_Checktime.py"
                    
            # Next scheduled system process event occurs before recurrence but after EOL
            elif entity.time_Sysp >= time_EOL:
                # Advance clock to EOL
                entity.allTime = time_EOL
                entity.time_Recurrence = 666666     # Future recurrence set to impossible date (SEE FOOTNOTE 2)
                entity.stateNum = 5.0               # Entity is in the "terminal disease" health state
                entity.currentState = "End of Life"                
                entity.endOfLife = 1
                    
            # If no disease event is scheduled before next system process event
            elif entity.allTime < entity.time_Sysp:
                entity.loopcount = 0 # Reset loop counter
                entity.allTime = entity.time_Sysp
                
            elif entity.allTime == entity.time_Sysp:
                # An error in the code might cause this kind of statement to loop if neither allTime
                #   or time_Sysp change. If that happens, this will catch it and return an eror.
                if hasattr(entity, 'loopcount') == False:
                    entity.loopcount = 1
                else:
                    if entity.loopcount < 1000: # An arbitrarily high number
                        entity.loopcount += 1
                    else:
                        entity.stateNum = 99
                        entity.currentState = "ERROR - entity caught in Sysp/allTime loop - look at Glb_Checktime.py"   
            else:
                #ERROR
                entity.stateNum = 99
                entity.currentState = "ERROR - time_Sysp conflict - look at Glb_Checktime.py"                    
    
####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   time_OPL - the time that the most recent OPL has developed
#   time_Cancer - the time that the entity developed cancer
#   time_cancerDetected - the time that the entity's cancer is detected (in this case, symptomatically)
#   cancerStage - the current stage (I, II, III, IV) of the entity's cancer    
#   time_death - the time that the entity dies (in this case, of undetected disease)
#   death_type - a flag indicating the way entity died (in this case, of oral cancer)
#   death_desc - a text description of the cause of death    
#   recurrence - a flag to indicate that disease has recurred
#   endOfLife - a flag to indicate that a person has terminal disease 
#    
#
# FOOTNOTE:
#
#   1 - Because the base case of this model relies on 'time to DETECTED recurrence' data, the time at which an entity
#   DEVELOPS a recurrence is treated as synonymous to the time that recurrence is DETECTED. If this model is updated
#   with recurrence rates from natural history or a clinical trial, then "stateNum" and "cancerStage" should only be
#   updated after a follow-up appointment (i.e., in the 'SysP_Followup' program).
#
#   2 - By setting the recurrence time impossibly late, the program won't reach the point where 'allTime' is greater
#   than 'time_Recurrence'. If the person DOES experience a subsequent recurrence, 'time_Recurrence' will be reset by
#   the 'RecurTx' System Process    