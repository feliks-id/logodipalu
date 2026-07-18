#!/usr/bin/env python3
"""
fix_image_references.py

Tujuan:
- Mendeteksi file gambar yang baru saja di-rename (via `git status`, BELUM di-commit)
- Mencari & mengganti semua referensi nama file lama -> nama file baru
  di dalam file .html, .json, dan .css di seluruh subfolder repo.

Cara pakai:
1. Pastikan kamu menjalankan script ini DARI DALAM folder repo Git kamu
   (folder yang sama dengan yang dibuka GitHub Desktop), dan JANGAN commit
   dulu perubahan rename-nya.
2. Jalankan:  python fix_image_references.py
3. Script akan menampilkan daftar rename yang terdeteksi, lalu minta
   konfirmasi sebelum benar-benar mengubah file.
4. Setelah selesai, cek hasilnya, baru commit semuanya di GitHub Desktop.

Catatan:
- Script ini hanya mengubah *referensi nama file* di dalam teks file
  (href, src, url(), key JSON, dll), bukan memindah/rename file itu sendiri
  (karena itu sudah kamu lakukan manual di GitHub Desktop).
- Pencarian bersifat "whole word" pada nama file (bukan substring sembarang),
  supaya tidak salah timpa nama file lain yang mirip.
"""

import subprocess
import re
import sys
from pathlib import Path

TARGET_EXTENSIONS = {".html", ".htm", ".json", ".css"}

def run_git_command(args, cwd="."):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error menjalankan git {' '.join(args)}: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Git tidak ditemukan. Pastikan git terinstall dan ada di PATH.")
        sys.exit(1)

def get_repo_root():
    out = run_git_command(["rev-parse", "--show-toplevel"])
    return Path(out.strip())

def detect_renames(repo_root):
    """
    Git tidak memasangkan file 'deleted' (belum di-stage) dengan file
    'untracked' sebagai rename -- dua kategori itu memang tidak saling
    dibandingkan oleh `git status`. Rename baru terdeteksi kalau
    perubahan sudah di-stage (dibandingkan terhadap HEAD).

    Jadi: stage semua perubahan dulu (git add -A), lalu baca rename dari
    `git diff --staged --find-renames --name-status -z`.
    """
    # Stage semua perubahan (aman, ini BUKAN commit)
    subprocess.run(["git", "add", "-A"], cwd=repo_root, capture_output=True, text=True)

    raw = subprocess.run(
        ["git", "diff", "--staged", "--find-renames=40%", "--name-status", "-z", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    ).stdout

    entries = [e for e in raw.split("\0") if e]
    renames = []
    i = 0
    while i < len(entries):
        status = entries[i]
        if status.startswith("R"):
            old_path = entries[i + 1]
            new_path = entries[i + 2]
            renames.append((old_path, new_path))
            i += 3
        else:
            i += 2  # status + 1 path (added/modified/deleted biasa)

    return renames

def is_image_file(path_str):
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"}
    return Path(path_str).suffix.lower() in image_exts

def find_target_files(repo_root):
    files = []
    for ext in TARGET_EXTENSIONS:
        files.extend(repo_root.rglob(f"*{ext}"))
    # Skip folder .git
    return [f for f in files if ".git" not in f.parts]

def build_replacements(renames):
    """
    Untuk tiap rename, siapkan beberapa varian nama (basename saja,
    dan path relatif) supaya replace bisa kena berbagai gaya penulisan
    referensi (misal 'img/foto.png' atau cuma 'foto.png').
    """
    replacements = []
    for old_path, new_path in renames:
        if not is_image_file(old_path):
            continue
        old_name = Path(old_path).name
        new_name = Path(new_path).name
        if old_name == new_name:
            continue  # nama file sama, mungkin cuma pindah folder
        replacements.append((old_name, new_name))
    return replacements

def replace_in_file(file_path, replacements):
    try:
        text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return 0

    original_text = text
    total_hits = 0

    for old_name, new_name in replacements:
        # whole-word match: nama file diapit oleh karakter non-alfanumerik
        # (kutip, slash, kurung, dsb) atau awal/akhir string
        pattern = re.compile(
            r'(?<![A-Za-z0-9_])' + re.escape(old_name) + r'(?![A-Za-z0-9_])'
        )
        text, n = pattern.subn(new_name, text)
        total_hits += n

    if total_hits > 0:
        file_path.write_text(text, encoding="utf-8")

    return total_hits

def main():
    repo_root = get_repo_root()
    print(f"Repo root: {repo_root}\n")

    renames = detect_renames(repo_root)
    if not renames:
        print("Tidak ada rename terdeteksi (sudah dicoba dengan auto-staging).")
        print("Kemungkinan: isi file gambar berubah sedikit saat rename (misal ke-resize/re-export ulang),")
        print("sehingga Git menganggapnya file baru, bukan rename dari file lama.")
        sys.exit(0)

    replacements = build_replacements(renames)
    if not replacements:
        print("Rename terdeteksi tapi tidak ada yang relevan (bukan file gambar, atau nama sama).")
        sys.exit(0)

    print("Rename gambar terdeteksi:")
    for old_name, new_name in replacements:
        print(f"  {old_name}  ->  {new_name}")

    confirm = input("\nLanjutkan cari-ganti referensi di HTML/JSON/CSS? (y/n): ").strip().lower()
    if confirm != "y":
        print("Dibatalkan.")
        sys.exit(0)

    target_files = find_target_files(repo_root)
    print(f"\nMemeriksa {len(target_files)} file (.html/.json/.css)...\n")

    total_files_changed = 0
    total_replacements = 0

    for f in target_files:
        hits = replace_in_file(f, replacements)
        if hits > 0:
            rel = f.relative_to(repo_root)
            print(f"  ✓ {rel}  ({hits} referensi diganti)")
            total_files_changed += 1
            total_replacements += hits

    print(f"\nSelesai. {total_replacements} referensi diganti di {total_files_changed} file.")
    print("Silakan cek hasilnya di GitHub Desktop, lalu commit semuanya jadi satu commit.")

if __name__ == "__main__":
    main()
