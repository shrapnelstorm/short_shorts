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
#import countvotes
import message
import pipe
import ServerData

# top level functions to use LockServer
# NOTE: use @staticmethod to define a static method
NUM_SERVERS = 10
LS_MGR = None

def get_lock_server():
	"""returns global LockServer instance"""
	global LS_MGR
	if LS_MGR is None:
		LS_MGR = LockServerManager(10) # system replicated 10 times
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
		self.paxos_comm 		= [pipe.Pipe() for i in range(n_serv)]
		self.manager_comm		= Queue.Queue() # just use a regular queue for this
		self.majority			= int(math.ceil(n_serv/2.0))


		# maps round_no --> psn generator
		self.psns = dict() # an empty dictionary of unique psns 

		# create instances
		self.create_instances()
	
	def create_instances(self):
		# run the required number of lock servers
		for i in range(self.num_servers):
			LockServerThread(i, self.paxos_comm, self.server_client_comm[i], self.manager_comm).start()

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
				Thread(target=LockServerManager.init_new_server, args=(int(s_id), self.paxos_comm, self.server_client_comm[s_id], self.manager_comm,timeout)).start()
	
	def run(self):
		self.manage_servers()


	def get_psn(self, round_num):
		# get the psn generator, or ceate a new one and return a fresh value
		psn_generator = self.psns.setdefault(round_num, uniquePsn())
		return psn_generator()
		
		

NUM_LOCKS = 15

# server states
#prep_req, propose, vote_received,
class LockServerThread(Thread): 
	"""docstring for LockServer"""
	# TODO: figure out how to include majority threshold
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0):
		Thread.__init__(self)

		print id_num
		# initialize data fields
		self.id_num = id_num
		self.paxos_comm = paxos_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		#self.ledger = []
		self.server_data = ServerData.ServerData(id_num)
		self.fail_rate = fail_rate
		#self.maj_threshold = maj_threshold

		self.majority= {}
		self.chosen_values = {}
		self.pending_requests = []

	
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
	def broadcast_msg(msg):
		for idx, comm in  enumerate(self.paxos_comm): 
			comm.put(result)

	# TODO: if have time, implement dedicated learner
	def send_to_learner(self, msg):
		self.broadcast_msg(msg)
	
	# TODO: change update to use new message types
	def update_ledger(self,round_no,list_val,psn):
		return "unimplemented"
		#maj = majority(list_val,self.maj_threshold)
		#if maj[0] == 1: 
		## update ledger
		#	entry = Ledger(round_no, maj[1].psn, maj[1].val, maj[1].cmd, maj[1].client)
		#	self.server_data.update_ledger(round_no, entry)

		# TODO: request missing data
		#if inconsistent(round_no):
			# update required

