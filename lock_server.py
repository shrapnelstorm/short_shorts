############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		Lock server and lock server manager impl
##				implementation.
############################################################	

# standard libraries
import math
import Queue
import threading
import threading
import os
import random
import time
from time import sleep
from time import time
from threading import Thread


# helper files
from countvotes import majority
import message
import pipe
import ServerData

# top level functions to use LockServer
# NOTE: use @staticmethod to define a static method
NUM_SERVERS = 10
LS_MGR = None
file_names = ['clients/1.client', 'clients/2.client']
#file_names = ['clients/simple.client']

def get_lock_server():
	"""returns global LockServer instance"""
	global LS_MGR
	if LS_MGR is None:
		LS_MGR = LockServerManager(5, len(file_names)) # system replicated 10 times
	return LS_MGR

## TODO: the above may not be necessary



# generate a function that creates unique psn's
def uniquePsn():
	# generate a unique psn, not sure if this is correct
	psn_lock = threading.Lock()
	def uniqueNumGen():
		num = 0
		while True:
			psn_lock.acquire()
			tmp = num
			num += 1
			psn_lock.release()
			yield tmp
	return uniqueNumGen

# TODO: file initialization, for now everything
# 		works as if there are no failures
class LockServerManager:
	"""creates and initializes lockservers, and their
	communication channels."""

	# responsibilities: revive servers, setup comm, setup unique NumGen
	# TODO: come up with a good way to do this!!

	# call order: create_instances, manage_servers

	def __init__(self, n_serv=10, n_client=10):
		self.num_servers		= n_serv
		self.num_clients        = n_client
		self.client_server_comm	= [pipe.Pipe() for i in range(n_serv)]
		self.server_client_comm	= [pipe.Pipe() for i in range(n_client)]
		self.paxos_comm 		= [pipe.Pipe(loss_factor=30) for i in range(n_serv)]
		self.manager_comm		= Queue.Queue() # just use a regular queue for this
		self.majority			= int(math.ceil(n_serv/2.0))
		self.timeout			= 5	 # seconds


		# maps round_no --> psn generator
		self.psns = dict() # an empty dictionary of unique psns 

		# psn fields
		self.psn_lock = threading.Lock()
		self.psn_next = 0

		# TODO: DELETE this later
		self.print_lock =	threading.Lock()
	
	def print_ledger(self, ledger, server):
		self.print_lock.acquire()
		print " ledger for %d" % server
		ledger.print_ledger()
		self.print_lock.release()

	def create_instances(self):
		# run the required number of lock servers
		print " num servers is %d" % self.num_servers
		for i in range(self.num_servers):
			LockServerThread(i, self.paxos_comm, self.client_server_comm[i], self.manager_comm).start()

	@staticmethod
	def init_new_server(server_id, paxos_comm, sc_comm, man_comm, timeout=0):
		# wait designated time that server is supposed to be down
		time.sleep(timeout)

		# initialize a new server
		LockServerThread(server_id, paxos_comm, sc_comm, man_comm).run()

	def manage_servers(self):
		while True:
			# listen for messages from servers
			# if server has failed, wait a timeout period and initialize a new server
			if not self.manager_comm.empty():
				s_id, timeout = self.manager_comm.get()
				Thread(target=LockServerManager.init_new_server, args=(int(s_id), self.paxos_comm, self.client_server_comm[s_id], self.manager_comm,timeout)).start()
	
	def run(self):
		self.manage_servers()


	def get_psn(self, round_num):
		# get the psn generator, or ceate a new one and return a fresh value
		#psn_generator = self.psns.setdefault(round_num, uniquePsn())
		#return psn_generator()
		self.psn_lock.acquire()
		psn = self.psn_next
		self.psn_next += 1
		self.psn_lock.release()
		return psn
		
		

NUM_LOCKS = 15

