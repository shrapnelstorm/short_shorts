================================================================================
Authors:		Sivaramakrishnan Natarajan Ramamoorthy	[1323328] (sivanr@cs.washington.edu)
				Armando Diaz Tolentino	[1323261] (ajdt@cs.washington.edu)

Course: 		CSE 550
Instructor:		Arvind Krishnamurthy
Quarter:		Winter 2014

Desc:			This repository contains code for the second systems
				assignment, a simple implementation of the paxos
				protocol. Our code is written in the python language.
================================================================================

#### Usage Instructions ########################

# run the server
python lock_server.py

# to kill the server
type ctrl-c when the server is running


################################################################################
##							features
################################################################################
Communication Failures:
* packet loss --
	Our server instances communicate using a Queue object that
	is wrapped by our own class, Pipe. This is configured
	with the loss_factor field passed to a Pipe instance.
* Additional features --
	The Pipe class contains fields for message reordering,
	and message latency. These features remain untested
	as they are not required by the project description.

* node failure -- 
	Node failure is achieved by passing a parameter
	to a LockServerThread instance that causes the
	thread instance to immediately fail upon execution.
* node recovery -- 
	A crude mechanism is in place for recovering a node
	that has failed. The LockServerManager class 
	spawns a new thread to replace a failed LockServerThread.
	The LockServerThread() then reads persistent data
	from a file that is periodically saved to.

################################################################################
##							implementation: Overview
################################################################################
We first describe our project's organization into files, followed by a more
detailed description of the class-level organization.

* lock_server.py	--	Contains the classes: LockServerManager, LockServerThread
						Client, and code to run the project.
* message.py		--	Contains the message classes encapsulating different
						types of messages required by our protocol as well
						as a Proposal class.
* ServerData.py		--	Contains all persistent data inside the ServerData
						class. Additional classes include the Ledger class
						to store chosen values for a round, the VoteTally
						class used to record vote and promise messages
						received, and a Lock_Status class used to 
						manage locks.
* Clients/			--	This is a directory where several client files
						are kept, instructing clients on how to request locks.

################################################################################
##							implementation: Class Overview
################################################################################
Here we describe the function and role of the major classes in our project.

* LockServerManager	--	Initializes and spawns LockServerThread instances which
						run the paxos protocol. Creates the Pipes (communication
						channels) used by both client and LockServerManager threads.
						This manager class also contains code to print debug messages
						and return a unique proposal number to a requesting
						LockServerThread
* LockServerThread	--	Runs the paxos protocol with other class instances that
						run on separate threads. Records decisions in a Ledger
						class instance, and keeps persistent data in a ServerData
						instance.
* ServerData		--	Maintains and restores (upon recovery) all persistent data
						required by a LockServerThread instance. Such data
						includes all promises made, accepted proposals, pending
						requests and (via the VoteTally class) vote counts 
						for proposals. Data must be explicitly saved by
						LockServerThread(), and is dumped into a file
						using the pickle module (a python object 
						serialization library).
* VoteTally			--	Keeps a count of votes received for a particular proposal.
						This class is used to keep track of both votes and 
						promise messages received. The return value of 
						add_vote() indicates when a majority has been attained.
* Ledger			--	This class stores the decisions that have been reached
						by LockServerThreads for each round, and indicates when
						a value is missing for a particular round. The name
						for the class comes from the Parliament analogy
						discussed in class relating to paxos.
* Client			--	The Client class is given a script file as input
						which it parses to complete client actions. Only
						three possible actions exist: releasing/requesting
						locks, and sleeping for a given time period (in seconds).
						Clients are generated as separate threads by the
						spawn_clients() function.
* Proposal			--	This class encapsulates a proposal and all the 
						data germane to it: proposal number, round number,
						and value. In our application, a value is a 3-tuple
						containing (cmd, lock_number, client_id), where 
						command is either obtain_lock or release_lock
* Message			--	The base class for all message types. The base class
						takes a proposal as its only parameter. A subclass
						exists for each type of message sent by our paxos
						implementation. Subclasses also accept additional
						parameters depending on the particular message.
						For example, our VoteMsg class contains a 
						voter_id field so that we can be sure to tally
						unique votes.
* Pipe				--	This class represents a one way communication channel.
						This is done by wrapping the python Queue class.
						The Queue class is thread-safe. We wrap the class
						to introduce message loss.
	

################################################################################
##							implementation: Tradeoffs and Decisions
################################################################################
LANGUAGE:
We've chosen the python language for our implementation due to the flexibility
that dynamic typing allowed us. Development proceeded very experimentally and
in an ad hoc fashion after a first draft was written. Certain language features
allowed us to react and patch up emergent issues much more quickly.

THREADS:
Our implementation uses threads rather than independent processes. 
This decision largely rests on the use of a single LockServerManager. 
We chose for this manager class to be a singleton, and to encapsulate certain
global features/properties like: returning unique proposal numbers, and allowing 
concurrent printing to the console. Such features would be
harder to implement in a multi-process setting, or so we felt.

COMMUNICATION
We elected to have one communication channel open per LockServerThread
for running the paxos protocol. This means the Pipe instance to 
server n is shared by all the other servers. The underlying Queue class
ensures the channel is used in a consistent way since it's thread safe.
This choice was mainly to avoid creation of a large number of pipes.
However, it may unnecessarily slow down our implementation.

ADDITIONAL INVARIANTS ENFORCED
In order to avoid message reordering, or assigning the same lock to
multiple clients. Our paxos implementation enforces that no 
LockServerThread instance may propose values unless it's 
ledger is not missing any values. Additionally, each server
may only propose one value at a time. Periodically, a server
takes the top request from its pending_requests queue, and 
issues a prepare request on only this value.
Though our implemention is multi-round, the next round
proceeds only after the current round has completed.

Our paxos implementation also introduces two new message types:
DecisionRequestMsg and DecisionResponseMsg. These messages
are for a server to request decisions that are missing from 
its ledger, and for another server to respond with the 
requested data (if available). Paxos solves this
problem by having a server issue a prepare request on
the missing round. We've implemented this alternate
procedure for efficiency reasons.

################################################################################
##							Quirks, Messups and Other Issues
################################################################################




