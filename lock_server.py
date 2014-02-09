############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		Lock server and lock server manager impl
##				implementation.
############################################################	

import pipe
import Queue
from threading import Thread
import os
import random
import time
import countvotes

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
		self.manager_comm = Queue.Queue() # just use a regular queue for this


		# maps round --> psn generator
		self.psns = dict() # an empty dictionary of unique psns 
	
	def create_instances(self):
		# run the required number of lock servers
		for i in range(self.num_servers):
			LockServerThread(i, self.paxos_comm, self.server_client_comm[i], self.manager_comm).run()

	def manage_servers(self):
		# TODO: need to do something other than busy wait
		while True:
			# listen for messages from servers
			# if server has failed, wait a timeout period and initialize a new server
			if not self.manager_comm.empty():
				s_id, timeout = manager_comm.get()
				threading.Thread(target=init_new_server, arg=[s_id, self.paxos_comm, self.server_client_comm[s_id], manager_comm,timeout]).start()
	
	def run(self):
		self.create_instances()
		self.manage_servers()

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
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0, maj_threshold):
		Thread.__init__(self)

		# initialize data fields
		self.id_num = id_num
		self.paxos_comm = paxos_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		#self.ledger = []
		self.server_data = ServerData(id_num)
		self.fail_rate = fail_rate
		self.maj_threshold = maj_threshold

	
	# will run the paxos protocol
	def run(self):
		print "server %d running" % self.id_num
		#return "unimplemented"

		# if previously saved file exists then initialize from it
		# if received a client request => propose it.

		# listen for msgs from other servers, and 
		# process according to state and message type
			# if proposal and haven't seen any other 
			# proposal then accept 

			# if 

		# save any new state in ledger or instance state
		# repeat
	
	def prepare_msg(self,round_no):
	    psn = get_lock_server().get_psn(round_no)
	    return Message('prepare',psn,0,round_no,0,0)
	    
	def promise_msg(self,round_no,prepare_psn):
	    (highest_psn,val) = self.server_data.highest_accepted(round_no)
	    if prepare_psn > highest_psn:
	         msg = Message('promise',highest_psn,val,round_no,val[0],val[1])
	         return msg
	    else:
	        return None
	        
	def accept_msg(self,round_no,list_val,psn):
	    maj = majority(list_val,self.maj_threshold)
	    if maj[0] == 0:
	        return None
	    else:
	        return Message('accept',psn,maj[1],round_no,maj[1][0],maj[1][1])
	    
    def accepted_msg(self,message):
        if message.psn >= self.server_Data.highest_accepted(message.round_no)[0]:
            return Message('accepted',message.psn,message.val,message.round_no,message.command,message.client_no)
        else if message.val == self.server_Data.highest_accepted(message.round_no)[1]:
            return Message('accepted',message.psn,message.val,message.round_no,message.command,message.client_no)
        else:
            return None
            
    def main(self):
        
	
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


# code to test lock server and manager class

# get lock server
ls = LockServerManager(10)
ls.run()
