"""
ViImage - compiled kernel
build: 2026-05-16T11:12:37.420793
"""

# ===== core/!syscalls.py =====
import enum, threading, time

class Syscalls(enum.IntEnum):
    #I/O
    PRINT     = 0x13
    INPUT     = 0x01

    #PROCESSES
    SLEEP     = 0x02
    EXIT      = 0x03
    KILL      = 0x04
    GETPPID   = 0x06
    GETPID    = 0x07
    SPAWN     = 0x08

    #FILES
    READ      = 0x09
    WRITE     = 0x0a
    LIST_DIR  = 0x0b
    EXISTS    = 0x0c

    #IPC
    SEND      = 0x0d
    RECV      = 0x0e

    #MEMORY
    ALLOC     = 0x0f
    FREE      = 0x10
    READ_MEM  = 0x11
    WRITE_MEM = 0x12

def handle_print(proc, args, krnl):
    print(" ".join(args[0:]))
    return "OK", "OK"

def handle_input(proc, args):
    prompt = " ".join(args[0:]) if args else ""
    proc["state"] = 0x01
    def on_input(text):
        proc["stdin"] = text

    def input_thread():
        text = input(prompt)
        on_input(text)

    t = threading.Thread(target=input_thread, daemon=True)
    t.start()
    return "WAIT", "OK"


def handle_sleep(proc, args, krnl):
    proc["state"] = 0x01
    t = int(args[0])
    def wait_thread():
        time.sleep(t)
        proc["state"] = 0x00

    t = threading.Thread(target=wait_thread, daemon=True)
    t.start()
    return "WAIT", "OK"

def handle_exit(proc, args, krnl):
    proc["state"] = int(args[0]) + 0x02
    print(f"Procces {proc["pid"]}exited with exit code: {int(proc["state"]) - 0x02}" )
    return "OK", "OK"

def handle_getpid(proc, args, krnl):
    return "OK", proc["pid"]

def handle_getppid(proc, args, krnl):
    return "OK", str(proc["parent"])

def handle_spawn(proc,args, krnl):
    pid = krnl.add_process(args[0], args[1](), proc["pid"])
    return "OK", pid

def handle_read(proc, args, krnl):
    with open(args[0], "rb") as f:
        return "OK", f.read(args[1])

def handle_write(proc,args,krnl):
    with open(args[0], "wb") as f:
        f.write(args[1])
        return "OK", "OK"


handlers = {
    Syscalls.PRINT: handle_print,
    Syscalls.INPUT: handle_input,
    Syscalls.SLEEP: handle_sleep,
    Syscalls.EXIT: handle_exit,
    Syscalls.GETPID: handle_getpid,
    Syscalls.GETPPID: handle_getppid,
    Syscalls.SPAWN: handle_spawn,
    Syscalls.READ: handle_read,
    Syscalls.WRITE: handle_write

}

def handle_syscall(syscall, proc, kernel):
    try:
        return handlers[syscall[0]](proc, syscall[1:], kernel)
    except Exception as e:
        return "ERR", e

# ===== core/scheduler.py =====
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
                        print(f"Procces {proc["pid"]}exited with ERROR: exit code: {int(proc["state"]) - 0x02}" )
                elif proc["stdin"] is not None and proc["state"] == 0x01:
                    proc["gen"].send(proc["stdin"])
                    proc["stdin"] = None
                    proc["state"] = 0x00
    def add_process(self, pname,gen, parentpid):
        self.programs.append( {
            "pid": len(self.programs) + 1,
            "gen": gen,
            "state": 0x00,
            "name": pname,
            "stdin": None,
            "parent": parentpid
        } )
        return len(self.programs)

# ===== bpy/preinit.py =====
initf = None

try:
  with open("./sbpy/init.py", "r") as f:
      initf = f.read()
except Exception as e:
  pass

try:
  with open("./init.py", "r") as f:
      initf = f.read()
except Exception as e:
  pass

if initf == None:
    Exception("KERNEL PANIC!!!!!! NO INIT FILE")
else:
    loc = {}
    exec(initf, {}, loc)
    program = loc["run"]


s = Scheduler()
s.add_process("preinit", program(), 0)
s.run()
