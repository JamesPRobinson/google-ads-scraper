from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
import sys
import os
sys.path.append(os.getcwd())
from settings import RAW_OUTPUT_FOLDER

def get_driver():
    profile = FirefoxProfile()
    profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'text/plain, application/vnd.ms-excel, text/csv, text/comma-separated-values, application/octet-stream, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", str(RAW_OUTPUT_FOLDER))
    return webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=profile, service_log_path=os.devnull)
