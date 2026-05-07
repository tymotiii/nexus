# 🧠 Nexus

A minimalist kernel-like system written in Python.
It supports processes (generator-based), syscalls, and a virtual file system.

The project is inspired by real operating systems, but simplified for learning and experimentation.

---

## 🚀 Features

* ⚙️ Generator-based scheduler (`yield`)
* 📞 Syscall system (PRINT, INPUT, SLEEP, EXIT, etc.)
* 📁 Virtual File System (VFS) stored in JSON
* 🧵 Pseudo-asynchronous operations (threading)
* 🔌 Modular project structure

---

## 📂 Project Structure
```
nexus/
├── core/
│   ├── scheduler.py
│   └── syscalls.py
│
├── fs/
│   └── vfs.py
│
└── main.py
```
---

## ⚙️ How It Works

### 🧵 Processes

A process is a Python generator:

```python
def program():
    yield (0x00, "Hello World")
    name = yield (0x01, "Name: ")
    yield (0x00, "Hello", name)
    yield (0x03,)
```

The scheduler executes processes and interprets `yield` as syscalls.

---

### 📞 Syscalls

Each syscall is a tuple:

(syscall_id, arg1, arg2, ...)

Examples:
```
0x00 → PRINT
0x01 → INPUT
0x02 → SLEEP
0x03 → EXIT
0x07 → GETPID
```
---

### ⚙️ Scheduler

Manages process states:
```
0x00 → RUNNING
0x01 → WAITING
0x02 → EXITED
```
---

### 📁 VFS (Virtual File System)

Data is stored in a `.vfs` file (JSON format).

Example:
```python
from fs.vfs import VFS

vfs = VFS("disk.vfs")

vfs.create_folder("/docs")
vfs.write_file("/docs/test.txt", "hello")
print(vfs.read_file("/docs/test.txt"))
```
---

## ▶️ How to Run
```shell
git clone https://github.com/tymotiii/nexus
cd nexus
python main.py
```
---

## 🧠 Roadmap

* [ ] Process management (SPAWN / KILL)
* [ ] IPC (SEND / RECV)
* [ ] Memory management (ALLOC / FREE)
* [ ] Permissions (rw, user space)
* [ ] /proc-like system
* [ ] Better scheduler (priority, round-robin)

---

## ⚠️ Disclaimer

This is not a real kernel.
It is a simulation for learning and experimentation purposes.

---

## 👤 Author

Tymoti
