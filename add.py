#!/usr/bin/env python3
"""
OLT Gemport Auto Add - One Shot (dengan JavaScript injection)
Usage: xvfb-run --auto-servernum python3 add.py CIOT16D9D920
"""

import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_IP = "100.10.1.254"
BASE_URL = f"http://{TARGET_IP}"
LOGIN_URL = f"{BASE_URL}/login.html"
USERNAME = "admin"
PASSWORD = "admin"

# Koordinat tombol Apply (dari mapping yang sudah berhasil)
APPLY_X, APPLY_Y = 1086, 548

# Nilai default untuk form Add Gemport
DEFAULT_SERVICE_NAME = "gemport-1"
DEFAULT_TCONT_NAME = "tcont-1"
DEFAULT_VLAN_MODE = "Transparent"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def click_add_button(driver):
    try:
        driver.find_element(By.ID, "gemport-add").click()
        logger.info("Klik Add")
        return True
    except:
        try:
            driver.find_element(By.XPATH, "//button[contains(text(),'Add')]").click()
            logger.info("Klik Add (by text)")
            return True
        except:
            logger.error("Tombol Add tidak ditemukan")
            return False

def fill_add_form_via_js(driver):
    """Isi form Add Gemport menggunakan JavaScript (handal, tanpa element interactable)."""
    script = """
    function fillByLabel(labelText, value, isSelect=false) {
        var allElements = document.querySelectorAll('*');
        for (var i = 0; i < allElements.length; i++) {
            if (allElements[i].textContent.trim() === labelText) {
                var parent = allElements[i].parentNode;
                var input = parent.querySelector('input, select');
                if (input) {
                    if (isSelect) {
                        input.value = value;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else {
                        input.value = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    return true;
                }
            }
        }
        return false;
    }
    fillByLabel('Service Name', arguments[0], false);
    fillByLabel('Tcont Name', arguments[1], false);
    fillByLabel('VLAN Mode', arguments[2], true);
    return true;
    """
    try:
        driver.execute_script(script, DEFAULT_SERVICE_NAME, DEFAULT_TCONT_NAME, DEFAULT_VLAN_MODE)
        logger.info("Form Add diisi via JavaScript")
        time.sleep(0.5)
    except Exception as e:
        logger.warning(f"Gagal mengisi form via JS: {e}")

def click_apply(driver):
    try:
        driver.execute_script(f"document.elementFromPoint({APPLY_X+10}, {APPLY_Y+10}).click();")
        logger.info(f"Klik Apply di koordinat ({APPLY_X}, {APPLY_Y})")
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Gagal klik Apply: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: xvfb-run --auto-servernum python3 add.py <SN>")
        sys.exit(1)
    sn = sys.argv[1]
    logger.info(f"Memulai proses Add Gemport untuk SN: {sn}")
    driver = None
    try:
        driver = get_driver()
        if not login(driver):
            return
        if not click_configure_by_sn(driver, sn):
            return
        if not wait_for_configure_page(driver):
            return
        if not click_tab(driver, "Gemport"):
            return
        time.sleep(2)
        if not click_add_button(driver):
            return
        time.sleep(1)
        fill_add_form_via_js(driver)
        if click_apply(driver):
            logger.info(f"✅ Add Gemport berhasil untuk SN {sn}")
        else:
            logger.error(f"❌ Gagal mengklik Apply")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()