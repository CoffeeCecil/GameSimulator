# -*- coding: utf-8 -*-

import unittest
import character
import logic
import initiative
import copy

class TestLogic(unittest.TestCase):
    def setUp(self):
        #Chance that power will effect character.
        self.t_effect = 0.5
        #Chance that effect will stack.
        self.t_stack = 0.25
        #max duration
        self.t_duration = 5
        self.t_resist = 0.5
        self.t_mag = lambda: 1
        
    def testParalysis(self):
        char_one = character.character()
        char_one.resist = self.t_resist
        char_one.logic_table["paralysis"]= lambda a,b,: logic.paralysis(a,b)
        
        #Test : make sure that paralysis doesn't happen.
        t1= lambda: .51
        #Test : make sure that paralysis does happen.
        t2 = lambda: .49
        #Test : make sure resistances work.
        #Test : make sure that paralysis doesn't stack.
        #Test : make sure it does stack.
        t3 = lambda: .24
        t4 = lambda: .12
        #Test : make sure the maximum value is five.
        #Test : Make sure that it decrements to zero.
        #Test : Make sure paralysis will remove itself from the character's effect table.
        
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t1, self.t_mag,  self.t_duration)
        self.assertNotIn("paralysis", char_one.etable)
        
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t2, self.t_mag,  self.t_duration)
        self.assertNotIn("paralysis", char_one.etable)
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t3, self.t_mag,  self.t_duration)
        self.assertIn("paralysis", char_one.etable)
        self.assertEqual(1, char_one.etable["paralysis"][0])
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t3, self.t_mag,  self.t_duration)
        self.assertEqual(1, char_one.etable["paralysis"][0])
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t4, self.t_mag,  self.t_duration)
        self.assertEqual(2, char_one.etable["paralysis"][0])
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t4, self.t_mag,  self.t_duration)
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t4, self.t_mag,  self.t_duration)
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t4, self.t_mag,  self.t_duration)
        logic.applyParalysisSkeleton(char_one,  self.t_effect ,self.t_stack, t4, self.t_mag,  self.t_duration)
        self.assertEqual(5, char_one.etable["paralysis"][0])
        char_one.logic_table.checkCondition()
        self.assertFalse(char_one.canmove)
        self.assertEqual(char_one.etable["paralysis"][0], 4)
        char_one.logic_table.checkCondition()
        char_one.logic_table.checkCondition()
        char_one.logic_table.checkCondition()
        char_one.logic_table.checkCondition()
        self.assertFalse(char_one.canmove)
        char_one.logic_table.checkCondition()
        self.assertTrue(char_one.canmove)
        self.assertNotIn("paralysis", char_one.etable)
        del char_one
        
    def testInitiativeInsertion(self):
        x = lambda x: (x, None)
        t = [x(1), x(2), x(2), x(4), x(4), x(0), x(-1), x(3), x(-5)]
        e = [x(-5), x(-1), x(0), x(1), x(2), x(2), x(3), x(4), x(4)]
        #Testing against super insert
        e2 = [ (-10, '*'),x(-5), x(-1), (0, '*'), x(0), x(1), x(2), x(2), (3,'*'), x(3), x(4), x(4), (5,'*'), (7,'*')]
        #Testing against insert
        e3 = [ (-5, '*'), x(-5), x(-1), (0, '*'), x(0), x(1), x(2), x(2), x(3), (4, '*'), x(4),  (4,'*'), x(4), (4,'*')]
        #Test creating the list raw.
        #Test creating the list empty
        eng = initiative.InitiativeEngine(t)
        self.assertListEqual(eng, e)
        
        eng = initiative.InitiativeEngine()
        for each in t:
            eng.append(each)
        
        def assertDataEqual(en, testdata):
            [ self.assertEqual( (each[0], each[1]), every) for each, every in zip(en, testdata) ]
        
        assertDataEqual(eng, e)

        eng.superinsert('*', 7)
        eng.superinsert('*', 5)
        eng.superinsert('*', 3)
        eng.superinsert('*', 0)
        eng.superinsert('*', -10)
        
            
        assertDataEqual(eng, e2)    
        #self.assertListEqual(eng, e2)
        eng.clear()
        eng.superinsert(None, 1)
        assertDataEqual(eng, [(1, None)])
        #self.assertListEqual(eng, [(1, None)])
        eng = initiative.InitiativeEngine(e)#Reload with expected, sorted values.
        eng.insert('*', 0 )
        eng.insert('*', -2 )
        eng.insert('*', 3)
        eng.insert('*', len(eng)-1)
        eng.insert('*', len(eng))
        assertDataEqual(eng, e3)
        #self.assertListEqual(eng, e3)
        
    def testClear(self):
        eng = initiative.InitiativeEngine()
        eng.append(None, 1)
        eng.append(None, 2)
        eng.callidx = 1000
        eng.clear()
        self.assertEqual(len(eng), 0)
        self.assertEqual(eng.callidx, None)
        
    def testRun(self):
        eng = initiative.InitiativeEngine()
        t = []
        
        l = [lambda: t.append(0)]
        l.append(lambda: t.append(1))
        l.append(lambda: t.append(2))
        l.append(lambda: t.append(3))
        l.append(lambda: t.append(4))        
        lp = [1,3,0,2,200]
        r = [2, 0, 3, 1, 4]

        for each, every in zip(l, lp):

            eng.append(each,every)
        eng()
        self.assertListEqual(t, r)
        #P
        #
        #
        eng.clear()
        t.clear()
        t.extend([0,0,0,0])
        
        def stat():
            t[0]+=1
            if t[0] > 10:
                return "kill"
        
        def resume():
            t[2]+=1
            return "stop"
        
        def kill():
            t[1]+=1
            return "kill"
        
        def update():
            eng.queuToUpdate(kill, -1)
            eng.queuToUpdate(kill, 2)
            eng.queuToUpdate(kill, 10)
            
        
            
        def monitor():
            if t[0] > 10:
                return ("kill","stop")

        eng.append(monitor, 0)
        m = eng[0]
        eng.append(stat, 1)
        eng.append(stat, 2)
        eng.append(kill, 3)
        eng.append(resume, 4)
        eng.append(update, 5)
        #Shows how calls can be run repeatedly
        while m in eng:
            if eng.callidx == None:
                eng()
            else:
                t[3]+=1
                eng.resume()
            if t[0] > 20:
                break
        print( "If monitor is set to 10, and there are  2 stat objects, should stop at 12")
        self.assertEqual(t[0], 12)
        print("Kill should kill itself sixteen times.")
        self.assertEqual(t[1], 17, )
        print("Should have stopped 6 times.")
        self.assertEqual(t[2], 6)
        print("Should have resumed as many times as it stopped.")
        self.assertEqual(t[2], t[3], )
        print("Without garbage collection should be items on the list.")
        self.assertEqual(len(eng), 4 )
        print("These items are a resume, update and 2 kill functions which could not be called.")
        self.assertEqual(len(list(filter( lambda x: x[1] == resume, eng ) )), 1)
        self.assertEqual(len(list(filter( lambda x: x[1] == kill, eng) )) , 2)
        self.assertEqual(len(list(filter( lambda x: x[1] == update, eng) )) , 1)
        
        
    def testSimulation(self):
        px = ["Start of combat!"]

        from collections import Counter
        interesting = ["Attacks", "Attack Hits", "Paralysis", 
                       "Paralysis Hits", "Actions", "Damage Dealt", 
                       "Duration Paralyzed"]
        stats = Counter({"turns":0})
        char_list = [character.character(), character.character()]        
        for each in interesting:
            for every in char_list:
                stats[every.label+each]=0
        
        eng = initiative.InitiativeEngine()

        rolled_initiative=[False]
        ms=lambda a,b,c,d: logic.miss(a, b, c, d, printer=px)
        
        pz=lambda a,b,c,d: logic.paralysis(a,b,c,d, printer=px, label="paralyze")
        
        atk= lambda a, b, c: logic.attack(a, b, c, printer=px)
        
        actions = {
                "paralyze":pz, 
                "attack":atk, 
                "miss": ms}
        #Initialize the characters. This would be better done as a factory.
        for each in char_list:
            each.logic_table.update(actions)
            f = lambda x: x != each
            each.target_list = [x for x in filter(f, char_list)]
                
        def monitor():
            
            for each in px:
                print(each)
            px.clear()
            for each in char_list:
                if each.hp < 1:
                    return ("end","kill")
            
            if not rolled_initiative[0]:
                rolled_initiative[0]=True
                for each in char_list:
                    each.rollInitiative()
                    eng.queuToUpdate(each, each.initiative + 20)
                eng.queuAtBack(countStats, len(eng))
                eng.queuAtBack(resolveActions, len(eng))
                
        def countStats():
            if rolled_initiative[0]:
                rolled_initiative[0]=False
            stats["turns"]+=1
            for each in char_list:
                for label, values in each.etable.items():
                    if label=="miss":
                        if values[2]=="attack":
                            stats[each.label +"Attacks"]+=1
                        if values[2]=="paralyze":
                            stats[each.label +"Paralysis"]+=1
                        stats[each.label +"Actions"]+=1                        
                    if label=="attack":
                        stats[values[1].label+"Attacks"]+=1
                        stats[values[1].label+"Attack Hits"]+=1
                        stats[values[1].label+"Actions"]+=1
                        stats[values[1].label+"Damage Dealt"]+=values[0]
                    if label=="paralyze":
                        if each.canmove:
                            stats[values[1].label+"Paralysis"]+=1
                        stats[each.label + "Duration Paralyzed"]+=1
                        stats[values[1].label+"Paralysis Hits"]+=1
                        stats[values[1].label+"Actions"]+=1
            return "kill"
                
        
        def resolveActions():
            for each in char_list:
                each.logic_table.checkCondition()
            return "kill"
        
        eng.append(monitor,0)
        while len(eng):
            if not eng.paused:
                eng()
            else:
                eng.resume()
        
        loser = list(filter(lambda x: x.hp<1, char_list))[0]
        winner = list(filter(lambda x: x.hp>0, char_list))[0]
        print("The winner is {}, the loser is {}, after {} turns.".format(winner.label, loser.label, stats["turns"]))
        print("Statistics")
        for each, every in sorted(stats.items(),key=lambda x: winner.label in x[0]):
            print("{} -> {}".format(each, every))
        
if __name__ == "__main__":
    unittest.main()