# server states
#prep_req, propose, vote_received,
class LockServerThread(Thread): 
	"""docstring for LockServer"""
	# TODO: figure out how to include majority threshold
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0):
		Thread.__init__(self)

		# initialize data fields
		self.id_num = id_num
		self.paxos_comm = paxos_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		#self.ledger = []
		self.server_data = ServerData.ServerData(id_num, get_lock_server().majority)
		self.fail_rate = fail_rate
		#self.maj_threshold = maj_threshold

		self.majority= {}
		self.chosen_values = {}
		self.pending_requests = []

		# drequest timeouts
		self.dreq_timeout = 0

	
	# will run the paxos protocol
		# if previously saved file exists then initialize from it
		# if received a client request => propose it.

		# listen for msgs from other servers, and 
		# process according to state and message type
			# if proposal and haven't seen any other 
			# proposal then accept 

			# if 

		# save any new state in ledger or instance state
		# repeat

###						SENDING MESSAGES 
	# send a message to every other node
	# TODO: do we want to send to self also?
	def broadcast_msg(self, msg):
		for idx, comm in  enumerate(self.paxos_comm): 
			comm.put(msg)

	def broadcast_to_others(self, msg):
		for idx, comm in  enumerate(self.paxos_comm): 
			if idx != self.id_num:
				comm.put(msg)

	# TODO: if have time, implement dedicated learner
	def send_to_learner(self, msg):
		self.broadcast_msg(msg)
	
		# TODO: request missing data
		#if inconsistent(round_no):
			# update required

###						GENERATING MESSAGES

	# create a prepare message for a given round number
	def send_prepare_msg(self, cmd):
		# get new psn, create proposal, and send prepare msg
		#r_num 	= max(self.server_data.ledger.max_r_num() + 1, self.server_data.max_r_num_accepted() )
		r_num 	= len(self.server_data.ledger.ledger) - 1
		new_psn	= get_lock_server().get_psn(r_num)
		prop	= message.Proposal(new_psn, r_num, cmd)
		msg		= message.PrepareMsg(self.id_num, prop)
		self.broadcast_msg(msg)
		print "%d sent prepare :%s" % (self.id_num, str(msg.proposal))
	    
	# create a promise mesage, in response to a prepare
	def send_promise_msg(self, prep_msg):
		#print "%d sending promise" % self.id_num
		# XXX: change server_data to store Proposal objects!!!

		# if receive promise for round with chosen value
		if self.server_data.ledger.lookup_round_num(prep_msg.proposal.round_num):
			msg = message.DecisionResponse(self.server_data.ledger.ledger[prep_msg.proposal.round_num])
			self.paxos_comm[prep_msg.sender].put(msg)
			return
			
		accepted_proposal = self.server_data.lookup_proposal(prep_msg.proposal.round_num)
		promise = self.server_data.last_promise(prep_msg.proposal.round_num)

		if promise is None or prep_msg.proposal.psn >= promise:
			 # respond with original proposal and last accepted proposal for round
			 self.server_data.update_promises(prep_msg.proposal.round_num, prep_msg.proposal.psn)
			 msg = message.PromiseMsg(self.id_num, prep_msg.proposal, accepted_proposal)
			 self.paxos_comm[prep_msg.sender].put(msg)
			 print "%d sent promise :%s" % (self.id_num, msg.msg_str())
	        
	# TODO: list of values?
	# issue proposal message in response to promise messages
	def send_proposal_msg(self, promise_msg):
		#print "%d sending proposal" % self.id_num

		# storing promise instead of id
		maj_resp, proposal = self.server_data.prepare_tally.add_vote(promise_msg.orig_proposal, promise_msg)
		if maj_resp:
			# clear the votes, so proposal isn't sent again
			self.server_data.prepare_tally.clear_votes(promise_msg.orig_proposal)

			arr2 = [ v.accepted_proposal for v in self.server_data.prepare_tally.get_votes(proposal)]
			array = []
			for i in arr2:
				if i != None:
					array.append(i.val)
			val_exists, val = majority(array,get_lock_server().majority)
			if val_exists and val is not None:
				# create copy of proposal with majority value
				prop = message.Proposal( promise_msg.orig_proposal.psn, promise_msg.orig_proposal.round_num, val)
				msg = message.ProposalMsg(prop)
			else:
				msg = message.ProposalMsg(promise_msg.orig_proposal)

			self.broadcast_msg(msg)
			print "%d sent proposal :%s" % (self.id_num, msg.msg_str())

				
			# XXX: TODO: make sure proposal has value too!!
			# TODO: after sending proposal, clear tally

	    
	## TODO: fix server data
	## This logic seems incorrect. We should be checking if a value has been chosen too (in ledger)
	def send_vote_msg(self, prop_msg):
		#print "%d sending vote" % self.id_num
		msg = None
		last_promise = self.server_data.last_promise(prop_msg.proposal.round_num)

		# value is already in ledger for this round
		if self.server_data.ledger.lookup_round_num(prop_msg.proposal.round_num):
			return

		if last_promise is None or prop_msg.proposal.psn >= last_promise:
			msg = message.VoteMsg(self.id_num, prop_msg.proposal)
			self.broadcast_msg(msg)
			self.server_data.update_accepted(prop_msg.proposal)
			print "%d sent vote message :%s" % (self.id_num, msg.msg_str())
            
