# -*- coding: utf-8 -*-
"""
Apply initial demographic characteristics to a newly-created entity
"""

############################################################################################
# Load some necessary packages and functions
import random
import pickle
import numpy

############################################################################################

"Assign a date of natural death"
with open('deathm.pickle', 'rb') as f:  # Load previously-created arrays
    deathage_M = pickle.load(f)
with open('deathf.pickle', 'rb') as f:
    deathage_F = pickle.load(f)

class ApplyInit:
    def __init__(self, estimates):
    
        self._estimates = estimates
        
        self.alcprevM = estimates.Prev_alcohol_M.sample()
        self.alcprevF = estimates.Prev_alcohol_F.sample()
        self.smokeprevM = estimates.Prev_smoking_M.sample()
        self.smokeprevF = estimates.Prev_smoking_F.sample()
        self.dentprev = estimates.Prev_dentist.sample()
        self.compliance = estimates.Screen_compliance.sample()

    def Process(self, entity):
        # A function to apply the initial characteristics to each person"
        
        # Starting age is applied randomly between 35 and 75 years"    
        # entity.startAge = random.randint(35,75) + random.random()
        
        # Starting age is sampled from normal distribution
        entity.startAge = self._estimates.Prev_startage.sample()
        
        # Sex: 1 = female, 0 = male
        makeSex = random.random()
        if makeSex < 0.5:
            entity.sex = 'F'
        else:
            entity.sex = 'M'
        
        # Smoking status: 1 = ever smoker, 0 = never smoker
        # Alcohol use: 1 = heavy user, 0 = not heavy user
        makeSmoker = random.random()
        makeAlc = random.random()
        
        if entity.sex == 'M':
            if makeSmoker < self.smokeprevM:
                entity.smokeStatus = 'Ever'
            else:
                entity.smokeStatus = 'Never'

            if makeAlc < self.alcprevM:
                entity.alcStatus = 'Heavy'
            else:
                entity.alcStatus = 'Nonheavy'
                
        elif entity.sex == 'F':
            if makeSmoker < self.smokeprevF:
                entity.smokeStatus = 'Ever'
            else:
                entity.smokeStatus = 'Never'
        
            if makeAlc < self.alcprevF:
                entity.alcStatus = 'Heavy'
            else:
                entity.alcStatus = 'Nonheavy'
            
        "Access to a dentist: 1 = yes, 0 = no"
        makeDentist = random.random()
        if makeDentist < self.dentprev*self.compliance:
            entity.hasDentist = 1
        else:
            entity.hasDentist = 0

        "Entities start asymptomatically, at t0"
        entity.OPLStatus = 0
        entity.hasCancer = 0
        entity.diseaseDetectable = 0
        entity.diseaseDetected = 0
        entity.cancerDetected = 0
        entity.utility.append(("Well", self._estimates.Util_Well.sample(), 0.0))
        
        if entity.sex == 'F':  
            nh_deathage = numpy.random.choice(deathage_F) + random.random()         # Sample an age at death from natural causes
        elif entity.sex == 'M':
            nh_deathage = numpy.random.choice(deathage_M) + random.random()
        nh_deathspan = nh_deathage - entity.startAge                     # Calculate the amount of time remaining before entity creation and death
        entity.natHist_deathAge = abs(nh_deathspan)*365        # Convert years to days

        "Assign OPL status based on age- and sex-adjusted prevalence estimates"

        if entity.sex == 'F':                         # Women, by age category

            if entity.startAge < 50:
                entity.probOPL = self._estimates.NatHist_prevOPLunder50f.sample()
            elif 50 <= entity.startAge < 60:
                entity.probOPL = self._estimates.NatHist_prevOPL5059f.sample()
            elif 60 <= entity.startAge < 70:
                entity.probOPL = self._estimates.NatHist_prevOPL6069f.sample()
            elif 70 <= entity.startAge < 80:
                entity.probOPL = self._estimates.NatHist_prevOPL7079f.sample()
            elif 80 <= entity.startAge:
                entity.probOPL = self._estimates.NatHist_prevOPL80plusf.sample()

        elif entity.sex == 'M':                       # Men, by age category

            if entity.startAge < 50:
                entity.probOPL = self._estimates.NatHist_prevOPLunder50m.sample()
            elif 50 <= entity.startAge < 60:
                entity.probOPL = self._estimates.NatHist_prevOPL5059m.sample()
            elif 60 <= entity.startAge < 70:
                entity.probOPL = self._estimates.NatHist_prevOPL6069m.sample()
            elif 70 <= entity.startAge < 80:
                entity.probOPL = self._estimates.NatHist_prevOPL7079m.sample()
            elif 80 <= entity.startAge:
                entity.probOPL = self._estimates.NatHist_prevOPL80plusm.sample()
            
        # Prevalence conversion factor for calibration
        entity.probOPL = entity.probOPL*self._estimates.NatHist_prevOPLconversion.sample()


        "Update state"
        
        entity.currentState = "Initial Characteristics Applied"
        entity.stateNum = 0.1


####################################################
# VARIABLES CREATED IN THIS STEP:
#
#   startAge - the entity's age at the beginning of the model
#   sex - the entity's binary sex (1: female; 0: male)
#   smokeStatus - whether the entity is a never or ever smoker (1: ever; 0: never)
#   alcStatus - whether or not the entity is a heavy alcohol user (1: yes; 0: no)
#   OPLStatus - whether or not the entity has an active OPL (1: yes; 0: no)
#   hasDentist - whether or not the entity has a dentist who performs screening tests (1: yes; 0: no)
#   hasCancer - whether or not the entity has an active cancer (1: yes; 0: no)
#   diseaseDetected - whether or not the entity has a premalignancy or a cancer that has been detected (1: yes; 0: no)
#   cancerDetected - whether or not the entity has a cancer that has been detected (1: yes; 0: no)
#   natHist_deathAge - the age at which the entity will die of natural causes
#   probOPL - the probability that the entity starts the simulation with a premalignancy