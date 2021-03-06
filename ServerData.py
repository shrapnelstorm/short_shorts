import os
import pickle

# helper modules
import message

# simple class to remember the status of a single lock
class Lock_Status:
	# status = 'obtained' or 'free'
    def __init__(self,status,client_no):
        self.status = status
        self.client_no = client_no

# keeps counts of votes
class VoteTally():
	def __init__(self, majority):
		self.majority	= majority #get_lock_server().majority
		self.counts		= dict()

	# count distinct votes, return true if majority
	# returns T/F and proposal
	# True when proposal has been chosen
	# param: vote is voter_id
	def add_vote(self, proposal, vote):
		vote_set = self.counts.setdefault(proposal, set())
		vote_set.add(vote)
		return ((len(vote_set) >= self.majority), proposal)

	# return the actual, stored votes for a proposal
	def get_votes(self, proposal):
		return self.counts.setdefault(proposal, set())

	def clear_votes(self, proposal):
		self.counts.setdefault(proposal, set()).clear()
	

# keeps track of all decisions made by paxos round
class Ledger:
	def __init__(self):
		self.ledger 			= [None, None]
		self.missing_entries	= []

	# add a chosen proposal to the ledger
	def update_ledger(self, chosen_proposal):
		round_no = chosen_proposal.round_num
		last_entry = len(self.ledger) 
		# successful update
		if round_no < last_entry-1:
			self.ledger[round_no] = chosen_proposal
			return

		# make room for new entry then insert it
		while last_entry <= round_no:
			self.ledger.append(None)
			last_entry += 1

		# check for missing entries, and add them
		for i in range(1,round_no):
			if self.ledger[i] == None:
				if i not in self.missing_entries:
					self.missing_entries.append(i) 

		# increase ledger size, if the update occurs for the first time
		# NOTE: ledger length determines round number
		if self.ledger[round_no] == None:
		    self.ledger.append(None)

		# update ledger
		self.ledger[round_no] = chosen_proposal

	# returns true if any entries are missing in ledger
	def is_inconsistent(self):
		return len(self.missing_entries) > 0
		

	# prints the contents of the ledger
	def print_ledger(self):
		for i in self.ledger:
			if i != None:
				print str(i.val) + " round_no: "+ str(i.round_num) + " length: " + str(len(self.ledger))

	# return true if only if proposal has been decided
	def lookup_round_num(self, r_num):
		if len(self.ledger) <= r_num:
			return False
		return (self.ledger[r_num] != None)

	# return missing entries to be requested later
	def get_missing_entries(self):
		return self.missing_entries
	
	# return the maximim round number
	def max_r_num(self):
		pls = [ prop for prop in self.ledger ]
		ls = []

		for i in pls:
			if i != None:
				ls.append(i.round_num)

		if len(ls) == 0:
			return 0
		return max(ls)
        
# global array of all locks
# NOTE: this is bad, but we're in a time crunch
locks = [i for i in range(1,15)]

# stores all persistent data for each server
class ServerData:
	def __init__(self, server_id, majority):
		self.file_name = str(server_id) + ".sav"
		if os.path.isfile(self.file_name):
			# if file exists with server_id then load from file
			self.load()
		else:
			self.ledger				= Ledger()
			self.accepted			= {} 
			self.promises			= {} 
			self.pending_requests	= [] # will be accessed directly


		# this data is not persistent
		self.prepare_tally			= VoteTally(majority)
		self.accept_tally			= VoteTally(majority)

		# lock statuses
		self.lock_statuses		= {}
		for i in locks:
			self.lock_statuses[i] = Lock_Status('free', 0)

	# save and load functions for backup
	def save(self):
		with open(self.file_name,'wb') as output:
			pickle.dump([self.ledger,self.accepted,self.pending_requests],output,-1)
	        
	def load(self):
			with open(self.file_name,'rb') as input:
				[self.ledger,self.accepted,self.pending_requests] = pickle.load(input)

	# update the list of accepted proposals
	def update_accepted(self, accepted_prop):
		## XXX: make sure this psn is higher than previous
		self.accepted[accepted_prop.round_num] = accepted_prop
	#def inconsistent(self, round_no):
		#return (len(self.ledger)+1 < round_no)
	
	def max_r_num_accepted(self):
		ls = [ r_num for r_num in self.accepted.keys()]
		if len(ls) == 0:
			return 0
		return max(ls)

	# return last accepted proposal for given round
	def lookup_proposal(self, round_num):
		return self.accepted.setdefault(round_num, None)

	def update_promises(self, round_num, psn):
		self.promises[round_num] = psn
	def last_promise(self, round_num):
		return self.promises.setdefault(round_num, None)
	    
	# checks if a specific instruction is there in the ledger
	def lookup_lock_status(self, lock_no):
		return (self.lock_statuses[int(lock_no)].status )

	def update_lock_status(self, lock_no, status):
		self.lock_statuses[int(lock_no)].status = status

