# -*- coding: utf-8 -*-
"""
A function to generate Time-to-Event estimates from competing risk models.

The program does the following:

    1 - Draws a random value for "Time to Next Event" from a parametric estimation
        of the survival function of any event occurring.
        
    2 - Estimates the probability of that value occurring within the first event
        curve
        
    3 - Estimates the probability of that value occurring within a second event
        curve (containing the competing risk)
        
    4 - Calculates the relative probability that the event that occurs is the
        competing event
        
    5 - Evaluates the relative probability against a randomly-drawn probability.
        If the random value is less than the relative probability, then the
        event that occurs is the competing risk.
    
    6 - Returns the event time and the type of event

@author: icromwell
"""

from Glb_GenTime import GenTime
import random

class CompTime:
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
        self.probEst = random.random()
        
    def Process(self, entity, tte1, tte2):
        # Draw two survival functions for the entity
        event1 = GenTime(self._estimates, self._regcoeffs)
        event2 = GenTime(self._estimates, self._regcoeffs)
        # Any event
        event1.readVal(entity, str(tte1))
        # Competing event
        event2.readVal(entity, str(tte2))
        
        # 1 - Draw random value for time to next event        
        event_time = event1.estTime()
        # 2 - Estimate probability of that value occurring within first event
        prob1 = 1 - event1.estProb(event_time)
        # 3 - Estimate probability of that value occurring within second event
        prob2 = 1 - event2.estProb(event_time)
        # 4 - Calculate relative probability that event is the competing event
        event_prob = prob2/prob1
        # 5 - Evaluate relative probability against random probability
        if self.probEst < event_prob:
            event_type = 2
        elif self.probEst >= event_prob:
            event_type = 1
        else:
            entity.stateNum = 99
            entity.currentState = "Error - something has gone wrong in Glb_CompTime"
        
        return (event_time, event_type)
        