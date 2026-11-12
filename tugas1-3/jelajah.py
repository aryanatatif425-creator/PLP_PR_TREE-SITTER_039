import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

def jelajah_rekursif(node, kedalaman=0, field=None):
    baris, kolom = node.start_point
    label = f"{field}: " if field else ""
    print("  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]")

    # Telusuri semua children dengan enumerate untuk menjaga indeks sebenarnya
    for i, child in enumerate(node.children):
        if not child.is_named:
            continue
        child_field = node.field_name_for_child(i)
        jelajah_rekursif(child, kedalaman + 1, child_field)

def jelajah_cursor(tree):
    """
    Implementasi Pengayaan menggunakan TreeCursor.
    Menelusuri pohon secara iteratif/DFS tanpa alokasi rekursif Node baru.
    """
    cursor = tree.walk()
    kedalaman = 0

    def kunjungi():
        nonlocal kedalaman
        node = cursor.node
        if node.is_named:
            baris, kolom = node.start_point
            field = cursor.field_name
            label = f"{field}: " if field else ""
            print("  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]")

        if cursor.goto_first_child():
            if node.is_named:
                kedalaman += 1
            kunjungi()
            while cursor.goto_next_sibling():
                kunjungi()
            cursor.goto_parent()
            if node.is_named:
                kedalaman -= 1

    kunjungi()

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python jelajah.py <file.py> [--mode=rekursif|cursor|banding]")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = "rekursif"
    if len(sys.argv) >= 3 and sys.argv[2].startswith("--mode="):
        mode = sys.argv[2].split("=")[1]

    with open(file_path, "rb") as f:
        src = f.read()

    tree = parser.parse(src)

    if mode == "rekursif":
        jelajah_rekursif(tree.root_node)
    elif mode == "cursor":
        jelajah_cursor(tree)
    elif mode == "banding":
        import io
        buf_rekursif = io.StringIO()
        buf_cursor = io.StringIO()

        sys_stdout = sys.stdout

        sys.stdout = buf_rekursif
        jelajah_rekursif(tree.root_node)

        sys.stdout = buf_cursor
        jelajah_cursor(tree)

        sys.stdout = sys_stdout

        out_rek = buf_rekursif.getvalue()
        out_cur = buf_cursor.getvalue()

        if out_rek == out_cur:
            print(f"VERIFIKASI SUKSES: Output traversal rekursif dan TreeCursor IDENTIK ({len(out_rek.splitlines())} baris node).")
        else:
            print("VERIFIKASI GAGAL: Terdapat perbedaan output antara rekursif dan TreeCursor.")
    else:
        jelajah_rekursif(tree.root_node)

if __name__ == "__main__":
    main()
