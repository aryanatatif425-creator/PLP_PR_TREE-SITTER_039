def proses_data(data):
    # TODO: Validasi skema input sebelum diproses
    if not data:
        return None
    # FIXME: Ganti algoritma bubble sort dengan timsort jika data > 1000 item
    data_terurut = sorted(data)
    # Catatan biasa: tidak boleh terdeteksi oleh linter
    return data_terurut