###						HANDLING MESSAGES
	# TODO: finish implementing this!!!
	def check_paxos_msgs(self):
		inbox = self.paxos_comm[self.id_num]
		if not inbox.empty():
			msg = inbox.get()
			#if isinstance(msg, message.PromiseMsg):
			#	print "%d paxos msg: %s for round %d" % (self.id_num, msg.__class__.__name__, msg.orig_proposal.round_num)
			#else:
			#	print "%d paxos msg: %s for round %d" % (self.id_num, msg.__class__.__name__, msg.proposal.round_num)
			self.handle_paxos_msg(msg)

		# propose client requests

	# TODO: empty dictionary once a majority is reached
	def count_vote_update_ledger(self, vote_msg):
	# handle received messages by type
		maj_resp, proposal = self.server_data.accept_tally.add_vote(vote_msg.proposal, vote_msg.voter_id)

		if maj_resp:
			# remove majority from accept_tally
			#self.server_data.accept_tally.clear_votes(vote_msg.proposal)
			self.server_data.ledger.update_ledger(proposal)
			get_lock_server().print_ledger(self.server_data.ledger, self.id_num)
			print "%d has this many votes %d" % (self.id_num, len(self.server_data.accept_tally.counts[proposal]) )
			if len(self.server_data.pending_requests) == 0 :
				return
			# update pending requests if there are any
			pending, timeout = self.server_data.pending_requests[0]
			if pending == proposal.val:
				req = self.server_data.pending_requests.pop(0)
				get_lock_server().server_client_comm[pending[2]].put('cmd accepted')


	# handle a single received message
	def handle_paxos_msg(self,msg):
		if isinstance(msg,message.PrepareMsg): # received prepare, send promise
			print "########## %d received  prepare:%s" % (self.id_num, msg.msg_str())
			#print "%d got prepmsg" % self.id_num
			self.send_promise_msg(msg)
		elif isinstance(msg,message.PromiseMsg): # received promise, send proposal
			print "########## %d received  promise:%s" % (self.id_num, msg.msg_str())
			self.send_proposal_msg(msg)
		elif isinstance(msg,message.ProposalMsg): # received proposal, send vote
			print "########## %d received  proposal:%s" % (self.id_num, msg.msg_str())
			# issue accept message in response to proposal
			self.send_vote_msg(msg)
		elif isinstance(msg,message.VoteMsg): # tally received votes
			print "########## %d received  vote:%s" % (self.id_num, msg.msg_str())
			# received vote
			# TODO: fix this, seems incorrect!!
			self.count_vote_update_ledger(msg)
		elif isinstance(msg,message.DecisionRequest):
			print "########## %d received  drequest:%s" % (self.id_num, msg.msg_str())
			r_num = msg.proposal.round_num
			if self.server_data.ledger.lookup_round_num(r_num):
				self.send_decision_response(self.server_data.ledger.ledger[r_num], msg)
		elif isinstance(msg,message.DecisionResponse):
			print "########## %d received  drespons:%s" % (self.id_num, msg.msg_str())

			# check if entry is in pending
			if len(self.server_data.pending_requests) != 0 :
				proposal = msg.proposal
				pending, timeout = self.server_data.pending_requests[0]
				if pending == proposal.val:
					req = self.server_data.pending_requests.pop(0)
					get_lock_server().server_client_comm[pending[2]].put('cmd accepted')

			# check if entry is missing from ledger
			if self.server_data.ledger.ledger[msg.proposal.round_num] == None:
				self.server_data.ledger.update_ledger(msg.proposal)
				get_lock_server().print_ledger(self.server_data.ledger, self.id_num)
				try:
					self.server_data.ledger.missing_entries.remove(msg.proposal.round_num)
				except ValueError:
					return 
					# do nothing


	def send_decision_response(self, proposal, msg):
		response = message.DecisionResponse(proposal)
		self.paxos_comm[msg.sender].put(response)
		print "%d sent  drespons:%s" % (self.id_num, response.msg_str())

	def send_decision_req(self, round_num):
		msg = message.DecisionRequest( self.id_num, message.Proposal(None, round_num, None))
		# don't send to self
		self.broadcast_to_others(msg)
		print "%d sent  dreq:%s" % (self.id_num, msg.msg_str())
	
	def run(self):
		time_out = get_lock_server().timeout
		while True:
			self.check_paxos_msgs()
			
			# check ledger consistency
			if self.server_data.ledger.is_inconsistent() and self.dreq_timeout < time():
				self.dreq_timeout = time() + 2 # wait at least 2 sec
				r_num = self.server_data.ledger.missing_entries[0]
				self.send_decision_req(r_num)

			# check pending client requests, and issue prepare msgs
			if not self.client_comm.empty() or len(self.server_data.pending_requests) > 0:

				# get new messages from queue, add to pending
				if not self.client_comm.empty():
					cmd = self.client_comm.get()
					req = cmd,None # (cmd, timeout)
					self.server_data.pending_requests.append(req)

				# check if last request's timeout has expired
				r = self.server_data.pending_requests.pop(0)
				current_time = time()
				if(r[1] is None or r[1] < current_time): # timeout expired, or request not issued 
					r = (r[0],  current_time + time_out)
					self.send_prepare_msg(r[0])
					self.server_data.pending_requests.insert(0,r)
				else:
					self.server_data.pending_requests.insert(0,r)
        

