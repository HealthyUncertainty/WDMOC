# -*- coding: utf-8 -*-
"""
A program to handle the age- and sex-specific mortality from undetected stage IV cancer.

This program was created separately to reduce the bulkiness of 'Glb_CheckTime.py'.

@author: icromwell
"""

class StageIVDeath:
    def __init__(self, estimates):
        self._estimates = estimates
        
        self.munder50 = estimates.NatHist_timeStagefour_deathunder50m.sample()
        self.m5059 = estimates.NatHist_timeStagefour_death5059m.sample()
        self.m6069 = estimates.NatHist_timeStagefour_death6069m.sample()
        self.m7079 = estimates.NatHist_timeStagefour_death7079m.sample()
        self.m80plus = estimates.NatHist_timeStagefour_death80plusm.sample()
        self.funder50 = estimates.NatHist_timeStagefour_deathunder50f.sample()
        self.f5059 = estimates.NatHist_timeStagefour_death5059f.sample()
        self.f6069 = estimates.NatHist_timeStagefour_death6069f.sample()
        self.f7079 = estimates.NatHist_timeStagefour_death7079f.sample()
        self.f80plus = estimates.NatHist_timeStagefour_death80plusf.sample()       

    def GenDTime(self, entity, stIVage):
        
        if entity.sex == 'F':                         # Women, by age category

            if stIVage < 50:
                time_death = self.funder50
            elif 50 <= stIVage < 60:
                time_death = self.f5059
            elif 60 <= stIVage < 70:
                time_death = self.f6069
            elif 70 <= stIVage < 80:
                time_death = self.f7079
            elif 80 <= stIVage:
                time_death = self.f80plus

        elif entity.sex == 'M':                       # Men, by age category

            if stIVage < 50:
                time_death = self.munder50
            elif 50 <= stIVage < 60:
                time_death = self.m5059
            elif 60 <= stIVage < 70:
                time_death = self.m6069
            elif 70 <= stIVage < 80:
                time_death = self.m7079
            elif 80 <= stIVage:
                time_death = self.m80plus
                
        return time_death