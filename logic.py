# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 14:26:43 2018

@author: Cecil Hutchings

This file contains the logic system of the generative simulator.

"""

"""


Goal: Impliment a rule system to paralyze a character. 
The character will be incapable of taking turns for up to 5 rounds.
If the character is hit by a second effect, it has a 66% chance of failing
and a 33% chance of extending the paralysis.

The system must also be extensible, meaning other effects can be added.

Strategy:

There needs to be a:
    character description x
    A listing of effects associated with the character. x Done
    A way of introducing effects to the character. x Done 
    A list of rules that is evaluated as the character interacts with contexts. x
    An initiative engine for the given context (for simulation steps.) x 
    
"""

from collections import defaultdict
from copy import deepcopy

class ConditionTable(defaultdict):
    """
    A condition table records all conditions.
    All conditions effecting the character are unique, they have a duration
    and a list of arguments.
    """
    def __init__(self):
        super(defaultdict, self).__init__()
        self.default_factory = lambda: [0] #Every conditiond has a list containing its duration as the first element.
        self.purge_list=[]#Manage removal of unneeded table objects with this list.
    """
    makeCondition:
    Takes a label, a duration, and a list of optional arguments.
    Creates new condition correctly.
    If a dictionary {"max":val} is included in the arguments to the function,
    limits the maximum value the function can be set to.
    This dictionary will be removed, and not included as an argument to the function.
    
    """
    def makeCondition(self,label="test", duration=0, *optional):

        extend=0
        if self[label][0]:
            extend = self[label][0]
        def filter_func(x):
            try:
                return "max" in x.keys()
            except:
                return False
        
        def exclude_func(x):
            try:
                return not "max" in x.keys()
            except:
                return True
        
        maxval = [x for x in filter( filter_func ,  optional)]
        op=optional
        if maxval:
            newduration = min(duration+extend, maxval[0]["max"])
            op = [x for x in filter(exclude_func, optional )]
        else:
            newduration = duration + extend
        l = [newduration]
        l.extend(op)

        self[label]= l
        
        
    """
    hasCondition:
    Checks to see if the target has a condition matching the label with the 
    duration threshold.
    """
    def hasCondition(self, label, duration_threshhold=1):
        if not label in self:
            return False
        if self[label][0] < duration_threshhold:
            return False
        return True
    
    """
    Easy increment and decrement for durations.
    """
    def decrDuration(self, label, value):
        self[label][0]= self[label][0]-value
        
    def incrDuration(self, label, value):
        self[label][0]= self[label][0]+value
        
    def duration(self, label):
        return self[label][0]
        
    """
    Return a list containing the meta information of the object.
    The metadata is the information other than the duration of the list.
    """
    def metadata(self,label):
        return self[label][1:]
    """
    enques a label to be purged if it is in the condition table.
    if it is not in the condition table raises a runtime error.
    if it is in the condition table does nothing.
    """    
    def enquePurge(self,label):
        if label in self:
            if label not in self.purge_list:
                self.purge_list.append(label)
        else:
            raise(RuntimeError("Unexpected Condition. Not in logic table."))
    """
    for every item in the purge list, attempts to delete the item.
    """
    
    def purge(self):
        if self.purge_list==[]:
            return
        for each in self.purge_list:
            del self[each]
        self.purge_list.clear()

    def clear(self):
        for each in self.keys():
            self.enquePurge(each)
        self.purge()
    
class LogicTable(dict):
    def __init__(self):
        super(dict,self).__init__()
    """
    The logic table is very simple.
    For each condition in the table, apply the array of arguments
    to the value.
    """
    def checkCondition(self,condition_tbl):
        for key, value in condition_tbl.items():
            if key in self:
                self[key](value)
        condition_tbl.purge()
             
                
    
class CharacterLogic(LogicTable):
    """
    Character logic checks to see if the character has any logical effects
    applied to them at the beginning of this turn.
    
    Unlike the normal logic table, this one calls a function with the character
    as its first argument and the values of the effect in the second argument.
    """
    def __init__(self, game_character=None):
        super(dict,self).__init__()
        if not game_character:
            raise(RuntimeError("Supply an object with the value"))
        self.uid = game_character
        
    """
    
    """
        
    def checkCondition(self):
        for key, value in self.uid.etable.items():
            if key in self:
                self[key](self.uid, *value)        
        self.uid.etable.purge()
                

def paralysis(char, duration, inflictor=None, minvalue=0, printer=[], label="paralysis"):
    """
    When the paralysis logical condition is found, call this corresponding function.
    The logical test for paralysis is the string paralysis.
    
    """
    char.wasparalyzed=False#The character has not been immediately paralyzed.
    if not inflictor or not inflictor.wasparalyzed:
        if duration > minvalue:    
            if inflictor:
                printer.append("{} paralyzed {}!".format(inflictor.label, char.label))
            else:
                printer.append("{} struggles with paralysis!".format(char.label))
            char.etable.decrDuration(label, 1)
            if not char.canmove:        
                return
            else:
                char.canmove=False
                return
        else:
            printer.append("{} broke paralysis!".format(char.label))
            char.etable.enquePurge(label)

        char.canmove=True
    #Remove triggering effect from dictionary.

def attack(char, damage, inflicting_character, printer=[]):
    if not inflicting_character.wasparalyzed:
        char.etable.enquePurge("attack")
    char.hp -= damage
    printer.append("{} took {} damage due to {}'s attack!".format(char.label, damage, inflicting_character.label))

def miss(char, duration, target, withaction=None, printer=[]):
    char.etable.enquePurge("miss")
    printer.append("{} used {} but missed {}!".format(char.label, withaction, target.label))


def applyParalysisSkeleton(char, chance_effect, chance_stack,rng, magnitude_func, max_value):
    if rng() > (chance_effect*char.resist):
        return
    
    if "paralysis" not in char.etable:
        char.etable["paralysis"] = [magnitude_func()]
        return
    
    if rng() > (chance_stack*char.resist):
        return
    
    char.etable["paralysis"][0] = min(char.etable["paralysis"][0] + magnitude_func(), max_value)
    
