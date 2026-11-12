"""
Modul Manajemen Pengguna dan Autentikasi Sederhana
Digunakan untuk pengujian tree-sitter AST traversal dan query matching.
"""

import os
import sys
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any

class Role:
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Pengguna:
    """Kelas representasi data pengguna sistem."""
    def __init__(self, username: str, email: str, role: str = Role.VIEWER):
        self.username = username
        self.email = email
        self.role = role
        self.is_active = True
        self.created_at = datetime.now()

    def ubah_role(self, role_baru: str) -> None:
        """Mengubah role pengguna jika valid."""
        daftar_role = [Role.ADMIN, Role.EDITOR, Role.VIEWER]
        if role_baru in daftar_role:
            self.role = role_baru
            print(f"Role pengguna {self.username} diubah menjadi {role_baru}")
        else:
            print(f"Error: Role {role_baru} tidak valid")

    def nonaktifkan(self) -> None:
        """Menonaktifkan akun pengguna."""
        self.is_active = False
        print(f"Akun {self.username} telah dinonaktifkan")

class SistemAutentikasi:
    """Sistem autentikasi dan penyimpanan pengguna dalam memori."""
    def __init__(self):
        self.database_pengguna: Dict[str, Pengguna] = {}
        self.hash_sandi: Dict[str, str] = {}

    def _hitung_hash(self, sandi: str) -> str:
        return hashlib.sha256(sandi.encode("utf-8")).hexdigest()

    def daftarkan_pengguna(self, username: str, email: str, sandi: str, role: str = Role.VIEWER) -> bool:
        """Mendaftarkan akun baru jika username belum terdaftar."""
        if username in self.database_pengguna:
            print(f"Peringatan: Username {username} sudah digunakan!")
            return False

        if len(sandi) < 6:
            print("Gagal: Kata sandi minimal harus 6 karakter")
            return False

        user = Pengguna(username, email, role)
        self.database_pengguna[username] = user
        self.hash_sandi[username] = self._hitung_hash(sandi)
        print(f"Sukses mendaftarkan pengguna: {username}")
        return True

    def login(self, username: str, sandi: str) -> Optional[Pengguna]:
        """Melakukan login dan verifikasi hash kata sandi."""
        if username not in self.database_pengguna:
            print("Login gagal: Pengguna tidak ditemukan")
            return None

        user = self.database_pengguna[username]
        if not user.is_active:
            print("Login gagal: Akun berstatus nonaktif")
            return None

        if self.hash_sandi[username] == self._hitung_hash(sandi):
            print(f"Login berhasil! Selamat datang {username}")
            return user
        else:
            print("Login gagal: Kata sandi salah")
            return None

    def list_pengguna_aktif(self) -> List[Pengguna]:
        hasil = []
        for username, user in self.database_pengguna.items():
            if user.is_active:
                hasil.append(user)
        return hasil

def fungsi_demo_utama():
    """Fungsi utama demonstrasi alur autentikasi."""
    auth = SistemAutentikasi()

    # Pendaftaran pengguna demo
    auth.daftarkan_pengguna("budi", "budi@perusahaan.co.id", "rahasia123", Role.ADMIN)
    auth.daftarkan_pengguna("siti", "siti@perusahaan.co.id", "sandiSiti", Role.EDITOR)
    auth.daftarkan_pengguna("andi", "andi@perusahaan.co.id", "12345", Role.VIEWER)

    # Percobaan login
    pengguna1 = auth.login("budi", "rahasia123")
    if pengguna1:
        pengguna1.ubah_role(Role.ADMIN)

    pengguna_salah = auth.login("budi", "sandisalah")
    print("Hasil login gagal:", pengguna_salah)

    daftar = auth.list_pengguna_aktif()
    print(f"Total pengguna aktif: {len(daftar)}")

if __name__ == "__main__":
    print("Menjalankan demo sistem autentikasi...")
    fungsi_demo_utama()
