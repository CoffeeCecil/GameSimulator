# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 22:33:53 2018

@author: admin
"""


class EventList(list):
    
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)
            
    def __repr__(self):
        return "Event list: {}".format(list.__repr__(self))

class InitiativeEngine(list):
    """
    Initiative engine:
        How it works:
        Append and insert
    """

    def __init__(self, lst=[], invariant= lambda x: x[0], callf=lambda x:str(x[1]())):
        super().__init__()
        for item in lst:
            self[len(self):] = [item]
        self.invariant=invariant
        self.callf=callf
        self.callidx=None
        self.remlist=[]
        self.updatelist=[]
        self.__idctr = 0
        self.paused = False
        if len(self) == 0:
            return
        else:
            self.sort(key=self.invariant)
    
    def __incrID(self):
        self.__idctr +=1
        
    def __getID(self):
        idx = self.__idctr
        self.__incrID()
        return idx
    
    def append(self, item, priority=None):
        if priority == None:
            self[len(self):] = [ (item[0], item[1], self.__getID()) ]
        else:
            self[len(self):] = [ (priority, item, self.__getID()) ]
        
        self.sort(key=self.invariant)
    
    
    """
    Items sometimes need to be added to the list.
    In order to facilitate this, an add list is kept.
    This list stores each item as (priority, item) pairs.
    
    Each item includes an id which is kept so that it may be indexed.
    When an update is triggered all items in the update list are added to
    the list itself.
    
    The list is then
    """
    def queuAtBack(self, item, default_value=0):
        if len(self.updatelist):
            self.updatelist.append( (self.updatelist[len(self.updatelist)-1 ][0] + 1, item ))
        else:
            self.updatelist.append(default_value, item)
            
    def queuAtFront(self, item, default_value=0):
        if len(self.updatelist):
            self.updatelist=[ (self.updatelist[0][0]-1,  item)].extend(self.updatelist)
        else:
            self.updatelist.append(default_value, item)
    
    def queuToUpdate(self, item, priority=None):
        if priority==None:
            self.updatelist.append(item)
        else:
            self.updatelist.append((priority, item))

    def triggerUpdate(self):
        lprev = len(self)#retrieve the previous length of the list
        idx = self.callidx
        #Establish if the index is less than the size of the list
        if idx < lprev:
            item = self[self.callidx]
        else:
            item = None
        #insert every item in the update list into this list
        for each in self.updatelist:
            self.superinsert( each[1], each[0] )
        self.updatelist.clear()
        #Clear the update list.
        if(item):
            self.callidx = self.index(item)
            return
#        if self.callidx == None:
#            return
#        if self.callidx == lprev:
#            self.callidx = 0
#            return
        self.callidx= None
                            
    def triggerRemove(self):
        idx = self.callidx#the index is the next item to call.
        i = 0
        def top():
            return self.remlist[len(self.remlist)-1]
        while len(self.remlist):#while the remove list has items
            i = self.index(top())#find the index of the top item in the remove list.
            self.remove(self.remlist.pop())
            if idx:
                if i < idx:
                    idx-=1#if it is less than the index, decrement the index.
                if i == idx:#if it is equal to the index, set the index to be the next item.
                    if len(self):
                        idx = min(len(self) - 1, idx + 1)
                    else:
                        idx=None
                        break
        self.callidx=idx
            
    def superinsert(self, item, superposition=0):
        """
        superinsert:
            input: an item and a super position
            effect:
                finds the first matching invariant in the list.
                places the item just before that invariant.
        """
        i = 0
        for each in self:
            if self.invariant(each) < superposition:
                i+=1
            else:
                break
        super().insert(i, (superposition, item, self.__getID()) )
        return self
        
        
    def insert(self, item, position=0):
        """
        insert:
            input: an item and a position.
            effect: places before the item at the indicated position.
            item is emplaced with a priority of the item at the indicated position.
            If the list is empty, gives a priority of position to the item.
            If the list length is given as position, inserts the item as though it was appended.
            The priority of the list will be equal to the priority of the last item,
            since it is invariant managed.
        """
        if(len(self))==0:
            self[len(self):] = [(position, item, self.__getID())]
            return
        if(len(self)==position):
            self[len(self):] = [ (self.invariant(self[position-1]) , item, self.__getID())]
            return
        p = position % len(self)
        v = self.invariant(self[p])
        super().insert(p, (v, item, self.__getID()))
        
    def __call_loop__(self):
        r = self.callf(self[self.callidx])
        
        if "kill" in r:
            self.remlist.append(self[self.callidx])
        if "end" in r:
            self.paused = False
            self.remlist.extend([x for x in filter( lambda x: x != self[self.callidx], self)])
            self.callidx = None
            return True
        if self.callidx != None:
            self.callidx+=1            

        if "stop" in r:
            self.paused = True
            return True
        return False
        
    def __call__(self):
        self.callidx = 0
        self.remlist.clear()
        self.paused = False
        """
        The initiative queue is called.
        It runs through each item, calling it with the callf function.
        The callf function is expected to return a string.
        If it is stop, the list stops its initiative count.
        If it is kill, the list removes the object to be killed from itself.
        
        Call and it's brother resume DO NOT clean up the initiative list.
        
        """
        
        while self.callidx < len(self):
            if self.__call_loop__():
                break

        #
        if len(self.updatelist):
            self.triggerUpdate()
        if len(self.remlist):
            self.triggerRemove()
        if (self.callidx != None) and (self.callidx > len(self)) :
            self.callidx=None

    def clear(self):
        del self[:]
        self.callidx = None
            

        
    def resume(self):
        """Resume is a function to resume operation on the initiative engine
        without restarting it. This way the engine can be paused to handle
        exceptional conditions.
        
        Call and it's brother resume DO NOT clean up the initiative list.
        """
        if self.callidx==None:
            raise(RuntimeError("Initiative resumed before it started."))
        if self.callidx > len(self):
            raise(RuntimeError("Size of running index larger than size of list!"))
        if self.callidx == len(self):
            self.callidx=0
        
        self.paused = False
        while self.callidx < len(self):
            r = self.callf(self[self.callidx])
            if "kill" in r:
                self.remlist.append(self[self.callidx])
            if self.callidx != None:
                self.callidx+=1
            if "stop" in r:
                self.paused=True
                break
            if "end" in r:
                self.paused=False
                break
       
        if len(self.updatelist):
            self.triggerUpdate()
        if len(self.remlist):
            self.triggerRemove()
        if(self.callidx != None and self.callidx > len(self)) :
            self.callidx=None
