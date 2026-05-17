import subprocess, sys, os
def ensure_profile(name):
    if f"--{name}" not in sys.argv:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        subprocess.Popen([
            "wt",
            "-p", name,
            "cmd", "/k",
            f'cd /d "{script_dir}" && py "{__file__}" --{name}'
        ])

        sys.exit()
ensure_profile("TVEMU")
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
s.add_process("preinit", program(), 0, {})
s.run()
