# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 15:27:20 2018

@author: admin
"""

import logic
import random as rmod

class character():
    
    def __init__(self):
        self.etable = logic.ConditionTable()
        self.logic_table = logic.CharacterLogic(self)
        self.canmove=True
        self.initiative=0
        self.resist = 1 #Character is fully effected by attacks.
        self.hp=10
        self.target_list=None
        self.actions=["attack", "paralyze"]
        self.label="Character {}".format(rmod.randint(1,1000))
        self.wasparalyzed=False
        
    def rollInitiative(self):
        
        self.initiative = rmod.randint(1,10)
        
    def turn(self):
        if self.canmove and (self.hp > 1) and not self.wasparalyzed:
            target=rmod.choice(self.target_list)
            act = rmod.choice(self.actions)
            hit = False
            tohit = rmod.randint(1,100)
            if act == "attack":
                if tohit >=50:
                    hit = True
                    target.etable.makeCondition("attack", rmod.randint(1,3), self)
            if act == "paralyze":
                if tohit >=1:
                    hit=True
                    target.etable.makeCondition("paralyze", rmod.randint(1,5), self, 0, {"max":5})
                    target.wasparalyzed=True
                    target.canmove=False
            if not hit:
                self.etable.makeCondition("miss",1, target, act)
    
    def __call__(self):
        self.turn()
        return "kill"
    