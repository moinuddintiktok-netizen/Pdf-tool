
from pathlib import Path
import hashlib
import os
import shutil
import tempfile
import platform


SAFE_TEMP_ROOTS = [
    Path(tempfile.gettempdir()),
    Path.home() / "AppData" / "Local" / "Temp",
]
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".dart", ".json", ".xml", ".yml", ".yaml"},
}


def scan_temp_files():
    found = []
    total = 0
    seen = set()
    for root in SAFE_TEMP_ROOTS:
        try:
            root = root.resolve()
        except Exception:
            continue
        if not root.exists() or root in seen:
            continue
        seen.add(root)
        for base, dirs, files in os.walk(root):
            for name in files:
                path = Path(base) / name
                try:
                    if path.is_symlink():
                        continue
                    size = path.stat().st_size
                    found.append(path)
                    total += size
                except (OSError, PermissionError):
                    pass
    return found, total


def clean_paths(paths):
    deleted = 0
    freed = 0
    for path in paths:
        try:
            if path.is_file() and not path.is_symlink():
                size = path.stat().st_size
                path.unlink()
                deleted += 1
                freed += size
        except (OSError, PermissionError):
            pass
    return deleted, freed


def organize_folder(folder):
    folder = Path(folder)
    moved = 0
    for item in list(folder.iterdir()):
        if not item.is_file() or item.name.startswith("."):
            continue
        ext = item.suffix.lower()
        category = next((name for name, exts in CATEGORIES.items() if ext in exts), "Others")
        target = folder / category
        target.mkdir(exist_ok=True)
        destination = target / item.name
        if destination.exists():
            stem, suffix = item.stem, item.suffix
            counter = 2
            while destination.exists():
                destination = target / f"{stem} ({counter}){suffix}"
                counter += 1
        shutil.move(str(item), str(destination))
        moved += 1
    return f"Moved {moved} file(s) into categorized folders."


def _sha256(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()


def find_duplicates(folder):
    folder = Path(folder)
    by_size = {}
    for base, dirs, files in os.walk(folder):
        for name in files:
            path = Path(base) / name
            try:
                size = path.stat().st_size
                by_size.setdefault(size, []).append(path)
            except OSError:
                pass

    groups = {}
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = {}
        for path in paths:
            try:
                by_hash.setdefault(_sha256(path), []).append(str(path))
            except OSError:
                pass
        for digest, same in by_hash.items():
            if len(same) > 1:
                groups[f"{size:,} bytes • {digest[:12]}"] = same
    return groups


def disk_overview():
    path = Path.home().anchor or os.path.abspath(os.sep)
    usage = shutil.disk_usage(path)
    return usage.total, usage.used, usage.free
