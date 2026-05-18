
```markdown
# Tenda TES-7002 OLT Automation

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Otomatisasi operasional ONT pada OLT GPON Tenda TES-7002 / TES-7001 melalui antarmuka web.  
Program ini dapat **menghapus (delete)** dan **menambah (add)** konfigurasi Gemport pada ONT tertentu secara otomatis.

---

## Daftar Isi
- [Fitur](#fitur)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Struktur Proyek](#struktur-proyek)
- [Pemetaan Koordinat](#pemetaan-koordinat)
- [Pemecahan Masalah](#pemecahan-masalah)
- [Catatan Penting](#catatan-penting)
- [Lisensi](#lisensi)

---

## Fitur
- ✅ Login otomatis ke OLT Tenda (IP `100.10.1.254`, user `admin`/`admin`)
- ✅ Mendapatkan daftar semua SN ONT dari halaman *Authorized List*
- ✅ Buka halaman **Configure** → tab **Gemport**
- ✅ **Delete** konfigurasi Gemport (dengan klik tombol Delete → konfirmasi OK)
- ✅ **Add** konfigurasi Gemport baru (isi form → klik Apply)
- ✅ Menyimpan screenshot setiap langkah penting (folder `screenshots/`)
- ✅ Bekerja dalam mode **headless** (`xvfb-run`) untuk server tanpa GUI

---

## Prasyarat
| Komponen | Versi / Catatan |
|----------|----------------|
| Sistem operasi | Ubuntu 22.04 / 26.04 atau Debian-based |
| Python | 3.14+ |
| Chromium / Chrome | `chromium-browser` (≥ 147.0) |
| ChromeDriver | Tersedia otomatis bersama `chromium-chromedriver` |
| Xvfb | Untuk headless (jika tidak ada display) |
| Koneksi jaringan | Ke `100.10.1.254` (OLT) |

---

## Instalasi

### 1. Clone repositori
```bash
git clone https://github.com/Bimaoitsuki/Tenda-tes-7002.git
cd Tenda-tes-7002
```

2. Install dependensi Python

```bash
pip install -r requirements.txt
```

3. Install Chromium & ChromeDriver

```bash
sudo apt update
sudo apt install chromium-browser chromium-chromedriver
```

4. Install Xvfb (untuk lingkungan headless)

```bash
sudo apt install xvfb
```

---

Penggunaan

🔹 Hapus konfigurasi Gemport (Delete)

```bash
xvfb-run --auto-servernum python3 net.py <SN_ONT>
```

Contoh:

```bash
xvfb-run --auto-servernum python3 net.py CIOT16D9D920
```

🔹 Tambah konfigurasi Gemport baru (Add)

```bash
xvfb-run --auto-servernum python3 add.py <SN_ONT>
```

Contoh:

```bash
xvfb-run --auto-servernum python3 add.py CIOT16D9D920
```

Catatan: Program akan menyimpan screenshot di folder screenshots/ dan log di file *.log.

---

Struktur Proyek

```
Tenda-tes-7002/
├── net.py                       # Hapus Gemport (utama)
├── add.py                       # Tambah Gemport (utama)
├── map_gemport_add.py           # Utilitas mapping dialog Add
├── olt_gemport_delete_mapper.py # Utilitas mapping tombol Delete
├── olt_gemport_delete_confirm.py# Utilitas mapping dialog OK/Cancel
├── requirements.txt             # Dependensi Python
├── config_maps/                 # File JSON hasil mapping koordinat
│   ├── gemport_CIOT16D9D920_mapping.json
│   ├── confirm_dialog_CIOT16D9D920.json
│   └── add_gemport_CIOT16D9D920.json
├── screenshots/                 # Screenshot debug (otomatis dibuat)
└── README.md                    # Dokumentasi ini
```

---

Pemetaan Koordinat

Karena tombol pada halaman web sering tidak dapat di‑interact secara langsung, program ini menggunakan koordinat absolut (x, y) untuk mengklik elemen.
Koordinat diperoleh dengan menjalankan utility mapper interaktif:

```bash
xvfb-run --auto-servernum python3 olt_gemport_delete_mapper.py
```

Ikuti instruksi di terminal (pilih nomor SN). Program akan:

1. Login, buka Configure → Gemport
2. Mencari tombol Delete, menyimpan koordinat ke config_maps/gemport_<SN>.json
3. Klik Delete, menangkap dialog, menyimpan koordinat OK/Cancel ke confirm_dialog_<SN>.json

Perhatian: Koordinat hanya valid untuk resolusi 1920x1080 dengan window maximized. Jika resolusi berubah, ulangi proses mapping.

---

Pemecahan Masalah

Error Kemungkinan Penyebab Solusi
element not interactable Tombol tertutup / belum siap Gunakan koordinat dari mapping ulang (lihat bagian Pemetaan Koordinat)
no such element Selector berubah (update firmware) Jalankan ulang program mapper untuk mendapatkan koordinat baru
WebDriverException Chromium/ChromeDriver versi mismatch sudo apt update && sudo apt upgrade chromium-browser chromium-chromedriver
Login gagal Kredensial salah atau koneksi bermasalah Coba akses http://100.10.1.254 melalui browser biasa
Halaman configure tidak muncul Klik Configure tidak berhasil Pastikan SN benar dan ONT dalam status online

---

Catatan Penting

· Kredensial saat ini di‑hardcode (admin/admin). Untuk lingkungan produksi, gunakan variabel lingkungan atau file konfigurasi terenkripsi.
· Koordinat bersifat statis dan bergantung pada resolusi layar (1920x1080). Jika menggunakan resolusi berbeda, lakukan mapping ulang.
· Stabilitas: Program ini bergantung pada struktur HTML antarmuka web OLT. Perubahan firmware dapat merusak kompatibilitas.
· Screenshot disimpan di folder screenshots/; hapus secara berkala jika tidak diperlukan.
· Semua operasi bersifat non‑destruktif (tidak mengubah konfigurasi selain Gemport yang ditargetkan). Namun tetap disarankan untuk menguji di lingkungan non‑produksi terlebih dahulu.

---

Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT – lihat file LICENSE untuk detail lengkap.

---

Kontribusi

Pull request dipersilakan. Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan apa yang ingin diubah.

---

Disclaimer

Perangkat lunak ini disediakan "apa adanya", tanpa jaminan apa pun. Penulis tidak bertanggung jawab atas kerusakan atau gangguan layanan yang mungkin timbul akibat penggunaan program ini. Gunakan dengan risiko Anda sendiri.

---

Dibuat dengan ❤️ oleh Bimaoitsuki

```

---

## 2. File `LICENSE` (MIT)

```text
MIT License

Copyright (c) 2026 Bimaoitsuki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

3. File requirements.txt

```txt
selenium>=4.15.0
```

Catatan: xvfb dan chromium diinstal melalui package manager sistem, tidak melalui pip.
