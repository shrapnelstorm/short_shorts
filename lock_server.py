############################################################	
## Programmers: Armando Diaz Tolentino & Siva
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


###						GLOBAL VARS
NUM_SERVERS = 10
LS_MGR = None			# lock server manager

						# client config files
file_names = ['clients/1.client', 'clients/2.client']
#file_names = ['clients/simple.client']
#file_names = ['clients/3.client']

						# node failure list
#(i,j) specifies the node i fails after time j 
nodes_tofail = [(0,0),(1,0)]



###						GLOBAL FUNCTIONS
#function that spawns the nodes of a distributed system
def get_lock_server():
	"""returns global LockServer instance"""
	global LS_MGR
	if LS_MGR is None:
		LS_MGR = LockServerManager(5, len(file_names)) # system replicated 10 times
	return LS_MGR


# NOTE: unused, due to bugs and insufficient time
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

class LockServerManager:
	"""creates and initializes lockservers, and their
	communication channels."""

	# responsibilities: revive servers, setup comm, setup unique NumGen

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

		# lock to print ledger
		self.print_lock =	threading.Lock()
	
	# function that prints the ledger
	def print_ledger(self, ledger, server):
		self.print_lock.acquire()
		print "\nledger for %d" % server
		ledger.print_ledger()
		self.print_lock.release()

	def create_instances(self):
		# run the required number of lock servers
		for i in range(self.num_servers):
			LockServerThread(i, self.paxos_comm, self.client_server_comm[i], self.manager_comm).start()

	# restart a failed server thread, used in recovery.
	# NOTE: implemented, but not tested
	@staticmethod
	def init_new_server(server_id, paxos_comm, sc_comm, man_comm, timeout=0):
		# wait designated time that server is supposed to be down
		time.sleep(timeout)

		# initialize a new server
		LockServerThread(server_id, paxos_comm, sc_comm, man_comm).run()

	# listen for messages from servers
	# if server has failed, wait a timeout period and initialize a new server
	def manage_servers(self):
		while True:
			if not self.manager_comm.empty():
				s_id, timeout = self.manager_comm.get()
				# start new thread for server
				Thread(target=LockServerManager.init_new_server, args=(int(s_id), self.paxos_comm, self.client_server_comm[s_id], self.manager_comm,timeout)).start()
	
	def run(self):
		self.manage_servers()


	# return a fresh psn for given round number
	# uses locking to ensure psn given to only one server
	def get_psn(self, round_num):
		#psn_generator = self.psns.setdefault(round_num, uniquePsn())
		#return psn_generator()
		self.psn_lock.acquire()
		psn = self.psn_next
		self.psn_next += 1
		self.psn_lock.release()
		return psn
		
		

# class responsibilities: handle requests from clients for locks,
#			send responses, run paxos protocol to achieve consensus
#			among peers.
class LockServerThread(Thread): 
	"""A single lock server instance"""
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0):
		Thread.__init__(self)

		# initialize data fields
		self.id_num = id_num
		self.paxos_comm = paxos_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		self.server_data = ServerData.ServerData(id_num, get_lock_server().majority)
		self.fail_rate = fail_rate 		# NOTE: not used, intended for recovery code

		# TODO: do we still need these??
		self.majority= {}
		self.chosen_values = {}
		self.pending_requests = []

		# drequest timeout so we don't make drequests too often
		self.dreq_timeout = 0

		# printing output
		self.debug_level = 1 # handles output verbosity 0:none, 1:just ledgers, 2:all


###						SENDING MESSAGES 
	# send a message to every other node
	def broadcast_msg(self, msg):
		for idx, comm in  enumerate(self.paxos_comm): 
			comm.put(msg)

	# send a message to every other node but itself
	def broadcast_to_others(self, msg):
		for idx, comm in  enumerate(self.paxos_comm): 
			if idx != self.id_num:
				comm.put(msg)

