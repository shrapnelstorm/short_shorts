import os
import pickle

class Lock_Status:
    def __init__(self,status,client_no):
        self.status = status
        self.client_no = client_no

class Ledger:
    def __init__(self, round_no, pnr_chosen, value_chosen, command_chosen, client_chosen):
        self.pnr_chosen = pnr_chosen
        self.value_chosen = value_chosen
        self.command_chosen = command_chosen
        self.client_chosen = client_chosen
		self.round_no = round_no
        
class ServerData:
	def __init__(self, server_id):
		self.file_name = str(server_id) + ".sav"
		if os.path.isfile(self.file_name):
			# if file exists with server_id then load from file
			self.load()
		else:
			self.ledger = []
			self.accepted = []
	def save(self):
	    with open(self.file_name,'wb') as output:
	        pickle.dump([self.ledger,self.accepted],output,-1)
	        
	def load(self):
	    with open(self.file_name,'rb') as input:
	        [self.ledger,self.accepted] = pickle.load(input)
	        
	def update_ledger(self,ledger_instance):
		while len(self.ledger) < ledger_instance.round_no:
			self.ledger.append(None)
	    self.ledger[ledger_instance.round_no] = ledger_instance
	    
	def update_accepted(self,accepted_instance):
		while len(self.accepted) < accepted_instance.round_no:
			self.accepted.append(None)
	    self.accepted[accepted_instance.round_no] = accepted_instance
	#def inconsistent(self, round_no):
		#return (len(self.ledger)+1 < round_no)
	    
	    
s = ServerData(10)
s.update_ledger(Ledger(8,67,34,2))
s.update_accepted(3)
s.save()
if os.path.isfile('10.sav'):
    print 'works'

