class Proposal():
	""" val = (cmd, lock, client)"""
	def __init__(self, psn, round_num, val):
		self.psn, self.round_num, self.val = psn, round_num, val
		
# base message class
class Message:
		def __init__(self, proposal):
			self.proposal = proposal

		def msg_str(self):
			proposal = self.proposal
			return str( (proposal.psn, proposal.round_num, proposal.val))

## message types
class PrepareMsg(Message):
	def __init__(self, sender, proposal):
		Message.__init__(self, proposal)
		self.sender = sender
class ProposalMsg(Message):
	def __init__(self, proposal):
		# NOTE: the proposal value doesn't matter in this message, can be ignored
		Message.__init__(self, proposal)
class PromiseMsg(Message):
	def __init__(self, server_id, orig_proposal, accepted_proposal):
		Message.__init__(self, orig_proposal)
		self.server_id			= server_id
		self.orig_proposal 		= orig_proposal # proposal number in received Proposal message
		self.accepted_proposal	= accepted_proposal
class VoteMsg(Message):
	def __init__(self, voter_id, proposal):
		Message.__init__(self, proposal)
		self.voter_id = voter_id

# Request missing data
class DecisionRequest(Message):
		# NOTE: the proposal value doesn't matter in this message, can be ignored
	def __init__(self, sender, proposal):
		Message.__init__(self, proposal)
		self.sender = sender
class DecisionResponse(Message):
		# NOTE: the proposal value doesn't matter in this message, can be ignored
	def __init__(self, proposal):
		Message.__init__(self, proposal)
    

## there will not be a class for client messages, instead we will use
## tuple with values (cmd, lock, client_id)
## NOTE: this tuple also corresponds to a value!!
#class Client_Msg:
#    def __init_(self,command)
#        self.command = command

