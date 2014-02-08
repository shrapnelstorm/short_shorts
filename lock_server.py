############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		Lock server and lock server manager impl
##				implementation.
############################################################	

import pipe
from threading import Thread
import os

# top level functions to use LockServer
# NOTE: use @staticmethod to define a static method
NUM_SERVERS
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

class LockServerManager:
	"""creates and initializes lockservers, and their
	communication channels."""

	# responsibilities: revive servers, setup comm, setup unique NumGen
	# come up with a good way to do this!!

	def __init__(self, n_serv=10):
		self.num_servers = n_serv
		self.server_client_comm = [pipe.Pipe() for i in range(n_serv)]
		self.paxos_comm = [pipe.Pipe() for i in range(n_serv)]
	
	def create_instances

		# run the required number of lock servers
		for i in range(num_servers):
			LockServerThread(i, paxos_comm, server_client_comm[i]).run()

NUM_LOCKS = 15
# server states
prep_req, propose, vote_received,
class LockServerThread(Thread): 
	"""docstring for LockServer"""
	def __init__(self, id_num, paxos_comm, client_comm):
		Thread.__init__(self)
		self.id_num = id_num
		self.out_comm = out_comm
		self.in_comm = in_comm
		self.client_comm = client_comm
		self.ledger = []
	
	# will run the paxos protocol
	def run(self):

		# if previously saved file exists then initialize from it
		# if received a client request => propose it.

		# listen for msgs from other servers, and 
		# process according to state and message type
			# if proposal and haven't seen any other 
			# proposal then accept 

			# if 

		# save any new state in ledger or instance state
		# repeat
	
class ServerData:
	def __init__(self, server_id):
		self.file_name = str(server_id) + ".sav"
		if os.path.isfile(self.file_name):
			# if file exists with server_id then load from file
		else:
			self.ledger = []
			self.accepted = []
	def save(self):
	def load(self):
		


		
		
