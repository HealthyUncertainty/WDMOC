# -*- coding: utf-8 -*-
"""
This code creates an entity with an expandable list of characteristics.

The entity is the main simulation unit.
"""

class Entity(object):
   def __init__(self, **kwargs):
       #This step allows the class to adopt any characteristic defined within the model       
       self.__dict__.update(kwargs)
       # These variables allow you to track where the entity is within the model
           # "currentState" is a text description of the state
           # "stateNum" is used by the sequencer to determine what action to take
       self.currentState = "Newly created entity"
       self.stateNum = 0.0
       
       # "allTime" is a running counter of the amount of time elapsed within the simulation (i.e., survival time)
       self.allTime = 0
       
       # "syspTime" denotes the time at which the next system process is scheduled to occur
       self.time_Sysp = 0       
       
       # "nh_" refers to Natural History processes used in the "NatHist" programs to set out the 
       self.nh_status = 0.0
       self.nh_time = 0
       self.nh_det = 0
       
       # Create lists to hold natural history, events, resources, and utility data
       self.natHist = []
       self.resources = []
       self.events = []
       self.utility = []


# VARIABLES CREATED IN THIS STEP:
    # currentState - a text decription of where the entity is within the model
    # stateNum - A numerical representation of where the entity is within the model
    # allTime - The amount of time that has elapsed in the simulation
    # nh_status - a variable used to guide the trajectory of the natural history process
    # nh_time - a variable used to sequence the events in the natural history process
    # nh_det - a flag to identify the point at which disease will be detected naturally