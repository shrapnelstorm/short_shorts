from enum import Enum 
typ = Enum('prepare','proposal','promise','accepted','learn','update')
class Message:
    def __init__(self,typ,psn,val,round_no,command,client_no, sender, orig_psn=None)
        self.typ = typ
        self.psn = psn
        self.val = val
        self.round_no = round_no
        self.command = command
        self.client_no = client_no
		self.sender = sender
		self.orig_psn = orig_psn
    # have to define functions later 
    
class Client_Msg:
    def __init_(self,command)
        self.command = command
