#!/usr/bin/env python3
"""
cek.py - CLI Code Checker Berbasis Tree-sitter
Tugas 6: Mini Proyek Pemeriksa Kualitas & Sintaks Kode

Fitur:
1. Mendeteksi komentar TODO dan FIXME beserta nomor barisnya (Query + #match?).
2. Mendeteksi fungsi yang panjangnya lebih dari 30 baris (start_point & end_point).
3. Mendeteksi file yang pohon sintaksnya mengandung error dan mencari baris error pertama.
4. [Pengayaan] Mendukung pemeriksaan file JavaScript (.js) menggunakan tree-sitter-javascript.
"""

import sys
import argparse
from pathlib import Path
from tree_sitter import Language, Parser, Query, QueryCursor

# Setup Tree-sitter Python
import tree_sitter_python as tspython
PY_LANG = Language(tspython.language())
parser_py = Parser(PY_LANG)

Q_TODO_PY = Query(PY_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FN_PY = Query(PY_LANG, '(function_definition name: (identifier) @nama) @fungsi')

# Setup Tree-sitter JavaScript (Pengayaan)
try:
    import tree_sitter_javascript as tsjs
    JS_LANG = Language(tsjs.language())
    parser_js = Parser(JS_LANG)
    Q_TODO_JS = Query(JS_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
    Q_FN_JS = Query(JS_LANG, '[ (function_declaration name: (identifier) @nama) (method_definition name: (property_identifier) @nama) (function_expression name: (identifier)? @nama) (arrow_function) ] @fungsi')
    HAS_JS = True
except Exception:
    HAS_JS = False

IGNORE_DIRS = {".venv", "venv", ".git", "node_modules", "__pycache__", "build", "dist", ".gemini"}

def cari_error_pertama(node):
    """Mencari node ERROR atau MISSING pertama secara rekursif (DFS preorder)."""
    if node.is_error or node.is_missing:
        return node
    for child in node.children:
        found = cari_error_pertama(child)
        if found:
            return found
    return None

def cek_file_python(path: Path, stats: dict):
    try:
        raw_bytes = path.read_bytes()
    except Exception as e:
        print(f"[ERROR BACA] {path}: {e}")
        return

    tree = parser_py.parse(raw_bytes)
    stats["total_files"] += 1

    # Fitur 1: Komentar TODO / FIXME
    for node in QueryCursor(Q_TODO_PY).captures(tree.root_node).get("c", []):
        line = node.start_point[0] + 1
        teks = node.text.decode(errors="replace").strip()
        stats["total_todo"] += 1
        print(f"[TODO/FIXME] {path}:{line}: {teks}")

    # Fitur 2: Fungsi lebih dari 30 baris
    for _, cap in QueryCursor(Q_FN_PY).matches(tree.root_node):
        fungsi_node = cap["fungsi"][0]
        start_row = fungsi_node.start_point[0]
        end_row = fungsi_node.end_point[0]
        panjang_baris = end_row - start_row + 1

        if panjang_baris > 30:
            nama = cap["nama"][0].text.decode(errors="replace") if "nama" in cap else "<anonim>"
            line = start_row + 1
            stats["total_fungsi_panjang"] += 1
            print(f"[FUNGSI PANJANG] {path}:{line}: Fungsi '{nama}' terlalu panjang ({panjang_baris} baris > 30 baris)")

    # Fitur 3: Syntax Error / Missing node
    if tree.root_node.has_error:
        stats["total_syntax_error"] += 1
        err_node = cari_error_pertama(tree.root_node)
        if err_node:
            err_line = err_node.start_point[0] + 1
            err_col = err_node.start_point[1]
            status = "MISSING" if err_node.is_missing else "ERROR"
            print(f"[SYNTAX ERROR] {path}:{err_line}:{err_col}: Pohon mengandung {status} (teks: {repr(err_node.text.decode(errors='replace'))})")
        else:
            print(f"[SYNTAX ERROR] {path}: Pohon terindikasi has_error=True")

def cek_file_javascript(path: Path, stats: dict):
    if not HAS_JS:
        return
    try:
        raw_bytes = path.read_bytes()
    except Exception as e:
        print(f"[ERROR BACA] {path}: {e}")
        return

    tree = parser_js.parse(raw_bytes)
    stats["total_files"] += 1

    # Fitur 1: Komentar TODO / FIXME
    for node in QueryCursor(Q_TODO_JS).captures(tree.root_node).get("c", []):
        line = node.start_point[0] + 1
        teks = node.text.decode(errors="replace").strip()
        stats["total_todo"] += 1
        print(f"[TODO/FIXME-JS] {path}:{line}: {teks}")

    # Fitur 2: Fungsi lebih dari 30 baris
    for _, cap in QueryCursor(Q_FN_JS).matches(tree.root_node):
        fungsi_node = cap["fungsi"][0]
        start_row = fungsi_node.start_point[0]
        end_row = fungsi_node.end_point[0]
        panjang_baris = end_row - start_row + 1

        if panjang_baris > 30:
            nama = cap["nama"][0].text.decode(errors="replace") if "nama" in cap else "<anonim>"
            line = start_row + 1
            stats["total_fungsi_panjang"] += 1
            print(f"[FUNGSI PANJANG-JS] {path}:{line}: Fungsi '{nama}' terlalu panjang ({panjang_baris} baris > 30 baris)")

    # Fitur 3: Syntax Error
    if tree.root_node.has_error:
        stats["total_syntax_error"] += 1
        err_node = cari_error_pertama(tree.root_node)
        if err_node:
            err_line = err_node.start_point[0] + 1
            print(f"[SYNTAX ERROR-JS] {path}:{err_line}: Pohon mengandung {err_node.type}")

def main():
    parser_cli = argparse.ArgumentParser(description="Pemeriksa Kode Python/JS berbasis Tree-sitter")
    parser_cli.add_argument("folder", help="Folder basis kode yang akan diperiksa")
    parser_cli.add_argument("--include-js", action="store_true", help="Sertakan pemeriksaan file JavaScript (.js)")
    args = parser_cli.parse_args()

    target_dir = Path(args.folder)
    if not target_dir.exists():
        print(f"Error: Folder '{args.folder}' tidak ditemukan.")
        sys.exit(1)

    print("=" * 70)
    print(f"MEMULAI PENGECEKAN KODE DENGAN TREE-SITTER")
    print(f"Target Direktori : {target_dir.resolve()}")
    print(f"Dukungan JS      : {'Aktif' if (args.include_js and HAS_JS) else 'Nonaktif (Python Only)'}")
    print("=" * 70)

    stats = {
        "total_files": 0,
        "total_todo": 0,
        "total_fungsi_panjang": 0,
        "total_syntax_error": 0,
    }

    # Kumpulkan file Python
    for file_path in target_dir.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue
        cek_file_python(file_path, stats)

    # Kumpulkan file JavaScript jika diminta
    if args.include_js and HAS_JS:
        for file_path in target_dir.rglob("*.js"):
            if any(part in IGNORE_DIRS for part in file_path.parts):
                continue
            cek_file_javascript(file_path, stats)

    print("\n" + "=" * 70)
    print("RINGKASAN HASIL PENGECEKAN")
    print("=" * 70)
    print(f"Total file dipindai     : {stats['total_files']}")
    print(f"Komentar TODO/FIXME     : {stats['total_todo']}")
    print(f"Fungsi > 30 baris       : {stats['total_fungsi_panjang']}")
    print(f"File dengan Parse Error : {stats['total_syntax_error']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
