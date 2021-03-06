#!/usr/bin/env python
############################################################	
## Programmer: 	Armando Diaz Tolentino
## Desc:		This class implements a single-direction
##				communication channel by wrapping
##				the python Queue class
############################################################	
import Queue
import time
import random
import message


class Pipe:
	"""implements single way communication channel between nodes"""

	# initialize new communication channel
	# @param latency seconds until msg is received 
	# @param reorder_factor range: 1 (low) - 100 (high) 
	# @param loss_factor	range: 1 (low) - 100 (high) 
	def __init__(self, loss_factor=0, latency=0, reorder_factor=0):
		self.latency		= latency
		self.reorder_factor	= reorder_factor
		self.loss_factor	= loss_factor

		# queue used to send/receive messages 
		# prev_msgs used to store messages since Queue() class
		# has no size() or reordering functionality
		self.queue = Queue.Queue(0)
		self.prev_msgs = []
	
	def empty(self):
		self.get_msgs()
		return len(self.prev_msgs) == 0

	def get_msgs(self):
		# get messages from queue, add to position 0
		while True:
			try:
				self.prev_msgs.insert(0, self.queue.get(block=False))
			except Queue.Empty:
				break # should break from the while loop

		# randomly reorder messages
		if random.randint(0,100) < self.reorder_factor :
			random.shuffle(self.prev_msgs)

	# returns either the oldest message or None if there aren't any
	# simulates latency and packet reordering
	def get(self):
		# simulate latency in message arriving
		time.sleep(self.latency)

		self.get_msgs()
		# return highest indexed message
		if not self.empty():
			return self.prev_msgs.pop()
		else:
			return None

	# send msg through channel unless message is to be lost randomly
	def put(self, msg):
		# apply loss factor first
		r_value = random.randint(0,100)
		# print loss messages
		#if  r_value < self.loss_factor :
			#if isinstance(msg,message.PrepareMsg): # received prepare, send promise
			#	print "++++++++++++++++++ LOST  prepare:%s" % (msg.msg_str())
			#elif isinstance(msg,message.PromiseMsg): # received promise, send proposal
			#	print "++++++++++++++++++ LOST  promise:%s" % (msg.msg_str())
			#elif isinstance(msg,message.ProposalMsg): # received proposal, send vote
			#	print "++++++++++++++++++ LOST  proposal:%s" % (msg.msg_str())
			#elif isinstance(msg,message.VoteMsg): # tally received votes
			#	print "++++++++++++++++++ LOST  vote:%s" % (msg.msg_str())
			#elif isinstance(msg,message.DecisionRequest):
			#	print "++++++++++++++++++ LOST  drequest:%s" % (msg.msg_str())
			#elif isinstance(msg,message.DecisionResponse):
			#	print "++++++++++++++++++ LOST  drespons:%s" % (msg.msg_str())
			#return
		self.queue.put(msg)
		
#x = Pipe()
#print x.empty()