###						GENERATING MESSAGES

	# create a prepare message for a given round number
	def send_prepare_msg(self, cmd, r_num):
		# get new psn, create proposal, and send prepare msg
		new_psn	= get_lock_server().get_psn(r_num)
		prop	= Proposal(new_psn, r_num, cmd)
		msg		= PrepareMsg(self.id_num, prop)
		self.broadcast_msg(msg)
	    
	# create a promise mesage, in response to a prepare
	def send_promise_msg(self, prep_msg):
		# XXX: change server_data to store Proposal objects!!!
		accepted_proposal = self.server_data.highest_accepted(round_no)

		if prep_msg.proposal.psn > accepted_proposal.psn:
			 # respond with original proposal and last accepted proposal for round
			 msg = PromiseMsg(self.id_num, prep_msg.proposal, accepted_proposal)
			 self.paxos_comm[prep_msg.sender].put(msg)
	        
	# TODO: list of values?
	# issue proposal message in response to promise messages
	def send_proposal_msg(self, promise_msg):
		# 				old code
		#ls = self.update_majority(promise_msg, self.majority) ### TODO: fix this code to use new MSG types
		#maj = majority(ls,self.maj_threshold)
		#if maj[0] == 0: return None
		#else:
			# XXX: TODO: cleanup this code, hard to understand
		#	msg = Message('proposal',psn,maj[1],round_no,maj[1][0],maj[1][1])
		#	self.broadcast_msg(new_msg)
		if self.server_data.prepare_tally.add_vote(promise_msg.orig_proposal, promise_msg.server_id):
			# XXX: TODO: make sure proposal has value too!!
			# TODO: after sending proposal, clear tally
			msg = ProposalMsg(promise_msg.orig_proposal)

	    
	## TODO: fix server data
	## This logic seems incorrect. We should be checking if a value has been chosen too (in ledger)
	def send_vote_msg(self, prop_msg):
		msg = None
		last_accepted_psn = self.server_Data.highest_accepted(prop_msg.proposal.round_no)[0]
		if prop_msg.proposal.psn >= last_accepted_psn:
			msg = VoteMsg(self.id_num, prop_msg.proposal)
		## why do we want to do this??
		elif message.val == self.server_Data.highest_accepted(message.round_no)[1]:
			msg = VoteMsg(self.id_num,prop_msg.proposal)

		if not (msg is None):
			self.send_to_learner(msg)
            
###						HANDLING MESSAGES
	# TODO: finish implementing this!!!
	def check_paxos_msgs(self):
		inbox = self.paxos_comm[self.id_num]
		if not inbox.empty():
			handle_paxos_msg(inbox.get())

		# propose client requests

	# TODO: empty dictionary once a majority is reached
	def update_majority(self, msg, hmap):
	# handle received messages by type
		entry = (msg.round_no, msg.psn)
		if hmap[entry] is None:
			hmap[entry] = [msg]
		else:
			hmap[entry] = hmap[entry] + [msg]
		return hmap[entry]


	# handle a single received message
	def handle_paxos_msg(self,msg):
		msg_type = type(msg)
		if msg_type == PrepareMsg: # received prepare, send promise
			self.send_promise_msg(msg.round_no, msg.psn)
		elif msg_type == PromiseMsg: # received promise, send proposal
			self.send_proposal_msg(msg.round_no, ls, msg.orig_psn)
		elif msg_type == ProposalMsg: # received proposal, send vote
			# issue accept message in response to proposal
			self.send_vote_msg(msg)
		elif msg_type == VoteMsg: # tally received votes
			# received vote
			# TODO: fix this, seems incorrect!!
			ls = self.update_majority(msg, self.chosen_values)
		#elif msg_type == DecisionRequest:
		#elif msg_type == DecisionResponse:


	# TODO: handle paxos msgs too
	def run(self,time_out):
		while True:
			self.check_paxos_msgs()
			
			while not self.client_comm.empty():
				print "%d received message" % self.id_num
				cmd = self.client_comm.get()
				self.server_data.pending_requests.append((cmd,None))
				# find round number and make_proposal()

            r = pending_request.pop(0)
            current_time = time()
            if(r[1] is None or r[1] < current_time):
                r[1] = current_time + self.time_out
                self.send_prepare_msg(r[0])
                pending_request.insert(0,r)
                
			# propose command
		# TODO: delete this test code
		#if self.id_num == 9:
		#	time.sleep(1)
		#	self.manager_comm.put((self.id_num, 5))

		return "unimplemented"

        

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
        while not r is None:
            r = self.client_pipe.get()

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
			print "done"

def spawn_clients(num,file_names):
     for i in range(num):
        print "spawning client"
        client = Client(i, file_names[i]).start()

############################################################	
## Desc:		 MAIN FUNCTION
############################################################	
# code to test lock server and manager class
file_names = ['clients/1.client', 'clients/2.client']

# get lock server
ls = LockServerManager(10,len(fine_names))
LS_MGR = ls
spawn_clients(len(file_names), file_names)
ls.run()

