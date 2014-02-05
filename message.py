from enum import Enum 
typ = Enum('prepare','accept','acceptor','learner')
class Message:
    def __init__(self,typ,pnr,val,inst_number,instruction)
        self.type = typ
        self.pnr = pnr
        self.val = val
        self.inst_number = inst_number
        self.instruction = instruction
    # have to define functions later 
    
class Client_Msg:
    def __init_(self,lock_object)
        self.lock_object = lock_object
