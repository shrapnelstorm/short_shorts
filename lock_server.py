############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		Lock server and lock server manager impl
##				implementation.
############################################################	

import pipe
from threading import Thread
import os
import random
import time

# top level functions to use LockServer
# NOTE: use @staticmethod to define a static method
NUM_SERVERS = 10
LS_MGR = None
def get_lock_server():
	"""returns global LockServer instance"""
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
# 		works there are no failures
class LockServerManager:
	"""creates and initializes lockservers, and their
	communication channels."""

	# responsibilities: revive servers, setup comm, setup unique NumGen
	# TODO: come up with a good way to do this!!

	# call order: create_instances, manage_servers

	def __init__(self, n_serv=10):
		self.num_servers = n_serv
		self.server_client_comm = [pipe.Pipe() for i in range(n_serv)]
		self.paxos_comm = [pipe.Pipe() for i in range(n_serv)]
		self.manager_comm = queue.Queue() # just use a regular queue for this


		# maps round --> psn generator
		self.psns = dict() # an empty dictionary of unique psns 
	
	def create_instances(self):
		# run the required number of lock servers
		for i in range(num_servers):
			LockServerThread(i, paxos_comm, server_client_comm[i], manager_comm).run()

	def manage_servers(self):
		# TODO: need to do something other than busy wait
		while True:
			# listen for messages from servers
			# if server has failed, wait a timeout period and initialize a new server
			if not manager_comm.empty():
				s_id, timeout = manager_comm.get()
				threading.Thread(target=init_new_server, arg=[s_id, self.paxos_comm, self.server_client_comm[s_id], manager_comm,timeout]).start()
	
	def init_new_server(server_id, paxos_comm, sc_comm, man_comm, timeout=0):
		# wait designated time
		sleep(timeout)

		# initialize a new server
		LockServerThread(i, paxos_comm, sever_client_comm[server_id], manager_comm).run()

	def get_psn(self, round_num):
		# get the psn generator, or ceate a new one and return a fresh value
		psn_generator = self.psns.setdefault(round_num, uniquePsn())
		return psn_generator()
		
		

NUM_LOCKS = 15

# server states
#prep_req, propose, vote_received,
class LockServerThread(Thread): 
	"""docstring for LockServer"""
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0):
		Thread.__init__(self)

		# initialize data fields
		self.id_num = id_num
		self.out_comm = out_comm
		self.in_comm = in_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		self.ledger = []
		self.fail_rate = fail_rate
	
	# will run the paxos protocol
	def run(self):
		return "unimplemented"

		# if previously saved file exists then initialize from it
		# if received a client request => propose it.

		# listen for msgs from other servers, and 
		# process according to state and message type
			# if proposal and haven't seen any other 
			# proposal then accept 

			# if 

		# save any new state in ledger or instance state
		# repeat
	
#class ServerData:
#	def __init__(self, server_id):
#		self.file_name = str(server_id) + ".sav"
#		if os.path.isfile(self.file_name):
#			# if file exists with server_id then load from file
#		else:
#			self.ledger = []
#			self.accepted = []
#	def save(self):
#	def load(self):
