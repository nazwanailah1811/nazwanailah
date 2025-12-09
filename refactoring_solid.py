from abc import ABC, abstractmethod

# Implementasi DIP/OCP: Abstraksi dan Kelas Konkrit

class IValidationRule(ABC):
    """Abstraksi (Kontrak) untuk semua aturan validasi. (DIP)"""
    @abstractmethod
    def validate(self, data: dict) -> bool:
        """
        Melakukan validasi. Mengembalikan True jika valid, False jika tidak.
        'data' adalah dictionary yang berisi data registrasi mahasiswa.
        """
        pass

class SksLimitRule(IValidationRule):
    """Aturan konkrit untuk memvalidasi batas SKS. (OCP)"""
    def validate(self, data: dict) -> bool:
        mahasiswa = data.get("mahasiswa", {})
        kursus_terpilih = data.get("kursus_terpilih", [])
        
        sks_terpilih = sum(k['sks'] for k in kursus_terpilih)
        batas_sks = mahasiswa.get("max_sks", 24)
        
        if sks_terpilih > batas_sks:
            print(f"❌ GAGAL VALIDASI SKS: Total SKS {sks_terpilih} melebihi batas {batas_sks}.")
            return False
        
        print("✅ Lolos Validasi SKS.")
        return True

class PrerequisiteRule(IValidationRule):
    """Aturan konkrit untuk memvalidasi prasyarat kursus. (OCP)"""
    def validate(self, data: dict) -> bool:
        mahasiswa = data.get("mahasiswa", {})
        kursus_terpilih = data.get("kursus_terpilih", [])
        
        riwayat_lulus = set(mahasiswa.get("riwayat_kursus", []))
        
        for kursus in kursus_terpilih:
            prasyarat = kursus.get("prasyarat")
            if prasyarat and prasyarat not in riwayat_lulus:
                print(f"❌ GAGAL VALIDASI PRASYARAT: Kursus '{kursus['nama']}' memerlukan '{prasyarat}' yang belum lulus.")
                return False

        print("✅ Lolos Validasi Prasyarat.")
        return True
# Implementasi SRP: Kelas Koordinator (RegistrationService) 

class RegistrationService:
    """
    Bertanggung jawab tunggal untuk mengkoordinasikan eksekusi validasi. (SRP)
    Menerima aturan via Dependency Injection.
    """
    def __init__(self, validation_rules: list[IValidationRule]):
        # Dependency Injection (DIP): Menerima daftar abstraksi (IValidationRule)
        self.rules = validation_rules

    def register_student(self, data: dict) -> bool:
        """Menjalankan semua aturan validasi yang ada."""
        print(f"\n--- Memulai Validasi Registrasi untuk {data['mahasiswa']['nama']} ---")
        
        for rule in self.rules:
            # Polymorphism: Memanggil validate() pada objek apapun yang
            # mengimplementasikan IValidationRule
            if not rule.validate(data):
                print(f"⚠️ REGISTRASI GAGAL karena aturan {rule.__class__.__name__} tidak terpenuhi.")
                return False
        
        print("🎉 REGISTRASI BERHASIL: Semua aturan validasi terpenuhi.")
        return True
# Challenge: Pembuktian OCP (JadwalBentrokRule)

class JadwalBentrokRule(IValidationRule):
    """
    Aturan baru ditambahkan tanpa memodifikasi RegistrationService. (OCP)
    """
    def validate(self, data: dict) -> bool:
        kursus_terpilih = data.get("kursus_terpilih", [])
        
        jadwal = set()
        for kursus in kursus_terpilih:
            waktu = kursus.get("jadwal")
            if waktu in jadwal:
                print(f"❌ GAGAL VALIDASI JADWAL: Jadwal {waktu} bentrok.")
                return False
            jadwal.add(waktu)

        print("✅ Lolos Validasi Jadwal Bentrok.")
        return True
        
# PROGRAM UTAMA & DEMONSTRASI

# Data Contoh
data_mahasiswa_valid = {
    "mahasiswa": {"nama": "Budi", "max_sks": 24, "riwayat_kursus": ["DASPRO", "ALGORITMA"]},
    "kursus_terpilih": [
        {"nama": "STRUKTUR DATA", "sks": 4, "prasyarat": "ALGORITMA", "jadwal": "SENIN 10:00"},
        {"nama": "JARINGAN KOMPUTER", "sks": 4, "prasyarat": None, "jadwal": "SELASA 08:00"}
    ]
}

# 1. Skenario Sukses (Semua Lolos)
aturan_lengkap = [
    SksLimitRule(),
    PrerequisiteRule(),
    JadwalBentrokRule() # Rule baru disuntikkan di sini (OCP)
]

registration_service = RegistrationService(aturan_lengkap)
registration_service.register_student(data_mahasiswa_valid)

# Skenario Gagal (Batas SKS)
data_mahasiswa_gagal_sks = {
    "mahasiswa": {"nama": "Andi", "max_sks": 8, "riwayat_kursus": ["DASPRO", "ALGORITMA"]},
    "kursus_terpilih": [
        {"nama": "STRUKTUR DATA", "sks": 4, "prasyarat": "ALGORITMA", "jadwal": "SENIN 10:00"},
        {"nama": "JARINGAN KOMPUTER", "sks": 4, "prasyarat": None, "jadwal": "SELASA 08:00"},
        {"nama": "BASIS DATA", "sks": 4, "prasyarat": None, "jadwal": "RABU 13:00"} # Total 12 SKS
    ]
}

registration_service.register_student(data_mahasiswa_gagal_sks)