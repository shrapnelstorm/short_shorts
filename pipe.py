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


class Pipe:
	"""implements single way communication channel between nodes"""
	def __init__(self, latency=0, reorder_factor=0, loss_factor=0):
		self.latency		= latency
		self.reorder_factor	= reorder_factor
		self.loss_factor	= loss_factor

		self.queue = Queue.Queue(0)
		self.prev_msgs = []
	
	def empty(self):
		return self.queue.empty()

	# returns either the oldest message or None if there aren't any
	# simulates latency and packet reordering
	def get(self):
		# simulate latency in message arriving
		sleep(self.latency)

		# get messages from queue, add to position 0
		while True:
			try:
				self.prev_msgs.insert(0, self.queue.get(block=False))
			except Empty e:
				break # should break from the while loop

		# randomly reorder messages
		if random.randint(0,100) < self.reorder_factor :
			random.shuffle(self.prev_msgs)

		# return highest indexed message
		if not self.prev_msgs.empty:
			return self.prev_msgs.pop()
		else:
			return None

	def put(self, msg):
		# apply loss factor first
		if random.randint(0,100) < self.loss_factor :
			return
		self.queue.put(msg)
		
