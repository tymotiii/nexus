import enum, threading, time
ENV = {}
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

    #LIB
    IMPORT    = 0x14

    #ENV VARIABLES
    SETENV    = 0x15
    GETENV    = 0x16

def handle_print(proc, args, krnl):
    print(" ".join(args[0:]))
    return "OK", "OK"

def handle_input(proc, args, krnl):
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
    return "OK", "OK"

def handle_getpid(proc, args, krnl):
    return "OK", proc["pid"]

def handle_getppid(proc, args, krnl):
    return "OK", str(proc["parent"])

def handle_spawn(proc,args, krnl):
    # print(f"DEBUG: CREATED PROCESS WITH THIS DATA: {args[0]}, {args[1]()}, {proc['pid']}, {proc['env'].copy()}")
    pid = krnl.add_process(args[0], args[1](), proc["pid"], proc["env"].copy())
    return "OK", pid

def handle_read(proc, args, krnl):
    with open(args[0], "rb") as f:
        return "OK", f.read(args[1])

def handle_write(proc,args,krnl):
    with open(args[0], "wb") as f:
        f.write(args[1])
        return "OK", "OK"

import os
import importlib
import importlib.util

def handle_exists(proc,args,krnl):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args[0].lstrip("/"))
    return "OK", {
        "exists": os.path.exists(path),
        "is_dir": os.path.isdir(path),
        "is_file": os.path.isfile(path)
    }
def import_from_lib(name):
    path = os.path.join("lib", name + ".py")

    if not os.path.exists(path):
        raise Exception(f"Module {name} not found in lib")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module

def handle_import(proc,args,krnl):
    return "OK", import_from_lib(args[0])

def handle_setenv(proc,args,krnl):
    key = args[0]
    val = args[1]
    proc["env"][key] = val
    return "OK", "OK"

def handle_getenv(proc,args,krnl):
    key = args[0]
    return "OK", proc["env"].get(key)


handlers = {
    Syscalls.PRINT: handle_print,
    Syscalls.INPUT: handle_input,
    Syscalls.SLEEP: handle_sleep,
    Syscalls.EXIT: handle_exit,
    Syscalls.GETPID: handle_getpid,
    Syscalls.GETPPID: handle_getppid,
    Syscalls.SPAWN: handle_spawn,
    Syscalls.READ: handle_read,
    Syscalls.WRITE: handle_write,
    Syscalls.EXISTS: handle_exists,
    Syscalls.IMPORT: handle_import,
    Syscalls.SETENV: handle_setenv,
    Syscalls.GETENV: handle_getenv

}

def handle_syscall(syscall, proc, kernel):
    try:
        return handlers[syscall[0]](proc, syscall[1:], kernel)
    except Exception as e:
        return "ERR", e
