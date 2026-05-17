import time

class Scheduler:
    def __init__(self):
        self.running = False
        self.programs = []
    def run(self):
        self.running = True
        while self.running:
            time.sleep(0.001)
            for proc in self.programs:
                if proc["state"] == 0x00:
                    try:
                        syscall = next(proc["gen"])
                        if syscall is None:
                          continue
                        status, result = handle_syscall(syscall, proc, self)
                        if status == "OK":
                            try:
                                proc["gen"].send(result)
                            except TypeError:
                                # generator nie oczekuje send (pierwszy run)
                                next(proc["gen"])
                        elif status == "WAIT":
                            continue
                        else:
                            proc["gen"].throw(Exception(result))

                    except StopIteration:
                        proc["state"] = 0x03
                elif proc["stdin"] is not None and proc["state"] == 0x01:
                    proc["gen"].send(proc["stdin"])
                    proc["stdin"] = None
                    proc["state"] = 0x00
    def add_process(self, pname,gen, parentpid, envi):
        self.programs.append( {
            "pid": len(self.programs) + 1,
            "gen": gen,
            "state": 0x00,
            "name": pname,
            "stdin": None,
            "parent": parentpid,
            "env": envi
        } )
        return len(self.programs)
