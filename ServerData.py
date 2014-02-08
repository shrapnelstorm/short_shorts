import pickle

class Lock_Status:
    def __init__(self,status,client_no):
        self.status = status
        self.client_no = client_no

class Legder:
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
		else:
			self.ledger = []
			self.accepted = []
	def save(self):
	    with open(self.file_name,'wb') as output:
	        pickle.dump([ledger,accepted],output,-1)
	        
	def load(self):
	    with open(self.file_name,'rb') as input:
	        [self.ledger,self.accepted] = pickle.load(input)
	        
	def update_ledger(self,ledger_instance):
	    self.ledger.append(ledger_instance)
	    
	def update_accepted(self,accepted_instance):
	    self.accepted.append(accepted_instance)
	    
