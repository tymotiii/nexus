import syscalls

class Scheduler:
    def __init__(self):
        self.running = False
        self.programs = []
    def run(self):
        self.running = True
        while self.running:
            for proc in self.programs:
                if proc["state"] == 0x00:
                    try:
             
                        syscall = next(proc["gen"])
                        if syscall:
                            sendto = syscalls.handle_syscall(syscall, proc)
                            if sendto != "eoo":
                                proc["gen"].send(sendto)
                    except StopIteration:
                        proc["state"] = 0x02
                elif proc["stdin_buffer"] is not None and proc["state"] == 0x01:
                    proc["gen"].send(proc["stdin_buffer"])
                    proc["stdin_buffer"] = None
    def add_process(self, pname,gen):
        self.programs.append( {
            "pid": len(self.programs) + 1,
            "gen": gen,
            "state": 0x00,
            "name": pname,
            "stdin_buffer": None
        } )