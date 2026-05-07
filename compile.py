import os
from pathlib import Path
from datetime import datetime

CORE_FILES = [
    "core/!syscalls.py",
    "core/scheduler.py",
    "core/!avfs.py",
]

OUTPUT_FILE = "ViImage.py"


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def strip_file(content: str) -> str:
    lines = content.splitlines()
    out = []

    for line in lines:
        stripped = line.strip()

        # usuń importy lokalne (żeby nie było konfliktów)
        if stripped.startswith("from core") or stripped.startswith("import core"):
            continue

        out.append(line)

    return "\n".join(out)


def dedupe(files: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen = set()
    result = []

    for name, content in files:
        if content in seen:
            continue
        seen.add(content)
        result.append((name, content))

    return result


def build():
    files = []

    for path in CORE_FILES:
        if not os.path.exists(path):
            raise Exception(f"Brak pliku: {path}")

        content = read_file(path)
        files.append((path, content))

    # usuń duplikaty
    files = dedupe(files)

    # strip importów
    files = [(name, strip_file(content)) for name, content in files]

    # HEADER
    header = f'''"""
ViImage - compiled kernel
build: {datetime.now().isoformat()}
"""

'''

    # BODY
    body_parts = []

    for name, content in files:
        part = f"# ===== {name} =====\n{content}\n"
        body_parts.append(part)

    body = "\n".join(body_parts)

    # FOOTER (bootstrap + API)
    footer = """"""

    final_code = header + body + footer

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_code)

    print(f"[OK] Zbudowano {OUTPUT_FILE}")


if __name__ == "__main__":
    build()