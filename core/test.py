import scheduler, syscalls

s = scheduler.Scheduler()
def generative():
    data = yield [syscalls.Syscalls.INPUT, "test > "]
    yield
    print(data)
    yield
        

s.add_process("test", generative())
s.run()