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
