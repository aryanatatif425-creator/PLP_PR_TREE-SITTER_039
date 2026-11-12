"""
filter_to_sql.py - [Pengayaan Tugas 4]
Menerjemahkan AST filter DSL menjadi parameterized SQL WHERE clause (dengan placeholder ?).
Mencegah kerentanan SQL Injection karena nilai dipisahkan ke dalam tuple parameter.
"""

import sys
import ctypes
from pathlib import Path
from tree_sitter import Language, Parser

# Muat dynamic library parser filter yang telah dikompilasi
SO_PATH = Path(__file__).parent / "filter.so"
lib = ctypes.cdll.LoadLibrary(str(SO_PATH))
lib.tree_sitter_filter.restype = ctypes.c_void_p
FILTER_LANG = Language(lib.tree_sitter_filter())
parser = Parser(FILTER_LANG)

def parse_literal(node):
    teks = node.text.decode("utf-8")
    if node.type == "string":
        # Hilangkan tanda kutip ganda pembungkus
        return teks[1:-1]
    elif node.type == "number":
        return float(teks) if "." in teks else int(teks)
    elif node.type == "boolean":
        return teks == "true"
    return teks

def to_sql(node, params):
    t = node.type

    if t == "query":
        return to_sql(node.children[0], params)

    elif t == "comparison":
        field_node = node.child_by_field_name("field")
        val_node = node.child_by_field_name("value")
        
        # Cari operator dari anak anonim
        op_teks = "="
        for c in node.children:
            if not c.is_named and c.text.decode() in ("=", "!=", ">", "<", ">=", "<="):
                op_teks = c.text.decode()
                break

        params.append(parse_literal(val_node))
        return f"{field_node.text.decode()} {op_teks} ?"

    elif t == "in_expression":
        field_node = node.child_by_field_name("field")
        # Nilai adalah semua named children setelah field
        val_nodes = [c for c in node.named_children if c != field_node]
        placeholders = []
        for vn in val_nodes:
            params.append(parse_literal(vn))
            placeholders.append("?")
        return f"{field_node.text.decode()} IN ({', '.join(placeholders)})"

    elif t == "contains_expression":
        field_node = node.child_by_field_name("field")
        val_node = node.child_by_field_name("value")
        val = parse_literal(val_node)
        params.append(f"%{val}%")
        return f"{field_node.text.decode()} LIKE ?"

    elif t == "and_expression":
        left = to_sql(node.child_by_field_name("left"), params)
        right = to_sql(node.child_by_field_name("right"), params)
        return f"({left} AND {right})"

    elif t == "or_expression":
        left = to_sql(node.child_by_field_name("left"), params)
        right = to_sql(node.child_by_field_name("right"), params)
        return f"({left} OR {right})"

    elif t == "not_expression":
        operand = to_sql(node.child_by_field_name("operand"), params)
        return f"NOT ({operand})"

    elif t == "parenthesized":
        # Ambil named child di dalam kurung
        return f"({to_sql(node.named_children[0], params)})"

    raise ValueError(f"Tipe node tidak dikenali: {t}")

def compile_filter(filter_str: str):
    tree = parser.parse(filter_str.encode("utf-8"))
    if tree.root_node.has_error:
        raise SyntaxError("Filter expression mengandung sintaks tidak valid!")
    params = []
    sql_where = to_sql(tree.root_node, params)
    return sql_where, params

def demo():
    sampel = [
        'status = "open"',
        'priority >= 2 and (owner = "budi" or department = "IT")',
        'not archived = true',
        'status in ("open", "pending", "in_review")',
        'title contains "invoice" and amount > 5000.0',
    ]

    print("=" * 70)
    print("DEMO [PENGAYAAN]: FILTER DSL -> PARAMETERIZED SQL WHERE CLAUSE")
    print("=" * 70)
    for s in sampel:
        sql, p = compile_filter(s)
        print(f"\n[DSL]   : {s}")
        print(f"[SQL]   : WHERE {sql}")
        print(f"[PARAMS]: {p}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dsl = " ".join(sys.argv[1:])
        sql, p = compile_filter(dsl)
        print(f"WHERE {sql}")
        print(f"Parameters: {p}")
    else:
        demo()
