#TODO:
#	client file: blank lines cause crashes !!
from time import sleep
import pipe
import threading 
from threading import Thread
import random
import lock_server

class Command:
    def __init__(self,cmd_type,cmd_arg):
        self.cmd_type = cmd_type
        self.cmd_arg = cmd_arg
        
class Client(Thread):
    
    def __init__(self, id_num, filename):
        Thread.__init__(self)
        self.id_num = id_num
        self.filename = filename
        # get handle to lock servers, and server manager
        self.ls_mgr = lock_server.get_lock_server()
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
        self.servers[random.randint(0,self.ls_mgr.num_servers)].put(cmd)

    def run(self):
        instrs = self.read_inst()
        for instr in instrs:
            print "hello world"
            cmd = self.parse_command(instr)
            if cmd.cmd_type == 'obtain_lock':
                print cmd.cmd_type + str(self.id_num)
                #send lock number request
                self.send_to_server(cmd)
            if cmd.cmd_type == 'sleep':
                print cmd.cmd_type + str(self.id_num)
                sleep(int(cmd.cmd_arg))
            if cmd.cmd_type == 'release_lock':
                print cmd.cmd_type + str(self.id_num)
                cmd.cmd_type
                # send lock release request
                self.send_to_server(cmd)
                
        print "done"
def spawn_clients(num,file_names):
     for i in range(num):
        print "spawning client"
        client = Client(i, file_names[i]).run()
