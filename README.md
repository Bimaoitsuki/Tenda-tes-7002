# Tenda-tes-7002
Screper web ui olt pemutusan sumber internet via olt. Only os ubuntu 


Dokumentasi Developer – OLT GPON Tenda Automation

Proyek: Otomatisasi operasional ONT (Delete/Add Gemport) untuk kebutuhan Billing
IP OLT: 100.10.1.254
Device: Tenda tes 7001/7002
Frimware: V3.0.0.47
Hardware: V0.0.0.1
Kredensial: admin / admin
Bahasa: Python 3.14+
Dependensi utama: selenium, xvfb (headless)

---

1. Arsitektur Umum

```
┌─────────────────────────────────────────────────────┐
│  Terminal (SSH)                                      │
│  └─ xvfb-run python3 <script>.py <SN>               │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Selenium WebDriver (Chromium)                      │
│  - login                                             │
│  - navigasi halaman Authorized List                  │
│  - klik Configure, tab Gemport                       │
│  - klik Delete / Add + konfirmasi                    │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Koordinat & mapping (file JSON)                    │
│  - gemport_CIOT16D9D920_mapping.json                │
│  - confirm_dialog_CIOT16D9D920.json                 │
│  - add_gemport_CIOT16D9D920.json                    │
└─────────────────────────────────────────────────────┘
```

Semua interaksi dilakukan melalui browser headless (Chromium) dengan bantuan X Virtual Framebuffer (xvfb).

---

2. Struktur File Proyek

```
/var/www/
├── net.py                    # Auto delete (dengan argumen SN)
├── add.py                    # Auto add Gemport (dengan argumen SN)
├── map_gemport_add.py        # Mapping dialog Add Gemport
├── olt_gemport_delete_mapper.py  # Mapping tombol Delete
├── olt_gemport_delete_confirm.py # Mapping tombol OK/Cancel
├── config_maps/              # Folder hasil mapping JSON
│   ├── gemport_CIOT16D9D920_mapping.json
│   ├── confirm_dialog_CIOT16D9D920.json
│   └── add_gemport_CIOT16D9D920.json
└── screenshots/              # Screenshot debug
```

---

3. Kode Inti (Template)

3.1. Setup driver

```python
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.binary_location = "/usr/bin/chromium-browser"
    return webdriver.Chrome(options=options)
```

3.2. Login

```python
def login(driver):
    driver.get("http://100.10.1.254/login.html")
    wait = WebDriverWait(driver, 10)
    username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password = driver.find_element(By.NAME, "password")
    username.send_keys("admin")
    password.send_keys("admin")
    driver.find_element(By.ID, "submit").click()
    time.sleep(3)
    return "login" not in driver.current_url.lower()
```

3.3. Klik Configure pada SN

```python
def click_configure(driver, sn):
    driver.get("http://100.10.1.254/index.html#/manage/authorized-list")
    rows = driver.find_elements(By.CSS_SELECTOR, "#authorized-module tbody tr")
    for row in rows:
        sn_cell = row.find_element(By.CSS_SELECTOR, "td[id$='-sn'] p.fixed")
        if sn_cell.text.strip() == sn:
            row.find_elements(By.CSS_SELECTOR, "span.operate__col--edit")[0].click()
            return True
    return False
```

3.4. Klik tab Gemport

```python
def click_gemport_tab(driver):
    tab = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Gemport')]"))
    )
    tab.click()
    time.sleep(2)
```

3.5. Klik menggunakan koordinat (fallback andal)

```python
def click_coord(driver, x, y):
    driver.execute_script(f"document.elementFromPoint({x+10}, {y+10}).click();")
```

3.6. Menunggu elemen muncul

```python
def wait_for_configure_page(driver):
    for _ in range(30):
        if driver.find_elements(By.XPATH, "//*[contains(text(),'DBA Template')]"):
            return True
        time.sleep(0.5)
    return False
```

---

4. Alur Program net.py (Delete Gemport)

```python
sn = sys.argv[1]
driver = get_driver()
login(driver)
click_configure(driver, sn)
wait_for_configure_page(driver)
click_gemport_tab(driver)
# Klik Delete (koordinat 929,233)
click_coord(driver, 929, 233)
# Tunggu dialog
wait = WebDriverWait(driver, 5)
wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Do you want to Delete?')]")))
# Klik OK (koordinat 909,184)
click_coord(driver, 909, 184)
print("✅ Delete sukses")
driver.quit()
```

