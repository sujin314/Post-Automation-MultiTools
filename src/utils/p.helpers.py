import os
import logging
import re # 정규 표현식 모듈 임포트
import time
from playwright.sync_api import Page, expect # Playwright의 Page 객체와 expect 단언 사용
from selenium import webdriver

URL = "http://localhost:4100/"

class Utils:

    #로케이터
    MAIN_LOGO_CSS = "a.navbar-brand[href='/']" # CSS 선택자
    LOGIN_BTN_XPATH = "//a[text()='Sign in']" # XPath 선택자

    def __init__(self, page: Page): # WebDriver 대신 Page 객체를 받음
        self.page = page

    #로그인
    def utils_login(self, email, password):
        self.page.goto(URL)

        #로그인하기
        self.page.wait_for_selector(self.LOGIN_BTN_XPATH, state="visible")
        self.page.click(self.LOGIN_BTN_XPATH)

        #아이디, 패스워드
        email_input_xpath = "//input[@type='email' and @placeholder='Email']"
        password_input_xpath = "//input[@type='password' and @placeholder='Password']"
        self.page.wait_for_selector(email_input_xpath)
        self.page.fill(email_input_xpath, email)
        self.page.wait_for_selector(password_input_xpath)
        self.page.fill(password_input_xpath, password)

        #제출 버튼
        submit_btn_xpath = "//button[@type='submit' and text()='Sign in']"
        self.page.wait_for_selector(submit_btn_xpath, state="visible")
        self.page.click(submit_btn_xpath)

        #URL 검증
        # expect(self.page).not_to_have_url(lambda url: "login" in url, timeout=5000) # 람다 함수 대신 정규 표현식 사용
        # 로그인 성공 후 URL에 "login"이라는 문자열이 포함되지 않아야 함
        expect(self.page).not_to_have_url(re.compile("login"), timeout=5000)

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
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_name = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{func_name}.png") # 확장자 png로 변경 권장

        return screenshot_name

    #메인로고 클릭
    def main_logo(self):
        self.page.locator(self.MAIN_LOGO_CSS).click()

    #css 요소 찾기 + 클릭
    def css_selector_element(self, selector_str: str): # 매개변수 이름을 명확히
        self.page.locator(selector_str).click()

    #css 요소들 찾기 + (num)번째 클릭
    def css_selector_elements(self, selector_str: str, num: int):
        self.page.locator(selector_str).nth(num).click()


    #css 요소 찾기 + 입력값
    def css_selector_send(self, selector_str: str, text_to_send: str):
        self.page.locator(selector_str).fill(text_to_send)


    #xpath 요소 찾기 + 클릭
    def xpath_element(self, xpath_str: str):
        self.page.locator(f"xpath={xpath_str}").click() # Playwright는 xpath= 접두사 사용
    
    
    #xpath 요소들 찾기 + (num)번째 클릭
    def xpath_elements(self, xpath_str: str, num: int):
        self.page.locator(f"xpath={xpath_str}").nth(num).click()

    def get_driver(browser_name="chrome"):
        if browser_name == "chrome":
            return webdriver.Chrome()
        elif browser_name == "firefox":
            return webdriver.Firefox()
        else:
            raise ValueError("지원되지 않는 브라우저입니다.")
