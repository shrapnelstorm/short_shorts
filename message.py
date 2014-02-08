from enum import Enum 
typ = Enum('prepare','accept','promise','accepted','learner')
class Message:
    def __init__(self,typ,pnr,val,round_no,command,client_no)
        self.type = typ
        self.pnr = pnr
        self.val = val
        self.round_no = round_no
        self.command = command
        self.client_no = client_no
    # have to define functions later 
    
class Client_Msg:
    def __init_(self,command)
        self.command = command
