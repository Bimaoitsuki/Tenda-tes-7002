#!/usr/bin/env python3
"""
OLT Gemport Auto Delete - One Shot
Usage: xvfb-run --auto-servernum python3 net.py CIOT16D9D920
"""

import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Konfigurasi
TARGET_IP = "100.10.1.254"
BASE_URL = f"http://{TARGET_IP}"
LOGIN_URL = f"{BASE_URL}/login.html"
USERNAME = "admin"
PASSWORD = "admin"

# Koordinat (dari mapping yang berhasil)
DELETE_X, DELETE_Y = 929, 233   # tombol Delete pada baris pertama
OK_X, OK_Y = 909, 184           # tombol OK pada dialog konfirmasi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.binary_location = "/usr/bin/chromium-browser"
    return webdriver.Chrome(options=options)

def login(driver):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)
    username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password = driver.find_element(By.NAME, "password")
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    driver.find_element(By.ID, "submit").click()
    for _ in range(15):
        time.sleep(1)
        if 'login' not in driver.current_url.lower():
            logger.info("Login berhasil")
            return True
    logger.error("Login gagal")
    return False

def click_configure_by_sn(driver, sn):
    driver.get(BASE_URL + "/index.html#/manage/authorized-list")
    time.sleep(2)
    rows = driver.find_elements(By.CSS_SELECTOR, "#authorized-module tbody tr")
    for row in rows:
        try:
            sn_cell = row.find_element(By.CSS_SELECTOR, "td[id$='-sn'] p.fixed")
            if sn_cell.text.strip() == sn:
                row.find_elements(By.CSS_SELECTOR, "span.operate__col--edit")[0].click()
                logger.info(f"Klik Configure untuk SN {sn}")
                return True
        except:
            continue
    logger.error(f"SN {sn} tidak ditemukan")
    return False

def wait_for_configure_page(driver):
    for _ in range(30):
        try:
            if driver.find_element(By.XPATH, "//*[contains(text(),'DBA Template')]"):
                logger.info("Halaman configure muncul")
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def click_tab(driver, tab_name):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{tab_name}')]"))
        ).click()
        logger.info(f"Klik tab '{tab_name}'")
        time.sleep(2)
        return True
    except:
        logger.error(f"Tab '{tab_name}' tidak ditemukan")
        return False

def delete_gemport(driver):
    # Klik Delete menggunakan koordinat
    driver.execute_script(f"document.elementFromPoint({DELETE_X+10}, {DELETE_Y+10}).click();")
    logger.info(f"Klik Delete di koordinat ({DELETE_X}, {DELETE_Y})")
    time.sleep(1)
    # Tunggu dialog
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Do you want to Delete?')]"))
        )
        logger.info("Dialog konfirmasi muncul")
    except:
        logger.warning("Dialog tidak muncul")
        return False
    # Klik OK menggunakan koordinat
    driver.execute_script(f"document.elementFromPoint({OK_X+10}, {OK_Y+10}).click();")
    logger.info(f"Klik OK di koordinat ({OK_X}, {OK_Y})")
    time.sleep(2)
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: xvfb-run --auto-servernum python3 net.py <SN>")
        sys.exit(1)
    sn = sys.argv[1]
    logger.info(f"Memulai proses untuk SN: {sn}")
    driver = get_driver()
    try:
        if not login(driver):
            return
        if not click_configure_by_sn(driver, sn):
            return
        if not wait_for_configure_page(driver):
            return
        if not click_tab(driver, "Gemport"):
            return
        time.sleep(2)
        if delete_gemport(driver):
            logger.info(f"✅ Delete berhasil untuk SN {sn}")
        else:
            logger.error(f"❌ Gagal delete SN {sn}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()