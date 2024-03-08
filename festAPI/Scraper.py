from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

class YulchonScraper:
    def __init__(self, driver_path='./chromedriver'):
        self.driver_path = driver_path
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=self.options)
    
    def scrape_and_save(self, url, name, output_path):
        # 이미 학습된 자료가 있는지 체크
        if os.path.exists(output_path + name + ".html"):
            print("File already exists.")
            return "이미 학습되어 있는 파일이 존재함."
        
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 2)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'content')))
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        content_element = soup.find(class_='content')
        if content_element:
            with open(output_path + name + ".html", 'w', encoding='utf-8') as f:
                f.write(str(content_element))
        return name + ".html"

    def close_driver(self):
        self.driver.quit()