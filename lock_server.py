############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		Lock server and lock server manager impl
##				implementation.
############################################################	

import pipe
import Queue
import threading
from threading import Thread
import threading
import os
import random
import time
from time import sleep




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

	def __init__(self, n_serv=10):
		self.num_servers = n_serv
		self.server_client_comm = [pipe.Pipe() for i in range(n_serv)]
		self.paxos_comm = [pipe.Pipe() for i in range(n_serv)]
		self.manager_comm = Queue.Queue() # just use a regular queue for this


		# maps round --> psn generator
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
	def __init__(self, id_num, paxos_comm, client_comm, manager_comm, fail_rate=0):
		Thread.__init__(self)

		print id_num
		# initialize data fields
		self.id_num = id_num
		self.paxos_comm = paxos_comm
		self.client_comm = client_comm
		self.manager_comm = manager_comm
		#self.ledger = []
		self.fail_rate = fail_rate

	
	# will run the paxos protocol
	def run(self):
		while True:
			if not self.client_comm.empty():
				print "%d received message" % self.id_num
				print str(self.client_comm.get().cmd_type)
		# TODO: delete this test code
		#if self.id_num == 9:
		#	time.sleep(1)
		#	self.manager_comm.put((self.id_num, 5))

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
	


############################################################	
## Programmer: 	Siva
## Desc:		Client class
############################################################	
class Command:
    def __init__(self,cmd_type,cmd_arg):
        self.cmd_type = cmd_type
        self.cmd_arg = cmd_arg
	def __str__(self):
		return "bacon" #self.cmd_type + " " + self.cmd_arg
        
class Client(Thread):
    
    def __init__(self, id_num, filename):
        Thread.__init__(self)
        self.id_num = id_num
        self.filename = filename
        # get handle to lock servers, and server manager
        self.ls_mgr = get_lock_server()
        self.servers = self.ls_mgr.server_client_comm 
        
    def read_inst(self):
        f = open(self.filename)
        lines = [line.strip() for line in f]
        f.close()
        return lines
    def sleep(self,delay):
        time.sleep(delay) # it sleeps for (time) seconds
    def parse_command(self,command):
        inst = command.split(' ',1)
        cmd = Command(inst[0],inst[1])
        return cmd

    def send_to_server(self, cmd):
        rand_server = random.randint(0,self.ls_mgr.num_servers - 1)
        self.servers[rand_server].put(cmd)
        print cmd.cmd_type + " id:" + str(self.id_num) + " to server " + str(rand_server)

    def run(self):
        instrs = self.read_inst()
        for instr in instrs:
            cmd = self.parse_command(instr)
            if cmd.cmd_type == 'obtain_lock':
                #send lock number request
                self.send_to_server(cmd)
            if cmd.cmd_type == 'sleep':
                print cmd.cmd_type + str(self.id_num)
                sleep(int(cmd.cmd_arg))
            if cmd.cmd_type == 'release_lock':
                # send lock release request
                self.send_to_server(cmd)
                
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
ls = LockServerManager(10)
LS_MGR = ls
spawn_clients(len(file_names), file_names)
ls.run()


