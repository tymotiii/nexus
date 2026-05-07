# 🧠 Nexus

Minimalistyczny kernel-like system napisany w Pythonie.
Obsługuje procesy (generator-based), syscalle i wirtualny system plików.

Projekt inspirowany działaniem prawdziwych systemów operacyjnych, ale uproszczony do nauki i eksperymentów.

---

## 🚀 Features

* ⚙️ Scheduler oparty o generatory (`yield`)
* 📞 System syscalli (PRINT, INPUT, SLEEP, EXIT itd.)
* 📁 Virtual File System (VFS) zapisany w JSON
* 🧵 Pseudo-asynchroniczne operacje (threading)
* 🔌 Modularna struktura projektu

---

## 📂 Struktura projektu

nexus/
├── core/
│   ├── scheduler.py
│   └── syscalls.py
│
├── fs/
│   └── vfs.py
│
└── main.py

---

## ⚙️ Jak to działa

### 🧵 Procesy

Proces to generator:

def program():
yield (0x00, "Hello World")
name = yield (0x01, "Imię: ")
yield (0x00, "Hej", name)
yield (0x03,)

Scheduler wykonuje procesy i interpretuje `yield` jako syscalle.

---

### 📞 Syscalle

Każdy syscall to tuple:

(syscall_id, arg1, arg2, ...)

Przykłady:

0x00 → PRINT
0x01 → INPUT
0x02 → SLEEP
0x03 → EXIT
0x07 → GETPID

---

### ⚙️ Scheduler

Zarządza procesami:

0x00 → RUNNING
0x01 → WAITING
0x02 → EXITED

---

### 📁 VFS (Virtual File System)

Dane trzymane w pliku `.vfs` (JSON).

Przykład:

from fs.vfs import VFS

vfs = VFS("disk.vfs")

vfs.create_folder("/docs")
vfs.write_file("/docs/test.txt", "hello")
print(vfs.read_file("/docs/test.txt"))

---

## ▶️ Jak uruchomić

git clone https://github.com/tymotiii/nexus
cd nexus
python main.py

---

## 🧠 Roadmap

* [ ] SPAWN / KILL procesów
* [ ] IPC (SEND / RECV)
* [ ] Memory management (ALLOC / FREE)
* [ ] Permissions (rw, user space)
* [ ] /proc-like system
* [ ] Lepszy scheduler (priority, round-robin)

---

## ⚠️ Disclaimer

To nie jest prawdziwy kernel.
To symulacja do nauki i eksperymentów.

---

## 👤 Autor

Tymoti
