# Imported modules
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Home libraries
from Driver import driver
# Runup a level
import sys
import os
sys.path.append(os.getcwd())
from settings import OUTPUT_FOLDER

class GABrowser():
    def __init__(self):
        self.driver = driver.get_driver()
        self.ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    
    def get(self, url):
        self.driver.get(url)

    def clickElement(self, xpath, w=1000):
        wait = WebDriverWait(self.driver, w, ignored_exceptions=self.ignored_exceptions)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        self.driver.find_element_by_xpath(xpath).click()

    
    def getElement(self, xpath, w=1000):
        wait = WebDriverWait(self.driver, w, ignored_exceptions=self.ignored_exceptions)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return self.driver.find_element_by_xpath(xpath)
