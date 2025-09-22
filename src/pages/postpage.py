from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

class PostPage:
    
    NAVBAR_USER_PROFILE_LINK = (By.CSS_SELECTOR, "a.nav-link[href^='/@']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.GLOBAL_FEED_TAB = (By.XPATH, "//ul[contains(@class, 'navbar-nav')]//a[contains(., 'Global Feed')]") # 글로벌 피드 탭 로케이터 (이미 있다면 그걸 사용)
        self.ARTICLE_PREVIEWS_GLOBAL_FEED = (By.CSS_SELECTOR, "div.article-preview")
        self.AUTHOR_LINK_IN_PREVIEW = (By.CSS_SELECTOR, "a.author") # article_preview 요소 내부의 작성자 링크
        self.ARTICLE_READ_MORE_LINK_IN_PREVIEW = (By.XPATH, ".//a[contains(@class, 'preview-link')]") # article_preview 요소 내부의 'Read more...' 링크
        # 페이지네이션 관련 로케이터 추가
        self.PAGINATION_UL = (By.CSS_SELECTOR, "ul.pagination")
        self.PAGINATION_LINK_IN_ITEM = (By.TAG_NAME, "a") # li.page-item 내부의 a 태그
   
    def click_button(self, xpath: str):
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        button.click()

    #newpost 버튼 클릭
    def click_newpost(self):
        self.click_button("//a[@href='/editor' and contains(., 'New Post')]")

    #publish article 버튼 클릭
    def click_publish_article(self):
        self.click_button("//button[contains(@class, 'btn-primary') and text()='Publish Article']")

    #home 버튼 클릭
    def click_home(self):
        self.click_button("//a[contains(@class, 'nav-link') and text()='Home']")

    #게시글 작성 페이지
    def go_to_editor_page(self):
        self.driver.get("http://localhost:4100/editor")

    #게시글 제목 입력
    def enter_post_title(self, text):
        input_title = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Article Title']")))
        input_title.clear() # 기존 내용 지우기, 수정 테스트 위함
        input_title.send_keys(text)

    #게시글 주제 입력
    def enter_post_topic(self, text):
        input_topic = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"What's this article about?\"]")))
        input_topic.clear() # 기존 내용 지우기
        input_topic.send_keys(text)

    #게시글 내용 입력
    def enter_post_body(self, text):
        input_body = self.wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Write your article (in markdown)']")))
        input_body.clear() # 기존 내용 지우기
        input_body.send_keys(text)

    #게시글 태그 입력 (수정 시 필요할 수 있음)
    def enter_post_tags(self, text):
        input_tags = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter tags']")))
        input_tags.clear() # 기존 내용 지우기
        input_tags.send_keys(text)
        input_tags.send_keys(Keys.RETURN)  # 엔터키 입력

    #네이게이션 바에 있는 현재 로그인된 사용자의 닉네임 클릭
    def click_user_profile(self):
        try:
            profile_link_element = self.wait.until(
                EC.element_to_be_clickable(self.NAVBAR_USER_PROFILE_LINK)
            )
            profile_link_element.click()
            print("네비게이션 바에서 현재 사용자 프로필 링크를 클릭했습니다.")
        except TimeoutException:
            print(f"오류: 네비게이션 바에서 현재 사용자 프로필 링크({self.NAVBAR_USER_PROFILE_LINK})를 찾거나 클릭할 수 없습니다 (시간 초과).")
            raise # 테스트 실패를 위해 예외를 다시 발생시킵니다.
        except Exception as e:
            print(f"네비게이션 바에서 현재 사용자 프로필 링크를 클릭하는 중 예기치 않은 오류 발생: {e}")
            raise

    #"My Articles" 탭이 활성화 확인
    def is_my_articles_tab_active(self):
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='articles-toggle']//ul[contains(@class, 'nav-pills')]/li/a[contains(text(), 'My Articles') and contains(@class, 'active')]")
            ))
            return True
        except:
            return False

    #프로필 페이지에서 특정 제목의 게시글 존재 확인
    def is_article_visible_in_profile(self, title: str):
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//div[@class='article-preview' and .//h1[contains(text(), '{title}')]]")
            ))
            return True
        except:
            return False

    #프로필 페이지에서 특정 제목의 게시글 클릭
    def click_article_in_profile_by_title(self, title: str):
        article_link = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@class='article-preview' and .//h1[contains(text(), '{title}')]]//a[contains(@class, 'preview-link')]")
        ))
        article_link.click()

    #게시글 상세 페이지에서 작성자 프로필 링크 클릭 (사용자 이름 기반)
    def click_author_link_on_article_page(self, username: str):
        author_link = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'article-meta')]//a[contains(@href, '/@{username}') and normalize-space()='{username}']")))
        author_link.click()

    #프로필 페이지에서 특정 제목의 게시글 링크(href) 가져오기
    def get_article_link_href_in_profile(self, title: str):
        try:
            article_link_element = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//div[@class='article-preview' and .//h1[contains(text(), '{title}')]]//a[contains(@class, 'preview-link')]")
            ))
            return article_link_element.get_attribute('href')
        except:
            return None
        
    #게시글 수정 버튼 클릭
    def click_edit_article(self):
        self.click_button("//a[contains(@class, 'btn-outline-secondary') and contains(@class, 'btn-sm') and normalize-space(.)='Edit Article']")
    
    #게시글 삭제 버튼 클릭
    def click_delete_article(self):
        self.click_button("//button[contains(@class, 'btn-outline-danger') and contains(@class, 'btn-sm') and contains(normalize-space(.), 'Delete Article')]")
    
    #게시글 상세 페이지에서 제목 가져오기
    def get_article_title_on_detail_page(self):
        try:
            title_element = self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='banner']//h1")
            ))
            return title_element.text
        except:
            return None

    #게시글 상세 페이지에서 본문 내용 가져오기
    def get_article_body_on_detail_page(self):
        try:
            body_element = self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'article-content')]//div/p")
            ))
            return body_element.text
        except:
            return None

    def verify_no_error_messages_present(self):
        error_elements = self.driver.find_elements(By.CLASS_NAME, "error-messages")
        assert error_elements == [] #오류 메시지 없음

    #게시 실패 시 페이지 이동 안 함, 오류 메시지 없음 확인
    def attempt_publish_and_verify_failure_on_editor(self):
        self.click_publish_article()
        time.sleep(1)
        assert "/editor" in self.driver.current_url
        self.verify_no_error_messages_present()

    #글로벌 피드 클릭
    def click_global_feed(self):
        self.click_button("//a[contains(@class, 'nav-link') and text()='Global Feed']")

    #게시글 수정 버튼이 보이는지 확인
    def is_edit_article_button_visible(self):
        try:
            self.driver.find_element(By.XPATH, "//a[contains(@class, 'btn-outline-secondary') and contains(@class, 'btn-sm') and normalize-space(.)='Edit Article']")
            return True
        except: # NoSuchElementException
            return False
        
    #게시글 삭제 버튼이 보이는지 확인 (게시글 상세 페이지에서)
    def is_delete_article_button_visible(self):
        try:
            self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn-outline-danger') and contains(@class, 'btn-sm') and contains(normalize-space(.), 'Delete Article')]")
            return True
        except: # NoSuchElementException
            return False
        
    #글로벌 피드에서 마지막 게시글 클릭
    def click_last_article_in_global_feed(self):
        #모든 게시글 미리보기 요소를 찾습니다. (article-list 내의 article-preview)
        article_previews = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='article-list']/div[@class='article-preview'] | //div[@class='article-preview'][not(ancestor::div[@class='article-list'])]"))
        ) #article-list가 있을 수도 있고 없을 수도 있는 경우 모두 고려
        if article_previews:
            last_article_preview = article_previews[-1]
            article_link_to_click = last_article_preview.find_element(By.XPATH, ".//a[contains(@class, 'preview-link')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", article_link_to_click) #스크롤
            time.sleep(0.5) #스크롤 후 잠시 대기
            article_link_to_click.click()
        else:
            raise Exception("글로벌 피드에 게시글이 없습니다.")

    #네비게이션 바에 있는 현재 로그인된 닉네임 가져옴 
    def get_current_logged_in_username_from_navbar(self):
        try:
            profile_link_element = self.wait.until(
                EC.visibility_of_element_located(self.NAVBAR_USER_PROFILE_LINK)
            )
            username = profile_link_element.text.strip()
            
            if username:
                return username
            else:
                # 텍스트가 비어있는 경우, href 속성에서 사용자 이름을 파싱 시도 (예: "/@username")
                href_value = profile_link_element.get_attribute("href")
                if href_value and href_value.startswith("/@"):
                    return href_value[2:] # "/@" 부분을 제외한 문자열 반환
                else:
                    print("오류: 사용자 이름 텍스트가 비어있고 href 속성이 예상 형식('/@username')이 아닙니다.")
                    return None
        except TimeoutException:
            print("오류: 네비게이션 바의 사용자 프로필 링크를 기다리는 중 시간 초과 발생.")
            return None
        except Exception as e: # NoSuchElementException 포함 가능
            print(f"네비게이션 바에서 사용자 이름을 가져오는 중 예기치 않은 오류 발생: {e}")
            return None
        
    #다른 사용자의 게시글 찾아서 클릭
    def find_and_click_other_user_article_in_global_feed(self, current_username, max_pages_to_check=10):
        #max_pages_to_check= ~ 페이지까지 찾음
        for page_attempt in range(max_pages_to_check):
            print(f"페이지 {page_attempt + 1}에서 다른 사용자 게시글 검색 중...")
            try:
                self.wait.until(EC.presence_of_element_located(self.ARTICLE_PREVIEWS_GLOBAL_FEED))
                articles = self.driver.find_elements(*self.ARTICLE_PREVIEWS_GLOBAL_FEED)
            except TimeoutException:
                print(f"페이지 {page_attempt + 1}에서 게시글을 로드하는 데 실패했거나 게시글이 없습니다.")
                return False #현재 페이지 또는 이전 페이지에서 게시글을 찾지 못함

            if not articles and page_attempt == 0: #첫 페이지부터 글이 없는 경우
                print("글로벌 피드에 게시글이 없습니다.")
                return False

            for article_preview_element in articles:
                try:
                    author_element = article_preview_element.find_element(*self.AUTHOR_LINK_IN_PREVIEW)
                    author_name = author_element.text.strip()

                    if author_name != current_username:
                        read_more_link = article_preview_element.find_element(*self.ARTICLE_READ_MORE_LINK_IN_PREVIEW)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", read_more_link)
                        time.sleep(0.3)
                        read_more_link.click()
                        print(f"'{author_name}' 사용자의 게시글을 클릭했습니다.")
                        return True #다른 사용자 게시글을 찾아 클릭 성공
                except Exception as e:
                    print(f"다른 사용자 게시글 찾는 중 개별 게시글 처리 오류: {e}")
                    continue

            #현재 페이지에서 다른 사용자의 글을 찾지 못했고, 마지막 시도가 아니면 다음 페이지로 이동
            if page_attempt < max_pages_to_check - 1:
                try:
                    pagination_ul = self.driver.find_element(*self.PAGINATION_UL)
                    all_page_list_items = pagination_ul.find_elements(By.CSS_SELECTOR, "li.page-item") # ul 내의 li.page-item

                    current_active_index = -1
                    for i, item in enumerate(all_page_list_items):
                        if "active" in item.get_attribute("class").split():
                            current_active_index = i
                            break
                    
                    if current_active_index != -1 and (current_active_index + 1) < len(all_page_list_items):
                        next_page_item = all_page_list_items[current_active_index + 1]
                        
                        if "disabled" in next_page_item.get_attribute("class").split():
                            print("다음 페이지 버튼이 비활성화되어 더 이상 진행할 수 없습니다.")
                            return False # 다음 페이지 없음

                        next_page_link = next_page_item.find_element(*self.PAGINATION_LINK_IN_ITEM)
                        print(f"다음 페이지({next_page_link.text.strip()})로 이동합니다...")
                        next_page_link.click()
                        time.sleep(0.5)
                    else:
                        print("더 이상 다음 페이지가 없습니다 (활성 페이지가 마지막이거나 다음 페이지 아이템 없음).")
                        return False #다음 페이지로 이동 불가
                except NoSuchElementException:
                    print("페이지네이션 UI(ul.pagination)를 찾을 수 없습니다. 현재 페이지만 검색된 것으로 간주합니다.")
                    return False #페이지네이션 UI 없음
            else:
                print(f"최대 {max_pages_to_check} 페이지까지 확인했지만, 다른 사용자의 게시글을 찾지 못했습니다.")
                return False #최대 페이지까지 확인 완료
        
        return False #모든 페이지 확인 후에도 찾지 못한 경우


#게시글 제목, 주제, 내용(현재 시각 기준 매초 고유 숫자로 내용 중복 피함)
def generate_unique_text(prefix="Test"):
    return f"{prefix} {int(time.time())}"