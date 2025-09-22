import time
import sys
from pathlib import Path # <--- 이 라인을 여기로 옮깁니다.

project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path: # 중복 추가 방지
    sys.path.insert(0, str(project_root))

from selenium.webdriver.remote.webdriver import WebDriver
from src.pages.postpage import PostPage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


#                 robot tests\robot_tests\postpage_test.robot    

class UtilsLibrary:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'  # 라이브러리 인스턴스 범위 설정
    ROBOT_AUTO_KEYWORDS = True      # 메서드를 자동으로 키워드로 인식하도록 명시 (기본값 True)

    """
    로봇 프레임워크 테스트를 위한 유틸리티 라이브러리입니다.
    이 라이브러리는 커스텀 키워드를 제공합니다.
    """
    def __init__(self):
        self.driver = None
        self.wait = None
        # find_and_click_other_user_article_in_global_feed 메서드에서 사용될 로케이터
        # 실제 웹사이트의 구조에 맞게 XPath를 정확히 지정해야 합니다.
        self.ARTICLE_PREVIEWS_GLOBAL_FEED = (By.XPATH, "//div[@class='article-preview']")
        self.AUTHOR_LINK_IN_PREVIEW = (By.XPATH, ".//a[contains(@class, 'author')]") # article_preview_element 내부에서 검색
        self.ARTICLE_READ_MORE_LINK_IN_PREVIEW = (By.XPATH, ".//a[contains(@class, 'preview-link')]") # article_preview_element 내부에서 검색
        self.PAGINATION_LINK = (By.XPATH, "//ul[@class='pagination']//a[@class='page-link']") # 페이지네이션 링크 로케이터


    def generate_unique_text(self, prefix="Test"):
        """
        접두사와 현재 타임스탬프를 사용하여 고유한 텍스트 문자열을 생성합니다.
        로봇 프레임워크에서는 'Generate Unique Text' 키워드로 사용됩니다.
        """
        unique_string = f"{prefix} {int(time.time())}"
        return unique_string
    
    def _ensure_selenium_resources(self):
        """WebDriver와 WebDriverWait 인스턴스를 가져오거나 초기화합니다."""
        if not self.driver:
            self.driver = self._get_driver_instance()
        if not self.wait and self.driver: # self.driver가 성공적으로 로드된 후에 self.wait 초기화
            self.wait = WebDriverWait(self.driver, 10) # 기본 타임아웃 10초

    def find_and_click_other_user_article_in_global_feed(self, current_username, max_pages_to_check=10):
        self._ensure_selenium_resources()
        if not self.driver or not self.wait: # 드라이버나 wait 객체가 없으면 오류 발생
            raise Exception("WebDriver or WebDriverWait not initialized. Ensure a browser is open.")
        
        print(f"DEBUG: Current user (from navbar) for comparison: repr='{repr(current_username)}', value='{current_username}'") # 현재 사용자 이름 상세 로깅
        current_page_number = 1 # 페이지네이션을 위해 현재 페이지 번호 추적
        for page_attempt in range(1, max_pages_to_check + 1):
            print(f"페이지 {page_attempt}에서 다른 사용자 게시글 검색 중...") # 페이지 번호 출력 수정
            try:
                # 페이지에 게시글 요소들이 나타날 때까지 기다립니다.
                self.wait.until(EC.visibility_of_all_elements_located(self.ARTICLE_PREVIEWS_GLOBAL_FEED))
                articles = self.driver.find_elements(*self.ARTICLE_PREVIEWS_GLOBAL_FEED)
            except TimeoutException:
                print(f"페이지 {page_attempt + 1}에서 게시글을 로드하는 데 실패했거나 게시글이 없습니다.")
                if page_attempt == 0: # 첫 페이지부터 글이 없는 경우
                    print("DEBUG: 글로벌 피드에 게시글이 없습니다 (첫 페이지 타임아웃).")
                    return False
                break # 현재 페이지 또는 이전 페이지에서 게시글을 찾지 못하면 중단
            
            if not articles: # 현재 페이지에 게시글이 없는 경우 (첫 페이지 이후)
                print(f"페이지 {page_attempt + 1}에 게시글이 더 이상 없습니다.")
                break
            
            for article_preview_element in articles:
                try:
                    author_element = article_preview_element.find_element(*self.AUTHOR_LINK_IN_PREVIEW)
                    author_name = author_element.text.strip()
                    print(f"DEBUG: Article author: repr='{repr(author_name)}', value='{author_name}'") # 게시글 작성자 상세 로깅
                    
                    # 비교 로직 상세 로깅
                    is_author_name_valid = bool(author_name)
                    is_different_user = author_name != current_username
                    print(f"DEBUG: Comparing: author_name_valid={is_author_name_valid}, is_different_user ({repr(author_name)} != {repr(current_username)}) = {is_different_user}")

                    if is_author_name_valid and is_different_user:
                        print(f"DEBUG: Condition MET. Found other user's article. Author: '{author_name}'. Clicking...")
                        read_more_link = article_preview_element.find_element(*self.ARTICLE_READ_MORE_LINK_IN_PREVIEW)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", read_more_link)
                        time.sleep(0.5) # 스크롤 후 잠시 대기
                        # 클릭 가능할 때까지 기다린 후 클릭
                        self.wait.until(EC.element_to_be_clickable(read_more_link)).click()
                        print(f"DEBUG: Successfully clicked article by '{author_name}' (repr: {repr(author_name)}).")
                        return True #다른 사용자 게시글을 찾아 클릭 성공
                except Exception as e:
                    print(f"다른 사용자 게시글 찾는 중 개별 게시글 처리 오류: {e}")
                    continue
            
            # 현재 페이지에서 다른 사용자 글을 찾지 못했고, 아직 더 확인할 페이지가 남았다면 다음 페이지로 이동
            if page_attempt < max_pages_to_check:
                try:
                    # 다음 페이지 번호에 해당하는 링크를 찾습니다.
                    next_page_number_to_click = current_page_number + 1
                    pagination_links = self.driver.find_elements(*self.PAGINATION_LINK)
                    found_next_page_link = False
                    for link in pagination_links:
                        if link.text.strip() == str(next_page_number_to_click):
                            self.wait.until(EC.element_to_be_clickable(link)).click()
                            current_page_number = next_page_number_to_click # 현재 페이지 번호 업데이트
                            print(f"다음 페이지({current_page_number})로 이동했습니다.")
                            found_next_page_link = True
                            break
                    if not found_next_page_link:
                        print(f"다음 페이지({next_page_number_to_click}) 링크를 찾을 수 없습니다. 마지막 페이지일 수 있습니다.")
                        return False # 더 이상 다음 페이지가 없음
                except Exception as e:
                    print(f"다음 페이지로 이동 중 오류 발생: {e}")
                    return False # 페이지네이션 중 오류 발생 시 중단
            else: # max_pages_to_check 만큼 확인했으면 종료
                break
        print(f"'{current_username}' 사용자가 아닌 다른 사용자의 게시글을 {max_pages_to_check} 페이지 내에서 찾지 못했습니다.")
        return False # 모든 페이지를 확인했지만 찾지 못한 경우

    def _get_driver_instance(self) -> WebDriver:
        """
        Returns the current Selenium WebDriver instance from the SeleniumLibrary.
        """
        try:
            selenium_lib = self._get_selenium_library()
            if selenium_lib and hasattr(selenium_lib, 'driver'): # driver 속성이 있는지 확인
                return selenium_lib.driver
            else:
                raise Exception("SeleniumLibrary instance not found or browser not open/driver not available.")
        except Exception as e:
            raise Exception(f"Error getting WebDriver instance: {str(e)}")

    def _get_selenium_library(self):
        """
        Returns the SeleniumLibrary instance from Robot Framework's built-in libraries.
        """
        return BuiltIn().get_library_instance('SeleniumLibrary')

    def get_current_username(self):
        """
        네비게이션 바에 표시되는 현재 사용자 이름을 가져옵니다.
        """
        try:
            self._ensure_selenium_resources() # driver와 wait 객체 확보
            if not self.driver:
                raise Exception("WebDriver not initialized for get_current_username.")
            post_page = PostPage(self.driver) # PostPage 클래스가 driver를 인자로 받도록 가정
            return post_page.get_current_logged_in_username_from_navbar()
        except Exception as e:
            # 테스트 실패를 유발하기보다는 경고 로그를 남기고 "None"과 유사한 값을 반환하여
            # Robot Framework의 Run Keyword If에서 처리할 수 있도록 함
            BuiltIn().log(f"Error getting current username: {str(e)}", "WARN")
            return "None" # 또는 빈 문자열 ''
