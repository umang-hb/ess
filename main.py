import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from apscheduler.schedulers.blocking import BlockingScheduler
from plyer import notification
from selenium import webdriver
from time import sleep
from datetime import time
from datetime import datetime, date
import requests
import wget
import zipfile
import os

from utils import decrypt

LOG_DIR = os.getcwd() + os.sep + 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    handlers=[logging.FileHandler(LOG_DIR + os.sep + datetime.now().strftime('ess_%d_%m_%Y.log')),
              logging.StreamHandler()],
    format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)


def get_driver():
    # get the latest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text

    # build the donwload url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number + "/chromedriver_win32.zip"

    # download the zip file using the url built above
    latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

    # extract the zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall()  # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)


def check_and_send_notification():
    daily_remaining_hours, _, _ = ess_get_working_hours()
    if daily_remaining_hours.seconds < 3600:
        notification.notify(
            title="ESS | HB",
            message=str(daily_remaining_hours) + ' remaining.',
            timeout=2
        )


def ess_get_working_hours():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("http://ess.hiddenbrains.net/")
    driver.find_element(By.ID, "email_address").send_keys(decrypt(credentials=os.environ['ESS_USERNAME']))
    driver.find_element(By.ID, "password").send_keys(decrypt(credentials=os.environ['ESS_PASSWORD']))
    driver.find_element(By.NAME, "submit").click()  # login
    logging.info("logged in succesfully")
    sleep(3)
    logging.info('fetching data')
    driver.get("http://ess.hiddenbrains.net/attedance.html")
    sleep(5)

    logging.info('calculating ...')
    # daily working and remaining hours
    daily_working_hours = time.fromisoformat(driver.find_element(By.XPATH, "(//table/tbody/tr)[last()]/td[12]").text)
    daily_remaining_hours = datetime.combine(date.today(), time.fromisoformat("09:00")) - datetime.combine(date.today(),
                                                                                                           daily_working_hours)
    # weekly working and remaining hours
    week_hours = time.fromisoformat(driver.find_element(By.XPATH, "(//table/tbody/tr)[last()]/td[18]").text)

    return daily_remaining_hours, daily_working_hours, week_hours,


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(check_and_send_notification, 'interval', minutes=10)
    scheduler.start()
