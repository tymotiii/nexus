"""
vfs.py - Virtual File System
Dane trzymane w pliku .vfs (format JSON).
"""

import json
import os
import time
from pathlib import Path
from typing import Optional


# ─── Wewnętrzna struktura ────────────────────────────────────────────────────
#
#  {
#    "meta": { "version": 1, "created": <timestamp> },
#    "fs": {
#      "/": {
#        "type": "dir",
#        "created": <ts>,
#        "modified": <ts>,
#        "children": {
#          "docs": { "type": "dir", ... },
#          "readme.txt": { "type": "file", "content": "...", ... }
#        }
#      }
#    }
#  }
# ─────────────────────────────────────────────────────────────────────────────


class VFSError(Exception):
    pass


class NotFoundError(VFSError):
    pass


class AlreadyExistsError(VFSError):
    pass


class NotADirectoryError(VFSError):
    pass


class NotAFileError(VFSError):
    pass


class VFS:
    VERSION = 1

    def __init__(self, vfs_path: str):
        self.vfs_path = Path(vfs_path)
        if self.vfs_path.exists():
            self._load()
        else:
            self._init_empty()

    # ── Zapis / odczyt pliku .vfs ────────────────────────────────────────────

    def _init_empty(self):
        self._data = {
            "meta": {"version": self.VERSION, "created": _now()},
            "fs": {
                "/": _make_dir()
            },
        }
        self._save()

    def _load(self):
        with open(self.vfs_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    def _save(self):
        with open(self.vfs_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ── Nawigacja po drzewie ─────────────────────────────────────────────────

    def _parts(self, path: str) -> list[str]:
        """Normalizuje ścieżkę i zwraca listę segmentów (bez root '/')."""
        p = path.strip()
        if not p.startswith("/"):
            p = "/" + p
        parts = [s for s in p.split("/") if s]
        return parts

    def _root(self) -> dict:
        return self._data["fs"]["/"]

    def _resolve(self, path: str) -> dict:
        """Zwraca węzeł dla podanej ścieżki lub rzuca NotFoundError."""
        parts = self._parts(path)
        node = self._root()
        for part in parts:
            if node["type"] != "dir":
                raise NotFoundError(f"Ścieżka nie istnieje: {path}")
            children = node.get("children", {})
            if part not in children:
                raise NotFoundError(f"Nie znaleziono: '{part}' w ścieżce '{path}'")
            node = children[part]
        return node

    def _resolve_parent(self, path: str) -> tuple[dict, str]:
        """Zwraca (węzeł_rodzic, nazwa_ostatniego_segmentu)."""
        parts = self._parts(path)
        if not parts:
            raise VFSError("Operacja na katalogu głównym niedozwolona.")
        parent_parts = parts[:-1]
        name = parts[-1]
        node = self._root()
        for part in parent_parts:
            if node["type"] != "dir":
                raise NotADirectoryError(f"'{part}' nie jest katalogiem.")
            children = node.get("children", {})
            if part not in children:
                raise NotFoundError(f"Katalog nie istnieje: '{part}'")
            node = children[part]
        if node["type"] != "dir":
            raise NotADirectoryError("Rodzic nie jest katalogiem.")
        return node, name

    # ── API ──────────────────────────────────────────────────────────────────

    def create_file(self, path: str, content: str = "") -> None:
        """Tworzy plik pod podaną ścieżką."""
        parent, name = self._resolve_parent(path)
        children = parent.setdefault("children", {})
        if name in children:
            raise AlreadyExistsError(f"'{path}' już istnieje.")
        children[name] = _make_file(content)
        parent["modified"] = _now()
        self._save()

    def create_folder(self, path: str) -> None:
        """Tworzy katalog (tworzy też brakujące katalogi pośrednie)."""
        parts = self._parts(path)
        node = self._root()
        for part in parts:
            children = node.setdefault("children", {})
            if part not in children:
                children[part] = _make_dir()
                node["modified"] = _now()
            node = children[part]
            if node["type"] != "dir":
                raise NotADirectoryError(f"'{part}' nie jest katalogiem.")
        self._save()

    def read_file(self, path: str) -> str:
        """Zwraca zawartość pliku."""
        node = self._resolve(path)
        if node["type"] != "file":
            raise NotAFileError(f"'{path}' nie jest plikiem.")
        return node["content"]

    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """Nadpisuje lub dopisuje do pliku (tworzy go jeśli nie istnieje)."""
        try:
            node = self._resolve(path)
            if node["type"] != "file":
                raise NotAFileError(f"'{path}' nie jest plikiem.")
            if append:
                node["content"] += content
            else:
                node["content"] = content
            node["modified"] = _now()
        except NotFoundError:
            self.create_file(path, content)
            return
        self._save()

    def delete_file(self, path: str) -> None:
        """Usuwa plik."""
        parent, name = self._resolve_parent(path)
        children = parent.get("children", {})
        if name not in children:
            raise NotFoundError(f"Plik nie istnieje: '{path}'")
        if children[name]["type"] != "file":
            raise NotAFileError(f"'{path}' nie jest plikiem. Użyj delete_folder.")
        del children[name]
        parent["modified"] = _now()
        self._save()

    def delete_folder(self, path: str, recursive: bool = False) -> None:
        """Usuwa katalog. Wymaga recursive=True jeśli nie jest pusty."""
        parent, name = self._resolve_parent(path)
        children = parent.get("children", {})
        if name not in children:
            raise NotFoundError(f"Katalog nie istnieje: '{path}'")
        node = children[name]
        if node["type"] != "dir":
            raise NotADirectoryError(f"'{path}' nie jest katalogiem.")
        if node.get("children") and not recursive:
            raise VFSError(f"Katalog '{path}' nie jest pusty. Użyj recursive=True.")
        del children[name]
        parent["modified"] = _now()
        self._save()

    def dir_folder(self, path: str = "/") -> list[dict]:
        """
        Zwraca listę wpisów w katalogu.
        Każdy wpis: {"name": str, "type": "file"|"dir", "size": int, ...}
        """
        node = self._resolve(path)
        if node["type"] != "dir":
            raise NotADirectoryError(f"'{path}' nie jest katalogiem.")
        result = []
        for name, child in node.get("children", {}).items():
            entry = {
                "name": name,
                "type": child["type"],
                "created": child["created"],
                "modified": child["modified"],
            }
            if child["type"] == "file":
                entry["size"] = len(child["content"].encode("utf-8"))
            else:
                entry["items"] = len(child.get("children", {}))
            result.append(entry)
        return sorted(result, key=lambda e: (e["type"] == "file", e["name"]))

    def move(self, src: str, dst: str) -> None:
        """Przenosi plik lub katalog."""
        src_parent, src_name = self._resolve_parent(src)
        src_children = src_parent.get("children", {})
        if src_name not in src_children:
            raise NotFoundError(f"Nie znaleziono: '{src}'")
        node = src_children.pop(src_name)
        src_parent["modified"] = _now()

        dst_parent, dst_name = self._resolve_parent(dst)
        dst_children = dst_parent.setdefault("children", {})
        if dst_name in dst_children:
            raise AlreadyExistsError(f"Cel '{dst}' już istnieje.")
        dst_children[dst_name] = node
        dst_parent["modified"] = _now()
        self._save()

    def copy(self, src: str, dst: str) -> None:
        """Kopiuje plik lub katalog (deep copy)."""
        import copy as _copy
        node = self._resolve(src)
        node_copy = _copy.deepcopy(node)
        node_copy["created"] = _now()
        node_copy["modified"] = _now()

        dst_parent, dst_name = self._resolve_parent(dst)
        dst_children = dst_parent.setdefault("children", {})
        if dst_name in dst_children:
            raise AlreadyExistsError(f"Cel '{dst}' już istnieje.")
        dst_children[dst_name] = node_copy
        dst_parent["modified"] = _now()
        self._save()

    def exists(self, path: str) -> bool:
        """Sprawdza czy ścieżka istnieje."""
        try:
            self._resolve(path)
            return True
        except (NotFoundError, VFSError):
            return False

    def info(self, path: str) -> dict:
        """Zwraca metadane węzła."""
        node = self._resolve(path)
        result = {
            "path": path,
            "type": node["type"],
            "created": node["created"],
            "modified": node["modified"],
        }
        if node["type"] == "file":
            result["size"] = len(node["content"].encode("utf-8"))
        else:
            result["items"] = len(node.get("children", {}))
        return result

    def tree(self, path: str = "/", _indent: int = 0) -> str:
        """Zwraca drzewo katalogów jako string."""
        node = self._resolve(path)
        name = path.split("/")[-1] or "/"
        icon = "📁" if node["type"] == "dir" else "📄"
        lines = [" " * _indent + f"{icon} {name}"]
        if node["type"] == "dir":
            for child_name in sorted(node.get("children", {})):
                child_path = (path.rstrip("/") + "/" + child_name)
                lines.append(self.tree(child_path, _indent + 4))
        return "\n".join(lines)

    def find(self, name: str, path: str = "/") -> list[str]:
        """Szuka plików/folderów po nazwie (obsługuje wildcard *)."""
        import fnmatch
        results = []
        self._find_recursive(name, path, results, fnmatch)
        return results

    def _find_recursive(self, pattern: str, path: str, results: list, fnmatch):
        node = self._resolve(path)
        if node["type"] == "dir":
            for child_name, child in node.get("children", {}).items():
                child_path = path.rstrip("/") + "/" + child_name
                if fnmatch.fnmatch(child_name, pattern):
                    results.append(child_path)
                if child["type"] == "dir":
                    self._find_recursive(pattern, child_path, results, fnmatch)

    def disk_usage(self) -> dict:
        """Zwraca statystyki użycia (pliki, katalogi, łączny rozmiar)."""
        stats = {"files": 0, "dirs": 0, "total_bytes": 0}
        self._du_recursive(self._root(), stats)
        return stats

    def _du_recursive(self, node: dict, stats: dict):
        if node["type"] == "file":
            stats["files"] += 1
            stats["total_bytes"] += len(node["content"].encode("utf-8"))
        else:
            stats["dirs"] += 1
            for child in node.get("children", {}).values():
                self._du_recursive(child, stats)

    def format(self) -> None:
        """Czyści cały system plików (zostawia tylko root)."""
        self._data["fs"]["/"] = _make_dir()
        self._save()


# ── Helpery ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _make_file(content: str = "") -> dict:
    ts = _now()
    return {"type": "file", "content": content, "created": ts, "modified": ts}


def _make_dir() -> dict:
    ts = _now()
    return {"type": "dir", "children": {}, "created": ts, "modified": ts}