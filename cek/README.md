# Tool Pemeriksa Kode Berbasis Tree-sitter (`cek.py`)

Tool CLI analisis statis ringan untuk memeriksa basis kode Python (dan opsional JavaScript) menggunakan parser deterministik **Tree-sitter**.

---

## 1. Fitur Utama

1. **Deteksi Komentar `TODO` dan `FIXME`**:
   Mencari komentar yang memerlukan tindak lanjut developer beserta nomor baris spesifik menggunakan Tree-sitter S-expression query dan predikat `#match?`.
2. **Deteksi Fungsi Terlalu Panjang (> 30 Baris)**:
   Mendeteksi fungsi atau method yang berpotensi menjadi *code smell* (panjang body > 30 baris) berdasarkan selisih koordinat `start_point` dan `end_point`.
3. **Deteksi File dengan Error Sintaks (Parse Error)**:
   Mendeteksi file yang mengalami kerusakan sintaks (`root_node.has_error`) dan secara rekursif melacak koordinat baris/kolom kemunculan node `ERROR` atau `MISSING` pertama.
4. **[Pengayaan] Dukungan File JavaScript (`--include-js`)**:
   Mendukung pemindaian berkas JavaScript (`.js`) menggunakan grammar `tree-sitter-javascript`.

---

## 2. Cara Memasang Dependensi

Pastikan Python 3.10+ sudah terpasang. Pasang pustaka Tree-sitter melalui `pip`:

```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

Atau jika menggunakan virtual environment di root workspace:
```bash
source ../.venv/bin/activate
```

---

## 3. Cara Menjalankan

Jalankan perintah berikut pada terminal:

```bash
# Pengecekan standar pada folder tertentu
python cek.py <path/ke/folder>

# Contoh pengujian pada folder uji bawaan:
python cek.py uji/

# Pengecekan termasuk file JavaScript (opsional):
python cek.py <path/ke/folder> --include-js
```

---

## 4. Contoh Output Eksekusi

### A. Pengujian pada Folder Uji Lokal (`uji/`)

```text
======================================================================
MEMULAI PENGECEKAN KODE DENGAN TREE-SITTER
Target Direktori : /home/aryanata/kuliah/Programming Language Pragmatics/Praktik/W9/cek/uji
Dukungan JS      : Nonaktif (Python Only)
======================================================================
[TODO/FIXME] uji/file_todo.py:2: # TODO: Validasi skema input sebelum diproses
[TODO/FIXME] uji/file_todo.py:5: # FIXME: Ganti algoritma bubble sort dengan timsort jika data > 1000 item
[FUNGSI PANJANG] uji/file_panjang.py:5: Fungsi 'fungsi_sangat_panjang_proses_bisnis' terlalu panjang (45 baris > 30 baris)
[SYNTAX ERROR] uji/file_error.py:2:0: Pohon mengandung ERROR (teks: 'def hitung_nilai(a, b\n    c = a + b\n    return c')

======================================================================
RINGKASAN HASIL PENGECEKAN
======================================================================
Total file dipindai     : 3
Komentar TODO/FIXME     : 2
Fungsi > 30 baris       : 1
File dengan Parse Error : 1
======================================================================
```

### B. Pengujian pada Repositori Terbuka Nyata (`bottlepy/bottle`)

```text
======================================================================
MEMULAI PENGECEKAN KODE DENGAN TREE-SITTER
Target Direktori : /home/aryanata/kuliah/Programming Language Pragmatics/Praktik/W9/cek/repo_uji
Dukungan JS      : Nonaktif (Python Only)
======================================================================
[TODO/FIXME] repo_uji/bottle.py:1002: # TODO: Handle these explicitly in handle() or make them iterable.
[TODO/FIXME] repo_uji/bottle.py:2837: # HTTP Utilities and MISC (TODO) ###############################################
[TODO/FIXME] repo_uji/bottle.py:2004: #: Not a plugin, but part of the plugin API. TODO: Find a better place.
[FUNGSI PANJANG] repo_uji/bottle.py:329: Fungsi 'add' terlalu panjang (75 baris > 30 baris)
...
[TODO/FIXME] repo_uji/test/test_html_helper.py:8: # TODO: Move more of the low level http stuff here.
[FUNGSI PANJANG] repo_uji/test/test_sendfile.py:118: Fungsi 'test_etag' terlalu panjang (35 baris > 30 baris)
...
======================================================================
RINGKASAN HASIL PENGECEKAN
======================================================================
Total file dipindai     : 30
Komentar TODO/FIXME     : 4
Fungsi > 30 baris       : 22
File dengan Parse Error : 0
======================================================================
```

---

## 5. Verifikasi Manual (2 Berkas Acak)

Untuk memastikan akurasi dan ketiadaan *false positive*, dilakukan pencocokan manual pada 2 berkas acak di repositori `bottle`:

1. **Berkas 1: `repo_uji/test/test_html_helper.py`**
   - **Hasil Tool**: Melaporkan 1 `TODO` pada baris 8.
   - **Pemeriksaan Manual**:
     Baris 8 berisi teks `# TODO: Move more of the low level http stuff here.`.
     Fungsi satu-satunya di file tersebut (`test_accept_header`) hanya berukuran 13 baris ($\le 30$).
   - **Kesimpulan**: **Valid 100% (Akurat)**.

2. **Berkas 2: `repo_uji/test/test_sendfile.py`**
   - **Hasil Tool**: Melaporkan fungsi `test_etag` terlalu panjang pada baris 118 (35 baris).
   - **Pemeriksaan Manual**:
     Header `def test_etag(self):` berada pada baris 118 dan statement terakhirnya `self.assertEqual(200, res.status_code)` berada pada baris 152.
     Perhitungan: $152 - 118 + 1 = 35$ baris.
   - **Kesimpulan**: **Valid 100% (Akurat)**.
