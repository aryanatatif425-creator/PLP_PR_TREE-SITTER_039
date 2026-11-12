import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY = Language(tspython.language())
parser = Parser(PY)

def cetak_header(judul):
    print("=" * 60)
    print(judul)
    print("=" * 60)

# ==========================================
# 1. Tiga Potongan Kode Python & Perbandingan Prediksi vs Aktual
# ==========================================
snippets = [
    {
        "nama": "Potongan 1: Fungsi",
        "kode": b"def tambah(a, b):\n    return a + b\n",
        "prediksi": "(module (function_definition name: (identifier) parameters: (parameters (identifier) (identifier)) body: (block (return_statement (binary_operator left: (identifier) right: (identifier))))))",
    },
    {
        "nama": "Potongan 2: Kondisional (if/else)",
        "kode": b"if x > 0:\n    y = 1\nelse:\n    y = -1\n",
        "prediksi": "(module (if_statement condition: (comparison_operator left: (identifier) right: (integer)) consequence: (block (expression_statement (assignment left: (identifier) right: (integer)))) alternative: (else_clause (block (expression_statement (assignment left: (identifier) right: (unary_operator argument: (integer))))))))",
    },
    {
        "nama": "Potongan 3: Kelas dengan Satu Method",
        "kode": b"class Persegi:\n    def luas(self):\n        return self.sisi * self.sisi\n",
        "prediksi": "(module (class_definition name: (identifier) body: (block (function_definition name: (identifier) parameters: (parameters (identifier)) body: (block (return_statement (binary_operator left: (attribute object: (identifier) attribute: (identifier)) right: (attribute object: (identifier) attribute: (identifier)))))))))",
    }
]

cetak_header("TUGAS 1: PERBANDINGAN PREDIKSI VS AKTUAL")
for s in snippets:
    tree = parser.parse(s["kode"])
    aktual = str(tree.root_node)
    print(f"\n--- {s['nama']} ---")
    print("Kode Sumber:")
    print(s["kode"].decode().rstrip())
    print("\nPohon Prediksi:")
    print(s["prediksi"])
    print("\nPohon Aktual (tree.root_node):")
    print(aktual)
    print(f"Prediksi Sesuai Aktual? {'YA' if s['prediksi'] == aktual else 'BEDA SEDIKIT (Cek detail)'}")

# ==========================================
# 2. Node Bernama vs Node Anonim
# ==========================================
cetak_header("IDENTIFIKASI NODE BERNAMA VS NODE ANONIM")
kode_fungsi = b"def tambah(a, b):\n    return a + b\n"
tree_fn = parser.parse(kode_fungsi)
fn_node = tree_fn.root_node.children[0]

print("Kode: def tambah(a, b): return a + b\n")
print(f"Anak-anak langsung dari {fn_node.type} (menggunakan .children):")
anonim_nodes = []
for c in fn_node.children:
    status = "BERNAMA" if c.is_named else "ANONIM"
    print(f"  - Node: {repr(c.type):<15} [{status:<7}] teks: {repr(c.text.decode())}")
    if not c.is_named:
        anonim_nodes.append((c.type, c.text.decode()))

print("\nAnak-anak di dalam node 'parameters':")
for c in fn_node.child_by_field_name("parameters").children:
    status = "BERNAMA" if c.is_named else "ANONIM"
    print(f"  - Node: {repr(c.type):<15} [{status:<7}] teks: {repr(c.text.decode())}")
    if not c.is_named:
        anonim_nodes.append((c.type, c.text.decode()))

print("\nNode Anonim yang ditemukan (minimal 3):")
for t, teks in set(anonim_nodes):
    print(f"  * Token anonim: {repr(teks)} (tipe grammar: {repr(t)})")

# ==========================================
# 3. Error Recovery (ERROR / MISSING)
# ==========================================
cetak_header("PENGUJIAN ERROR RECOVERY (SINTAKS RUSAK)")

kode_rusak_1 = b"def tambah(a, b\n    return a + b\n"  # kurung tutup ')' hilang
tree_err_1 = parser.parse(kode_rusak_1)
print("Kasus 1: Tanda kurung tutup ')' hilang pada definisi fungsi:")
print(f"Kode: {repr(kode_rusak_1.decode())}")
print(f"Pohon: {tree_err_1.root_node}")
print(f"Memiliki error? {tree_err_1.root_node.has_error}")

kode_rusak_2 = b"def tambah(a, b)\n    return a + b\n"  # tanda titik dua ':' hilang
tree_err_2 = parser.parse(kode_rusak_2)
print("\nKasus 2: Tanda titik dua ':' hilang setelah header fungsi:")
print(f"Kode: {repr(kode_rusak_2.decode())}")
print(f"Pohon: {tree_err_2.root_node}")
print(f"Memiliki error? {tree_err_2.root_node.has_error}")

# ==========================================
# 4. Perbedaan `children` vs `named_children`
# ==========================================
cetak_header("PENJELASAN PERBEDAAN .children VS .named_children")
print(f"Node target: {fn_node.type} ({fn_node.text.decode().splitlines()[0]})")
print(f"Total .children       : {len(fn_node.children)} node -> {[c.type for c in fn_node.children]}")
print(f"Total .named_children : {len(fn_node.named_children)} node -> {[c.type for c in fn_node.named_children]}")
print("""
Penjelasan:
- `children` mencakup SELURUH token yang ada pada Concrete Syntax Tree (CST),
  termasuk node literal/anonim seperti 'def', ':', '(', ')', dan koma ','.
- `named_children` hanya menyaring node bernama (bermakna semantik/sintaksis tinggi)
  yang didefinisikan sebagai rule bernilai di grammar, seperti 'identifier',
  'parameters', dan 'block', serta menyembunyikan tanda baca/simbol pembatas.
""")
