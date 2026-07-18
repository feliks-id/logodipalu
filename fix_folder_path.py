#!/usr/bin/env python3
"""
fix_folder_path.py

Tujuan:
Mengganti semua referensi path folder LAMA -> BARU di file .html, .json, .css
di seluruh subfolder repo. Dipakai untuk kasus seperti:
  wp-content/uploads  ->  image
(folder upload WordPress dipindah ke root dan diganti nama)

Cara pakai:
  python fix_folder_path.py

Script akan minta konfirmasi path lama & baru, tampilkan preview jumlah
kecocokan di tiap file, lalu minta konfirmasi sebelum menulis perubahan.
"""

import sys
from pathlib import Path
import subprocess

TARGET_EXTENSIONS = {".html", ".htm", ".json", ".css"}

def get_repo_root():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path(".").resolve()

def find_target_files(repo_root):
    files = []
    for ext in TARGET_EXTENSIONS:
        files.extend(repo_root.rglob(f"*{ext}"))
    return [f for f in files if ".git" not in f.parts]

def replace_in_file(file_path, old_path, new_path):
    try:
        text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return 0

    total_hits = 0
    escaped_old = old_path.replace("/", r"\/")
    escaped_new = new_path.replace("/", r"\/")

    # 1) varian escaped JSON: wp-content\/uploads -> image
    n1 = text.count(escaped_old)
    if n1:
        text = text.replace(escaped_old, escaped_new)
        total_hits += n1

    # 2) varian normal (dengan leading slash dulu, baru tanpa)
    n2 = text.count("/" + old_path)
    if n2:
        text = text.replace("/" + old_path, "/" + new_path)
        total_hits += n2

    n3 = text.count(old_path)
    if n3:
        text = text.replace(old_path, new_path)
        total_hits += n3

    if total_hits > 0:
        file_path.write_text(text, encoding="utf-8")

    return total_hits

def main():
    repo_root = get_repo_root()
    print(f"Repo root: {repo_root}\n")

    old_path = input("Path folder LAMA (contoh: wp-content/uploads): ").strip().strip("/")
    new_path = input("Path folder BARU (contoh: image): ").strip().strip("/")

    if not old_path or not new_path:
        print("Path tidak boleh kosong.")
        sys.exit(1)

    target_files = find_target_files(repo_root)
    print(f"\nMemeriksa {len(target_files)} file (.html/.json/.css)...\n")

    escaped_old = old_path.replace("/", r"\/")
    any_found = False

    for f in target_files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        count = text.count(old_path) + text.count(escaped_old)
        if count > 0:
            any_found = True
            rel = f.relative_to(repo_root)
            print(f"  {rel}  ({count} kemunculan '{old_path}')")

    if not any_found:
        print(f"Tidak ada kemunculan '{old_path}' di file manapun.")
        sys.exit(0)

    confirm = input(f"\nGanti '{old_path}' -> '{new_path}' di file-file di atas? (y/n): ").strip().lower()
    if confirm != "y":
        print("Dibatalkan.")
        sys.exit(0)

    total_files_changed = 0
    total_replacements = 0

    for f in target_files:
        hits = replace_in_file(f, old_path, new_path)
        if hits > 0:
            rel = f.relative_to(repo_root)
            print(f"  \u2713 {rel}  ({hits} diganti)")
            total_files_changed += 1
            total_replacements += hits

    print(f"\nSelesai. {total_replacements} referensi diganti di {total_files_changed} file.")
    print("Cek hasilnya di GitHub Desktop / VS Code, lalu commit.")

if __name__ == "__main__":
    main()