###						GENERATING MESSAGES

	# create a prepare message for a given round number
	def send_prepare_msg(self, cmd):
		# get new psn, create proposal, and send prepare msg
		#r_num 	= max(self.server_data.ledger.max_r_num() + 1, self.server_data.max_r_num_accepted() )

		# round number dependent only on ledger size
		r_num 	= len(self.server_data.ledger.ledger) - 1
		new_psn	= get_lock_server().get_psn(r_num)
		prop	= message.Proposal(new_psn, r_num, cmd)
		msg		= message.PrepareMsg(self.id_num, prop)
		self.broadcast_msg(msg)
		if self.debug_level >= 2: print "%d sent prepare :%s" % (self.id_num, str(msg.proposal))
	    
	# create a promise mesage, in response to a prepare
	def send_promise_msg(self, prep_msg):

		# if receive promise for round with chosen value, send DecisionResponse instead
		if self.server_data.ledger.lookup_round_num(prep_msg.proposal.round_num):
			msg = message.DecisionResponse(self.server_data.ledger.ledger[prep_msg.proposal.round_num])
			self.paxos_comm[prep_msg.sender].put(msg)
			return
			
		accepted_proposal = self.server_data.lookup_proposal(prep_msg.proposal.round_num)
		promise = self.server_data.last_promise(prep_msg.proposal.round_num)

		# sends out a promise for proposal numbers greater than the previously promised number
		if promise is None or prep_msg.proposal.psn >= promise:
			 # respond with original proposal and last accepted proposal for round
			 self.server_data.update_promises(prep_msg.proposal.round_num, prep_msg.proposal.psn)
			 msg = message.PromiseMsg(self.id_num, prep_msg.proposal, accepted_proposal)
			 self.paxos_comm[prep_msg.sender].put(msg)
			 if self.debug_level >= 2: print "%d sent promise :%s" % (self.id_num, msg.msg_str())
	        
	# issue proposal message in response to promise messages
	def send_proposal_msg(self, promise_msg):
		# storing promise instead of id
		maj_resp, proposal = self.server_data.prepare_tally.add_vote(promise_msg.orig_proposal, promise_msg)
		# check for majority promise messages for a particular prepare
		if maj_resp:
			# clear the votes, so proposal isn't sent again
			self.server_data.prepare_tally.clear_votes(promise_msg.orig_proposal)

			arr2 = [ v.accepted_proposal for v in self.server_data.prepare_tally.get_votes(proposal)]
			array = []
			for i in arr2:
				if i != None:
					array.append(i.val)
			val_exists, val = majority(array,get_lock_server().majority)
			# make sure one proposes the majority value if it exists
			if val_exists and val is not None:
				# create copy of proposal with majority value
				prop = message.Proposal( promise_msg.orig_proposal.psn, promise_msg.orig_proposal.round_num, val)
				msg = message.ProposalMsg(prop)
			else:
				msg = message.ProposalMsg(promise_msg.orig_proposal)

			self.broadcast_msg(msg)
			if self.debug_level >= 2: print "%d sent proposal :%s" % (self.id_num, msg.msg_str())

				
	    
	# as a response to proposal, send a vote message depending on state of 
	# last promies and ledger
	def send_vote_msg(self, prop_msg):
		msg = None
		last_promise = self.server_data.last_promise(prop_msg.proposal.round_num)

		# value is already in ledger for this round
		if self.server_data.ledger.lookup_round_num(prop_msg.proposal.round_num):
			return

		if last_promise is None or prop_msg.proposal.psn >= last_promise:
			msg = message.VoteMsg(self.id_num, prop_msg.proposal)
			self.broadcast_msg(msg)
			self.server_data.update_accepted(prop_msg.proposal)
			if self.debug_level >= 2: print "%d sent vote message :%s" % (self.id_num, msg.msg_str())
            
