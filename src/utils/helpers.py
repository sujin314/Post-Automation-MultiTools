import os
import logging
import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait as ws
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

URL = "http://localhost:4100/"

class Utils:

    #로케이터
    MAIN_LOGO = (By.CSS_SELECTOR, "a.navbar-brand[href='/']")
    LOGIN_BTN = (By.XPATH, "//a[text()='Sign in']")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = ws(driver, 10)

    #로그인
    def utils_login(self, email, password):
        self.driver.get(URL)

        #로그인하기
        login_btn = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN))
        login_btn.click()

        #아이디, 패스워드
        input_email = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email' and @placeholder='Email']")))
        input_email.send_keys(email)
        input_password = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @placeholder='Password']")))
        input_password.send_keys(password)

        #제출 버튼
        submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and text()='Sign in']")))
        submit_btn.click()

        #URL 검증
        self.wait.until(EC.url_contains(""))
        assert "" in self.driver.current_url

    # 로그, 스크린샷 설정
    def utils_reports_setting(page_name, func_name):
        LOG_DIR = f"reports/logs/{page_name}"
        SCREENSHOT_DIR = f"reports/screenshots/{page_name}"

        # 폴더 없을 시 생성
        os.makedirs(LOG_DIR, exist_ok=True)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # 로깅 설정
        logger = logging.getLogger()

        # 핸들러를 매번 초기화하고 새로 추가
        logger.handlers.clear()

        logger.setLevel(logging.INFO)
        #file_handler = logging.FileHandler(f"{LOG_DIR}/{page_name}.log", encoding="utf-8") #기존에 추가하기
        file_handler = logging.FileHandler(f"{LOG_DIR}/{page_name}.log", mode="w", encoding="utf-8")  # 🔥 mode="w"로 변경하여 덮어쓰기 설정
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"))
        logger.addHandler(file_handler)

        # 스크린샷 설정
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{func_name}.jpg")

        return screenshot_name

    #메인로고 클릭
    def main_logo(self):
        navbar_link = self.wait.until(EC.element_to_be_clickable(self.MAIN_LOGO))
        navbar_link.click()
        
    #css 요소 찾기 + 클릭
    def css_selector_element(self,str):
        element = self.wait.until(EC.element_to_be_clickable((str)))
        element.click()

    #css 요소들 찾기 + (num)번째 클릭
    def css_selector_elements(self,str,num):
        # 모든 요소를 리스트로 가져오기
        elements = self.wait.until(EC.presence_of_all_elements_located(str))
        # 지정된 인덱스(num)의 요소 클릭
        elements[num].click()

    #css 요소 찾기 + 입력값
    def css_selector_send(self,str1,str2):
        textarea_element = self.wait.until(EC.presence_of_element_located(str1))  # ✅ 튜플 형태로 전달
        # 텍스트 입력
        textarea_element.send_keys(str2)

    #xpath 요소 찾기 + 클릭
    def xpath_element(self,str):
        element = self.wait.until(EC.presence_of_element_located(str))
        element.click()
    
    #xpath 요소들 찾기 + (num)번째 클릭
    def xpath_elements(self,str,num):
        elements = self.wait.until(EC.presence_of_all_elements_located(str))
        elements[num].click()