############################################################	
## Programmer: 	Siva
## Desc:		Client class
############################################################	
class Client(Thread):
    
    def __init__(self, id_num, filename):
        Thread.__init__(self)
        self.id_num = id_num
        self.filename = filename
        # get handle to lock servers, and server manager
        self.ls_mgr = get_lock_server()
        self.servers = self.ls_mgr.client_server_comm 
        self.client_pipe = self.ls_mgr.server_client_comm[id_num]
        
    def read_inst(self):
        f = open(self.filename)
        lines = [line.strip() for line in f]
        f.close()
        return lines
    def parse_command(self,line):
		# client command is (cmd_type, number, client_id)
		# number is either lock num or sleep time
        return tuple(line.split(' ',1) + [self.id_num])

    def send_to_server(self, cmd):
        rand_server = random.randint(0,self.ls_mgr.num_servers - 1)
        self.servers[rand_server].put(cmd)
        
    def read_from_server(self):
			r = self.client_pipe.get()
			#print r
			while (r == None):
				r = self.client_pipe.get()
			#print " r after loop " + str(r)

    def run(self):
			instrs = self.read_inst()
			for instr in instrs:
				cmd = self.parse_command(instr)
				cmd_type, _, _ = cmd
				if cmd_type == 'sleep':
					_,timeout,_ = cmd
					sleep(int(timeout))
				else :
					self.send_to_server(cmd)
					self.read_from_server()
			#print "done %d" % self.id_num

def spawn_clients(num,file_names):
     for i in range(num):
        #print "spawning client"
        client = Client(i, file_names[i]).start()

############################################################	
## Desc:		 MAIN FUNCTION
############################################################	
# code to test lock server and manager class
#file_names = ['clients/1.client', 'clients/2.client']

# get lock server
ls = get_lock_server()
ls.create_instances()
spawn_clients(len(file_names), file_names)
ls.run()