###						HANDLING MESSAGES
	# Calls the function that reads the paxos queue
	def check_paxos_msgs(self):
		inbox = self.paxos_comm[self.id_num]
		if not inbox.empty():
			msg = inbox.get()
			self.handle_paxos_msg(msg)

		# propose client requests

	# count a received vode, 
	# if a majority is achieved enter it in ledger
	# and update lock statuses if necessary.
	def count_vote_update_ledger(self, vote_msg):
		maj_resp, proposal = self.server_data.accept_tally.add_vote(vote_msg.proposal, vote_msg.voter_id)

		if maj_resp:
			# update lock status, depending on message type
			if proposal.val[0] == 'obtain_lock':
				self.server_data.update_lock_status(proposal.val[1], 'obtained')
			else:
				self.server_data.update_lock_status(proposal.val[1], 'free')

			# remove majority from accept_tally
			self.server_data.accept_tally.clear_votes(vote_msg.proposal)
			self.server_data.ledger.update_ledger(proposal)

			# print ledger for debugging purposes
			if self.debug_level >= 1: get_lock_server().print_ledger(self.server_data.ledger, self.id_num)

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
			if self.debug_level >= 2: print "########## %d received  prepare:%s" % (self.id_num, msg.msg_str())
			self.send_promise_msg(msg)
		elif isinstance(msg,message.PromiseMsg): # received promise, send proposal
			if self.debug_level >= 2: print "########## %d received  promise:%s" % (self.id_num, msg.msg_str())
			self.send_proposal_msg(msg)
		elif isinstance(msg,message.ProposalMsg): # received proposal, send vote
			if self.debug_level >= 2: print "########## %d received  proposal:%s" % (self.id_num, msg.msg_str())
			# issue accept message in response to proposal
			self.send_vote_msg(msg)
		elif isinstance(msg,message.VoteMsg): # tally received votes
			if self.debug_level >= 2: print "########## %d received  vote:%s" % (self.id_num, msg.msg_str())
			# received vote
			self.count_vote_update_ledger(msg)
		elif isinstance(msg,message.DecisionRequest):
			if self.debug_level >= 2: print "########## %d received  drequest:%s" % (self.id_num, msg.msg_str())
			r_num = msg.proposal.round_num
			if self.server_data.ledger.lookup_round_num(r_num):
				self.send_decision_response(self.server_data.ledger.ledger[r_num], msg)
		elif isinstance(msg,message.DecisionResponse):
			# decision response message means a specific ledger entry has been decided
			if self.debug_level >= 2: print "########## %d received  drespons:%s" % (self.id_num, msg.msg_str())

			# check if entry is in pending
			if len(self.server_data.pending_requests) != 0 :
				proposal = msg.proposal
				pending, timeout = self.server_data.pending_requests[0]
				if pending == proposal.val:
					req = self.server_data.pending_requests.pop(0)
					get_lock_server().server_client_comm[pending[2]].put('cmd accepted')

			# check if entry is missing from ledger
			if self.server_data.ledger.ledger[msg.proposal.round_num] == None:
				if msg.proposal.val[0] == 'obtain_lock':
					self.server_data.update_lock_status(msg.proposal.val[1], 'obtained')
				else:
					self.server_data.update_lock_status(msg.proposal.val[1], 'free')

				self.server_data.ledger.update_ledger(msg.proposal)
				get_lock_server().print_ledger(self.server_data.ledger, self.id_num)
				try:
					self.server_data.ledger.missing_entries.remove(msg.proposal.round_num)
				except ValueError:
					return 
					# do nothing

	# send a message with a chosen value
	def send_decision_response(self, proposal, msg):
		response = message.DecisionResponse(proposal)
		self.paxos_comm[msg.sender].put(response)
		if self.debug_level >= 2: print "%d sent  drespons:%s" % (self.id_num, response.msg_str())
	
	# message to request for a chosen value for a particular round
	def send_decision_req(self, round_num):
		msg = message.DecisionRequest( self.id_num, message.Proposal(None, round_num, None))
		# don't send to self
		self.broadcast_to_others(msg)
		if self.debug_level >= 2: print "%d sent  dreq:%s" % (self.id_num, msg.msg_str())
	
	# the main loop executed by each server thread
	def run(self):
		time_out = get_lock_server().timeout
		while True:
			# fail if necessary
			for i in nodes_tofail:
				if i[0] == self.id_num:
					if time() > i[1] and self.debug_level >= 2:
						print str(self.id_num) + " is about to fail....."
						return

			# check paxos messages
			self.check_paxos_msgs()
			
			# check ledger consistency
			if self.server_data.ledger.is_inconsistent() and self.dreq_timeout < time():
				self.dreq_timeout = time() + 2 # wait at least 2 sec
				r_num = self.server_data.ledger.missing_entries[0]
				self.send_decision_req(r_num)
				continue

			# check pending client requests, and issue prepare msgs
			if not self.client_comm.empty() or len(self.server_data.pending_requests) > 0:

				# get new messages from queue, add to pending
				if not self.client_comm.empty():
					cmd = self.client_comm.get()
					req = cmd,None # (cmd, timeout)
					self.server_data.pending_requests.append(req)

				# check if last request's timeout has expired
				r = self.server_data.pending_requests.pop(0)

				# lock is unavailable, put back in queue and continue
				if r[0][0] == 'obtain_lock' and self.server_data.lookup_lock_status(r[0][1]) == 'obtained':
					# need to push lock to end, to avoid deadlocks
					self.server_data.pending_requests.append(r)
					continue # lock is not available

				current_time = time()
				if(r[1] is None or r[1] < current_time): # timeout expired, or request not issued 
					r = (r[0],  current_time + time_out)
					self.send_prepare_msg(r[0])
					self.server_data.pending_requests.insert(0,r)
				else:
					self.server_data.pending_requests.insert(0,r)
        

# make requests to servers for obtaining and releasing locks
class Client(Thread):
    
    # constructor for the class
    def __init__(self, id_num, filename):
        Thread.__init__(self)
        self.id_num = id_num
        self.filename = filename
        # get handle to lock servers, and server manager
        self.ls_mgr = get_lock_server()
        self.servers = self.ls_mgr.client_server_comm 
        # communication channel to recieve messages from the server
        self.client_pipe = self.ls_mgr.server_client_comm[id_num]

        # initialize list of available servers
        self.available_servers = []
        failing_nodes = [ i for (i,j) in nodes_tofail]
        for i in range(self.ls_mgr.num_servers):
        	if i not in failing_nodes:
        		self.available_servers.append(i)

    
    def read_inst(self):
        f = open(self.filename)
        lines = [line.strip() for line in f]
        f.close()
        return lines
    def parse_command(self,line):
		# client command is (cmd_type, number, client_id)
		# number is either lock num or sleep time
        return tuple(line.split(' ',1) + [self.id_num])

	# write a message to the server queue
    def send_to_server(self, cmd):
        self.available_servers
        rand_idx = random.randint(0,len(self.available_servers) -1)
        rand_server = self.available_servers[rand_idx]
        self.servers[rand_server].put(cmd)
        
    def read_from_server(self):
			r = self.client_pipe.get()
			while (r == None):
				r = self.client_pipe.get()

	# the main function. read instructions from a file and dispatch requests accordingly
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

# create clients with config files as params
def spawn_clients(num,file_names):
     for i in range(num):
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

