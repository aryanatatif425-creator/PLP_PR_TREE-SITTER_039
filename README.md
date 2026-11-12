# Praktikum W9: Tree-sitter

Mata Kuliah: **Programming Language Pragmatics**
Praktik: **W9 - Part 1: Tree-sitter**

## Deskripsi Proyek

Proyek ini berisi tugas-tugas praktikum yang berfokus pada penggunaan **Tree-sitter** sebagai parser *Concrete Syntax Tree* (CST) inkremental deterministik. Seluruh tugas (Tugas 1–6) beserta pengayaannya telah diselesaikan dengan struktur repositori standar:

- **Tugas 1–3** (`tugas1-3/`): Membaca pohon sintaks, penjelajah node rekursif & TreeCursor, serta query pertama.
- **Tugas 4–5** (`tree-sitter-filter/`): Grammar DSL filter untuk halaman admin *enterprise web* beserta syntax highlighting.
- **Tugas 6** (`cek/`): Mini proyek linter CLI (`cek.py`) untuk pendeteksi TODO/FIXME, fungsi panjang, dan error sintaks.

## Struktur Folder

```
tugas1-3/           # Tugas 1–3: skrip Python, query .scm, dan output .txt
tree-sitter-filter/ # Tugas 4–5: grammar DSL filter, parser, highlight, dan test corpus
cek/                # Tugas 6: CLI checker (cek.py), README, dan folder uji
laporan.pdf         # Laporan praktikum (maks. 3 halaman)
proposal-draf.pdf   # Draf proposal proyek (maks. 1 halaman)
```

## Identitas

- **Nama**: Arya Nata Adidjaya
- **NIM**: 251524039

## Cara Menjalankan

### Tugas 1–3
```bash
cd tugas1-3
python3 t1.py
python3 jelajah.py uji_100_baris.py
python3 q.py --uji-lengkap uji_100_baris.py
```

### Tugas 4–5
```bash
cd tree-sitter-filter
tree-sitter generate
tree-sitter test
tree-sitter highlight contoh.filter
```

### Tugas 6
```bash
cd cek
python3 cek.py uji/
```

## Teknologi

- Python 3.10+
- Tree-sitter CLI & Python binding (`tree-sitter`, `tree-sitter-python`, `tree-sitter-javascript`)
- Grammar DSL kustom (Tree-sitter grammar)
