import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BRIGHTWHEEL_URL = "https://mybrightwheel.com/login"
FSAFEDS_URL = "https://www.fsafeds.gov/login"
DOWNLOAD_DIR = "invoices"
USERNAME_BRIGHTWHEEL = os.getenv("BRIGHTWHEEL_USERNAME")  # Set in environment variables
PASSWORD_BRIGHTWHEEL = os.getenv("BRIGHTWHEEL_PASSWORD")
USERNAME_FSAFEDS = os.getenv("FSAFEDS_USERNAME")
PASSWORD_FSAFEDS = os.getenv("FSAFEDS_PASSWORD")
CHROMEDRIVER_PATH = "/path/to/chromedriver"  # Update with your ChromeDriver path

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def setup_driver():
    """Set up Selenium WebDriver with Chrome."""
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # Uncomment for headless mode
    # chrome_options.add_argument("--headless")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_brightwheel(driver):
    """Log in to Brightwheel."""
    try:
        logger.info("Navigating to Brightwheel login page")
        driver.get(BRIGHTWHEEL_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        
        # Enter credentials
        driver.find_element(By.ID, "email").send_keys(USERNAME_BRIGHTWHEEL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD_BRIGHTWHEEL)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for dashboard or 2FA
        WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
        logger.info("Successfully logged in to Brightwheel")
    except Exception as e:
        logger.error(f"Failed to log in to Brightwheel: {e}")
        raise

def download_invoices(driver):
    """Download invoices from Brightwheel and rename them."""
    try:
        # Navigate to payment history (adjust URL/path based on Brightwheel's structure)
        logger.info("Navigating to payment history")
        driver.get("https://mybrightwheel.com/payments/history")  # Hypothetical URL
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "payment-item")))
        
        # Find invoice download links
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        invoice_elements = soup.find_all("a", class_="download-invoice")  # Adjust selector
        for idx, element in enumerate(invoice_elements):
            invoice_url = element.get("href")
            if invoice_url:
                # Download the invoice
                response = requests.get(invoice_url, stream=True)
                if response.status_code == 200:
                    # Extract invoice metadata (e.g., date or invoice number)
                    invoice_date = element.get("data-date") or datetime.now().strftime("%Y%m%d")
                    invoice_number = element.get("data-invoice-number") or f"invoice_{idx+1}"
                    filename = f"brightwheel_invoice_{invoice_date}_{invoice_number}.pdf"
                    file_path = os.path.join(DOWNLOAD_DIR, filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded and saved invoice: {filename}")
                else:
                    logger.warning(f"Failed to download invoice from {invoice_url}")
    except Exception as e:
        logger.error(f"Error downloading invoices: {e}")
        raise

def login_to_fsafeds(driver):
    """Log in to FSAFEDS."""
    try:
        logger.info("Navigating to FSAFEDS login page")
        driver.get(FSAFEDS_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        # Enter credentials
        driver.find_element(By.ID, "username").send_keys(USERNAME_FSAFEDS)
        driver.find_element(By.ID, "password").send_keys(PASSWORD_FSAFEDS)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Handle potential 2FA or CAPTCHA manually
        logger.info("Check for 2FA or CAPTCHA and handle manually if needed")
        WebDriverWait(driver, 30).until(EC.url_contains("dashboard"))
        logger.info("Successfully logged in to FSAFEDS")
    except Exception as e:
        logger.error(f"Failed to log in to FSAFEDS: {e}")
        raise

def upload_to_fsafeds(driver):
    """Upload invoices to FSAFEDS."""
    try:
        logger.info("Navigating to FSAFEDS claim submission page")
        driver.get("https://www.fsafeds.gov/claims/submit")  # Hypothetical URL
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "file-upload")))
        
        # Iterate through downloaded invoices
        for filename in os.listdir(DOWNLOAD_DIR):
            if filename.endswith(".pdf"):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                driver.find_element(By.ID, "file-upload").send_keys(file_path)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                logger.info(f"Uploaded {filename} to FSAFEDS")
                time.sleep(2)  # Wait for upload to process
    except Exception as e:
        logger.error(f"Error uploading to FSAFEDS: {e}")
        raise

def main():
    driver = None
    try:
        driver = setup_driver()
        login_to_brightwheel(driver)
        download_invoices(driver)
        login_to_fsafeds(driver)
        upload_to_fsafeds(driver)
    except Exception as e:
        logger.error(f"Automation failed: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    main()