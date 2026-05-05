import enum, threading

class Syscalls(enum.IntEnum):
    #I/O
    PRINT     = 0x00
    INPUT     = 0x01
    
    #PROCESSES
    SLEEP     = 0x02
    EXIT      = 0x03
    KILL      = 0x04
    PS        = 0x05
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

def handle_print(proc, args):
    print(" ".join(args[0:]))
    return "eoo"
    
def handle_input(proc, args):
    prompt = " ".join(args[0:]) if args else ""
    proc["status"] = 0x01
    def on_input(text):
        proc["stdin_buffer"] = text
        
    def input_thread():
        text = input(prompt)
        on_input(text)
    
    t = threading.Thread(target=input_thread, daemon=True)
    t.start()
    return "eoo"
    

def handle_sleep(proc, args):
    pass
    
handlers = {
    Syscalls.PRINT: handle_print,
    Syscalls.INPUT: handle_input
}

def handle_syscall(syscall, proc):
    try:
        return handlers[syscall[0]](proc, syscall[1:])
    except Exception as e:
        return e