---

5. Alur Program add.py (Add Gemport)

```python
sn = sys.argv[1]
driver = get_driver()
login(driver)
click_configure(driver, sn)
wait_for_configure_page(driver)
click_gemport_tab(driver)
driver.find_element(By.ID, "gemport-add").click()
time.sleep(1)
# Isi form via JavaScript (cari label)
fill_js = """
function setByLabel(label, value, isSelect=false) {
    let spans = [...document.querySelectorAll('*')];
    for(let el of spans) {
        if(el.textContent.trim() === label) {
            let input = el.parentNode.querySelector('input, select');
            if(input) {
                if(isSelect) { input.value = value; input.dispatchEvent(new Event('change')); }
                else { input.value = value; input.dispatchEvent(new Event('input')); }
                return true;
            }
        }
    }
    return false;
}
setByLabel('Service Name', 'gemport-1');
setByLabel('Tcont Name', 'tcont-1');
setByLabel('VLAN Mode', 'Transparent', true);
"""
driver.execute_script(fill_js)
# Klik Apply (koordinat 1086,548)
click_coord(driver, 1086, 548)
print("✅ Add sukses")
driver.quit()
```

---

6. Mapping Koordinat (Cara Mendapatkan)

Jalankan script mapper interaktif:

```bash
xvfb-run --auto-servernum python3 olt_gemport_delete_mapper.py
```

Program akan:

· Login, pilih SN (contoh 36 untuk CIOT16D9D920)
· Navigasi ke Gemport
· Mencari tombol Delete dan menyimpan koordinat ke gemport_CIOT16D9D920_mapping.json
· Kemudian klik Delete → tangkap dialog → simpan koordinat OK/Cancel ke confirm_dialog_CIOT16D9D920.json

File JSON hasil mapping (contoh):

```json
{
  "delete_buttons": [{"x": 929, "y": 233}],
  "confirm_buttons": [
    {"text": "Cancel", "x": 996, "y": 548},
    {"text": "OK", "x": 1086, "y": 548}
  ]
}
```

---

7. Menjalankan Otomatisasi

```bash
# Untuk Delete
xvfb-run --auto-servernum python3 net.py CIOT16D9D920

# Untuk Add
xvfb-run --auto-servernum python3 add.py CIOT16D9D920
```

Catatan: Pastikan chromium-browser dan chromedriver terinstall. Jika tidak, install:

```bash
sudo apt install chromium-browser chromium-chromedriver
```

---

8. Troubleshooting Umum

Error Kemungkinan Penyebab Solusi
element not interactable Tombol tertutup / belum siap Gunakan click_coord() dengan koordinat dari mapping ulang
no such element Selector berubah (update UI) Jalankan ulang script mapper untuk mendapatkan koordinat baru
WebDriverException: unknown error Chromium/ChromeDriver versi mismatch Update chromium dan chromedriver
Login gagal Kredensial salah atau halaman redirect Cek manual di browser, pastikan name="username" dan id="submit" masih ada
Halaman configure tidak muncul Klik Configure tidak berhasil Periksa span.operate__col--edit dan apakah SN muncul di tabel

---

9. Catatan Penting

· Koordinat hanya valid untuk resolusi 1920x1080 dengan window maximized. Jika resolusi berubah, lakukan mapping ulang.
· ID tombol OK pada dialog delete bersifat dinamis (mengandung angka random), karena itu mapping koordinat lebih andal.
· Semua program menggunakan headless (xvfb-run). Untuk debugging, hapus xvfb-run dan jalankan langsung di lingkungan desktop (aktifkan headless=False).
· Log proses tersimpan di file *.log (misal gemport_delete_ok_fixed.log).

---

10. Lisensi & Kontribusi

Dikembangkan untuk keperluan internal. Diperbolehkan memodifikasi sesuai kebutuhan.
Maintainer: [solo vibe]

---

Dokumentasi ini mencakup semua aspek teknis yang diperlukan untuk memahami, menggunakan, dan mengembangkan lebih lanjut sistem otomatisasi OLT GPON Tenda.
