import os
import pickle

class Lock_Status:
    def __init__(self,status,client_no):
        self.status = status
        self.client_no = client_no

class Ledger:
    def __init__(self, pnr_chosen, value_chosen, command_chosen, client_chosen):
        self.pnr_chosen = pnr_chosen
        self.value_chosen = value_chosen
        self.command_chosen = command_chosen
        self.client_chosen = client_chosen
        
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
	    self.ledger.append(ledger_instance)
	    
	def update_accepted(self,accepted_instance):
	    self.accepted.append(accepted_instance)
	    
	    
s = ServerData(10)
s.update_ledger(Ledger(8,67,34,2))
s.update_accepted(3)
s.save()
if os.path.isfile('10.sav'):
    print 'works'

