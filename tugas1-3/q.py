import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

def jalankan_query_biasa(file_kode, file_query):
    kode = Path(file_kode).read_bytes()
    pola = Path(file_query).read_text(encoding="utf-8")
    tree = parser.parse(kode)

    query = Query(PY, pola)
    cursor = QueryCursor(query)

    print(f"=== Menjalankan Query: {file_query} pada {file_kode} ===")
    matches = cursor.matches(tree.root_node)

    if not matches:
        # Coba captures jika matches tidak mengembalikan hasil
        captures = cursor.captures(tree.root_node)
        for nama, nodes in captures.items():
            for n in nodes:
                print(f"@{nama:<10} [baris {n.start_point[0] + 1}:{n.start_point[1]}] -> {n.text.decode().strip()}")
        return

    for pattern_idx, cap in matches:
        info = []
        for k, nodes in cap.items():
            val = ", ".join(n.text.decode().strip() for n in nodes)
            line = nodes[0].start_point[0] + 1
            info.append(f"@{k}(baris {line})={val}")
        print(" | ".join(info))

def uji_lengkap(file_kode):
    kode = Path(file_kode).read_bytes()
    tree = parser.parse(kode)
    root = tree.root_node

    print("=" * 70)
    print("TUGAS 3: UJI LENGKAP QUERY PADA FILE UJI")
    print(f"Target: {file_kode}")
    print("=" * 70)

    # 1. Nama fungsi dan jumlah parameter
    print("\n--- 1. Fungsi dan Jumlah Parameternya ---")
    q_fn = Query(PY, Path("query_fungsi.scm").read_text(encoding="utf-8"))
    fungsi_ditemukan = []
    for _, cap in QueryCursor(q_fn).matches(root):
        nama = cap["nama"][0].text.decode()
        baris = cap["nama"][0].start_point[0] + 1
        param_node = cap["params"][0]
        # Hitung named children di dalam parameters (mengecualikan '(', ')', dan koma)
        jumlah_param = param_node.named_child_count
        param_list = [c.text.decode() for c in param_node.named_children]
        fungsi_ditemukan.append((nama, baris, jumlah_param, param_list))
        print(f"  * Fungsi `{nama}` (baris {baris:2d}) -> {jumlah_param} parameter: {param_list}")

    print(f"Total fungsi terdeteksi: {len(fungsi_ditemukan)}")

    # 2. Pemanggilan print(...)
    print("\n--- 2. Pemanggilan print(...) ---")
    q_print = Query(PY, Path("query_print.scm").read_text(encoding="utf-8"))
    print_ditemukan = []
    for _, cap in QueryCursor(q_print).matches(root):
        fn_node = cap["fn"][0]
        args_node = cap["args"][0]
        baris = fn_node.start_point[0] + 1
        teks_args = args_node.text.decode().replace("\n", " ").strip()
        print_ditemukan.append((baris, teks_args))
        print(f"  * Baris {baris:3d}: print{teks_args}")

    print(f"Total pemanggilan print(): {len(print_ditemukan)}")

    # 3. Semua import dan from ... import ...
    print("\n--- 3. Modul yang di-import (import & from ... import) ---")
    q_import = Query(PY, Path("query_import.scm").read_text(encoding="utf-8"))
    import_ditemukan = []
    for _, cap in QueryCursor(q_import).matches(root):
        for modul_node in cap.get("modul", []):
            baris = modul_node.start_point[0] + 1
            nama_modul = modul_node.text.decode()
            import_ditemukan.append((baris, nama_modul))
            print(f"  * Baris {baris:2d}: modul `{nama_modul}`")

    print(f"Total import modul: {len(import_ditemukan)}")

    # 4. [Pengayaan] Docstring fungsi
    print("\n--- 4. [Pengayaan] Docstring Baris Pertama Body Fungsi ---")
    q_doc = Query(PY, Path("query_docstring.scm").read_text(encoding="utf-8"))
    doc_ditemukan = []
    for _, cap in QueryCursor(q_doc).matches(root):
        fn_name = cap["nama"][0].text.decode()
        doc_node = cap["doc"][0]
        baris = doc_node.start_point[0] + 1
        teks_doc = doc_node.text.decode().strip()
        doc_ditemukan.append((fn_name, baris, teks_doc))
        print(f"  * Fungsi `{fn_name}` (baris {baris}): {teks_doc}")

    print(f"Total docstring fungsi ditemukan: {len(doc_ditemukan)}")

    # Verifikasi Manual
    print("\n" + "=" * 70)
    print("VERIFIKASI HASIL QUERY VS HITUNGAN MANUAL")
    print("=" * 70)
    print(f"1. Fungsi & Parameter : Query = {len(fungsi_ditemukan):2d} | Manual =  9 -> {'COCOK (PASS)' if len(fungsi_ditemukan) == 9 else 'TIDAK COCOK'}")
    print(f"2. Pemanggilan print  : Query = {len(print_ditemukan):2d} | Manual = 13 -> {'COCOK (PASS)' if len(print_ditemukan) == 13 else 'TIDAK COCOK'}")
    print(f"3. Import Modul       : Query = {len(import_ditemukan):2d} | Manual =  5 -> {'COCOK (PASS)' if len(import_ditemukan) == 5 else 'TIDAK COCOK'}")
    print(f"4. Docstring Fungsi   : Query = {len(doc_ditemukan):2d} | Manual =  5 -> {'COCOK (PASS)' if len(doc_ditemukan) == 5 else 'TIDAK COCOK'}")

def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--uji-lengkap":
        uji_lengkap(sys.argv[2])
    elif len(sys.argv) == 3:
        jalankan_query_biasa(sys.argv[1], sys.argv[2])
    else:
        print("Penggunaan:")
        print("  python q.py <file_kode.py> <query.scm>")
        print("  python q.py --uji-lengkap <file_kode.py>")

if __name__ == "__main__":
    main()
