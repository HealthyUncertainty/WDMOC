# -*- coding: utf-8 -*-
"""
A screening process wherein a person returns for regular checkups at a dentist.

The person comes to the dentist on a regular basis for ordinary checkups.

A healthy person (no OPL) may have another kind of lesion and generate a false
positive. If they do, they are asked to return in three weeks. If the lesion persists
then they are referred to a specialist. The specialist will evaluate the lesion and
may biopsy it if it seems supicious (OPLs are assumed to be suspicious). People with
negative biopsy results and/or benign lesions return for routine dental care.

A person who has an asymptomatic premalignancy or cancer may have it detected during 
an ordinary visit, based on the sensitivity of an ordinary exam. If it is detected, 
then the person is referred to a periodontist for a biopsy (which will be positive). 
They will proceed to the "OPL Management" stage at that point.

"""

import random

class ScreenAppt:
    
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
        
        self.anyLesion = estimates.Screen_anylesion.sample()
        self.appInt = int(estimates.Screen_appint.sample())
        self.screenReturnInt = estimates.Screen_returnint.sample()
        self.willReturn = estimates.Screen_willreturn.sample()
        self.lesionResolves = estimates.Screen_lesionresolves.sample()
        self.detectOPL = estimates.Screen_sensitivity.sample()
        self.needsBiopsy = estimates.Screen_needsbiopsy.sample()
        
    def Process(self, entity): 
    
        if hasattr(entity, "count_DentAppt") == False:              # If this person doesn't already have the 'DentAppt' field created, create it for them
            entity.count_DentAppt = 0                               # Start the tally of appointments at zero
            entity.count_ScreenAppt = 0
            entity.count_ScreenInt = 0                              # Start a count for the screening interval
            entity.screenReturn = 0                                 # Is entity returning from previous lesion
            entity.screened = 1
            
        if hasattr(entity, "flsPosCount") == False:
            entity.flsNegCount = 0
            entity.flsPosCount = 0
            
        if entity.time_Sysp > entity.allTime:
            # Have not yet reached next system process event, do nothing
            pass
    
        else:
            # A person comes for a regular appointment at the dentist
            entity.resources.append(("Dental Appointment", entity.allTime))  # Add dentist appointment into resources list
            entity.count_DentAppt = entity.count_DentAppt +1
            
            if entity.OPLStatus == 1:
                if entity.screenReturn == 0:
                    detectDisease = random.random()
                    if detectDisease < self.detectOPL:
                        # An additional screening cost may be incurred
                        entity.resources.append(("Cancer Screening", entity.allTime))
                        # OPL is detected, person is asked to return
                        entity.screenReturn = 1
                        entity.time_Sysp += self.screenReturnInt
                    else:
                        # False negative
                        entity.events.append(("False negative", entity.allTime))
                        entity.flsNegCount += 1
                        entity.time_Sysp += self.appInt
                
                else:
                    # Assume that persistent lesions go for biopsy
                    # An additional screening cost may be incurred
                    entity.resources.append(("Cancer Screening", entity.allTime))
                    entity.resources.append(("Specialist Appointment", entity.allTime))
                    entity.resources.append(("Biopsy", entity.allTime))
                    
                    if entity.hasCancer == 0:
                        entity.events.append(("OPL Diagnosed", entity.allTime))
                        entity.OPLDetected = 1
                        entity.OPL_screenDetected = 1
                        # The time at which an OPL is detected
                        entity.time_OPLDetected = entity.allTime                           
                        entity.stateNum = 2.0                    
                        entity.currentState = "2.0 - OPL Detected"
                        entity.utility.append(("Detected OPL", self._estimates.Util_OPL_Detected.sample(), entity.allTime))
                        
                    else:
                        entity.events.append(("Cancer First Detected", entity.allTime))
                        entity.cancer_screenDetected = 1
                        entity.cancerDetected = 1
                        # The time at which the entity's cancer was detected
                        entity.time_cancerDetected = entity.allTime                           
                        entity.stateNum = 3.0
                        entity.currentState = "3.0 - Invasive cancer detected"
                # END DISEASE-POSITIVE APPOINTMENT
                        
            else:
                if entity.screenReturn == 0: # Regular appointment
                    hasLesion = random.random() # A non-premalignant lesion may be present
                    if hasLesion < self.anyLesion:
                        # Non-premalignant lesion may be recommended to return
                        # An additional screening cost may be incurred
                        entity.resources.append(("Cancer Screening", entity.allTime))
                        willReturn = random.random()
                        if willReturn < self.willReturn:
                            entity.screenReturn = 1
                            entity.time_Sysp += self.screenReturnInt
                        else:
                            # Lesion is deemed insignificant, or person does not return when recommended
                            entity.time_Sysp += self.appInt
                    else:
                        # Entity has no lesion of any kind
                        entity.time_Sysp += self.appInt
                
                else:
                    entity.screenReturn = 0     # Entity is returning, screenReturn status is reset
                    # Has lesion resolved?
                    lesionResolved = random.random()
                    if lesionResolved < self.lesionResolves: # Lesion persists
                        # An additional screening cost may be incurred
                        entity.resources.append(("Cancer Screening", entity.allTime))                
                        # Refer to specialist for further screening
                        entity.resources.append(("Specialist Appointment", entity.allTime))                    
    
                        biopsyLesion = random.random()
                        if biopsyLesion < self.needsBiopsy: # non-OPL is suspicious
                            entity.flsPosCount += 1
                            # Add biopsy into resources list
                            # Add false positive to the events list
                            entity.resources.append(("Biopsy", entity.allTime))              
                            entity.events.append(("False positive", entity.allTime))
                        else:
                            pass                            
                        entity.time_Sysp += self.appInt
                    
                    else:
                        # Lesion does not warrant biopsy or has resolved
                        pass
                        entity.time_Sysp += self.appInt
            # END DISEASE NEGATIVE APPOINTMENT
            

# VARIABLES CREATED IN THIS STEP:
    # time_OPL - the time that the entity develops an OPL
    # time_detectOPL - the time that an OPL is detected by a dentist

