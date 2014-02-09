import os
import pickle

# helper modules
import message

# TODO: add some lock consistency code if have time
class Lock_Status:
    def __init__(self,status,client_no):
        self.status = status
        self.client_no = client_no

# keeps counts of votes
class VoteTally():
	def __init__(self):
		self.majority	= get_lock_server().majority
		self.counts		= dict()

	# count distinct votes, return true if majority
	# TODO: delete old entries
	def add_vote(proposal, vote):
		vote_set = self.counts.setdefault(proposal, set())
		vote_set.add(vote)
		return (len(vote_set) >= self.majority)
	
	# TODO: add more code to handle vote tallys

class Ledger:
	def __init__(self):
		self.ledger 			= []
		self.missing_entries	= []

	# TODO: include logic for updating entries
	def update_ledger(self, chosen_proposal):
		round_no = chosen_proposal.round_no
		last_entry = len(self.ledger) - 1

		# make room for new entry if needed, & record missing entries
		while last_entry < round_no:
			last_entry += 1
			self.ledger.append(None)
			self.missing_entries(last_entry)

			# store proposal
			self.ledger[round_no] = chosen_proposal

	# return missing entries to be requested later
	def get_missing_entries(self):
		return self.missing_entries
        
# stores all persistent data for each server
class ServerData:
	def __init__(self, server_id):
		self.file_name = str(server_id) + ".sav"
		if os.path.isfile(self.file_name):
			# if file exists with server_id then load from file
			self.load()
		else:
			self.ledger				= Ledger()
			self.accepted			= []
			self.pending_requests	= [] # will be accessed directly

		# this data is not persistent
		self.prepare_tally			= VoteTally()
		self.accept_tally			= VoteTally()

	def save(self):
		with open(self.file_name,'wb') as output:
			pickle.dump([self.ledger,self.accepted,self.pending_requests],output,-1)
	        
	def load(self):
			with open(self.file_name,'rb') as input:
				[self.ledger,self.accepted,self.pending_requests] = pickle.load(input)

	def update_accepted(self,accepted_instance):
		while len(self.accepted) < accepted_instance.round_no:
			self.accepted.append(None)
			self.accepted[accepted_instance.round_no] = accepted_instance
	#def inconsistent(self, round_no):
		#return (len(self.ledger)+1 < round_no)
	    
	    

		
## fix these tests!!!
#s = ServerData(10)
#s.ledger.update_ledger(Ledger(8,67,34,2))
#s.update_accepted(3)
#s.save()
#if os.path.isfile('10.sav'):
#	print 'works'

