def fungsi_pendek(x, y):
    # Fungsi ini hanya 4 baris
    return x + y

def fungsi_sangat_panjang_proses_bisnis(transaksi, konfigurasi):
    """
    Fungsi ini sengaja dibuat panjang (> 30 baris)
    untuk menguji deteksi code smell / refactoring linter.
    """
    hasil = {}
    total_nominal = 0
    pajak = 0.11

    # Langkah 1: Pengecekan status
    if not transaksi.get("aktif", False):
        return {"status": "gagal", "alasan": "transaksi nonaktif"}

    # Langkah 2: Iterasi item transaksi
    for item in transaksi.get("items", []):
        nama_item = item.get("nama")
        harga = item.get("harga", 0)
        qty = item.get("qty", 1)

        subtotal = harga * qty
        if subtotal < 0:
            continue

        if konfigurasi.get("diskon_khusus"):
            subtotal *= 0.9

        total_nominal += subtotal
        hasil[nama_item] = subtotal

    # Langkah 3: Perhitungan pajak dan biaya admin
    total_pajak = total_nominal * pajak
    biaya_admin = 2500
    grand_total = total_nominal + total_pajak + biaya_admin

    # Langkah 4: Penyusunan metadata response
    response_data = {
        "detail_item": hasil,
        "subtotal": total_nominal,
        "pajak": total_pajak,
        "biaya_admin": biaya_admin,
        "grand_total": grand_total,
        "status": "sukses",
    }

    return response_data
