from time import sleep
import pipe
import threading 

class Command:
    def __init__(self,cmd_type,cmd_arg):
        self.cmd_type = cmd_type
        self.cmd_arg = cmd_arg
        
class Client:
    #def __init__():
        
    def read_inst(self,filename):
        f = open(filename)
        lines = [line.strip() for line in f]
        f.close()
        return lines
    def sleep(self,delay):
        time.sleep(time) # it sleeps for (time) seconds
    def parse_command(self,command):
        inst = command.split(' ',1)
        cmd = Command(inst[0],inst[1])
        return cmd
    def main_client(self,instr_file):
        instrs = self.read_inst(instr_file)
        for instr in instrs:
            cmd = self.parse_command(instr)
            if cmd.cmd_type == 'obtain_lock':
                print cmd.cmd_type
                #send lock number request
            if cmd.cmd_type == 'sleep':
                sleep(int(cmd.cmd_arg))
            if cmd.cmd_type == 'release_lock':
                cmd.cmd_type
                # send lock release request
                
def spawn_clients(num,file_names):
     for i in range(num):
        client = Client()
        threading.Thread(target=client.main_client, args=[file_names[i]]).start()

cl = Client()
cl.main_client('test')

