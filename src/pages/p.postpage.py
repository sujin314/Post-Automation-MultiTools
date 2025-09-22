from playwright.sync_api import Page, expect, Locator
import time
import re # 정규 표현식 사용을 위해 임포트

class PostPage:
        # Playwright 로케이터 (문자열)
    # NAVBAR_USER_PROFILE_LINK_CSS = "a.nav-link[href^='/@']" # 너무 일반적임
    # NAVBAR_USER_PROFILE_LINK_CSS = "ul.navbar-nav li.nav-item a.nav-link[href^='/@']:not(:has-text('My Articles')):not(:has-text('Favorited Articles')):not(:has-text('New Post')):not(:has-text('Settings'))" # 이전 시도
    NAVBAR_USER_PROFILE_LINK_CSS = "ul.navbar-nav li.nav-item a.nav-link[href^='/@']:has(img.user-pic)" # user-pic 클래스를 가진 img 태그를 포함하는 링크
    NEW_POST_LINK_XPATH = "//a[@href='/editor' and contains(., 'New Post')]" # 이 로케이터도 실제 HTML 확인 필요
    PUBLISH_ARTICLE_BUTTON_XPATH = "//button[contains(@class, 'btn-primary') and text()='Publish Article']"
    HOME_LINK_XPATH = "//a[contains(@class, 'nav-link') and text()='Home']"
    TITLE_INPUT_XPATH = "//input[@placeholder='Article Title']"
    TOPIC_INPUT_XPATH = "//input[@placeholder=\"What's this article about?\"]"
    BODY_TEXTAREA_XPATH = "//textarea[@placeholder='Write your article (in markdown)']"
    TAGS_INPUT_XPATH = "//input[@placeholder='Enter tags']"
    MY_ARTICLES_ACTIVE_TAB_XPATH = "//div[@class='articles-toggle']//ul[contains(@class, 'nav-pills')]/li/a[contains(text(), 'My Articles') and contains(@class, 'active')]"
    EDIT_ARTICLE_BUTTON_XPATH = "//a[contains(@class, 'btn-outline-secondary') and contains(@class, 'btn-sm') and normalize-space(.)='Edit Article']"
    DELETE_ARTICLE_BUTTON_XPATH = "//button[contains(@class, 'btn-outline-danger') and contains(@class, 'btn-sm') and contains(normalize-space(.), 'Delete Article')]"
    ARTICLE_TITLE_DETAIL_PAGE_XPATH = "//div[@class='banner']//h1"
    ARTICLE_BODY_DETAIL_PAGE_XPATH = "//div[contains(@class, 'article-content')]//div/p" # 좀 더 구체적인 선택자 필요할 수 있음
    ERROR_MESSAGES_CSS = ".error-messages"
    GLOBAL_FEED_LINK_XPATH = "//a[contains(@class, 'nav-link') and text()='Global Feed']"
    ARTICLE_PREVIEWS_GLOBAL_FEED_CSS = "div.article-preview"
    AUTHOR_LINK_IN_PREVIEW_CSS = "a.author"
    ARTICLE_READ_MORE_LINK_IN_PREVIEW_XPATH = ".//a[contains(@class, 'preview-link')]" # article_preview 요소 내부

    # 페이지네이션 관련 로케이터
    PAGINATION_UL_CSS = "ul.pagination"
    PAGINATION_LI_ITEM_CSS = "li.page-item" # ul.pagination 내부의 li.page-item
    PAGINATION_LINK_IN_ITEM_TAG = "a" # li.page-item 내부의 a 태그
    
    def __init__(self, page: Page):
        self.page = page
        # Playwright는 자동 대기 기능을 사용하므로 명시적인 WebDriverWait 객체는 필요 없음

    def click_button(self, xpath: str): # 이 메서드는 Playwright 스타일로 직접 호출하는 것이 더 나을 수 있음
        self.page.locator(f"xpath={xpath}").click()

    #newpost 버튼 클릭
    def click_newpost(self):
        self.page.locator(f"xpath={self.NEW_POST_LINK_XPATH}").click()

    #publish article 버튼 클릭
    def click_publish_article(self):
        self.page.locator(f"xpath={self.PUBLISH_ARTICLE_BUTTON_XPATH}").click()

    #home 버튼 클릭
    def click_home(self):
        self.page.locator(f"xpath={self.HOME_LINK_XPATH}").click()

    #게시글 작성 페이지
    def go_to_editor_page(self):
        self.page.goto("http://localhost:4100/editor")
        expect(self.page).to_have_url(re.compile(r"/editor"))

    #게시글 제목 입력
    def enter_post_title(self, text: str):
        locator = self.page.locator(f"xpath={self.TITLE_INPUT_XPATH}")
        locator.fill(text) # fill은 기존 내용을 지우고 입력

    #게시글 주제 입력
    def enter_post_topic(self, text: str):
        locator = self.page.locator(f"xpath={self.TOPIC_INPUT_XPATH}")
        locator.fill(text)

    #게시글 내용 입력
    def enter_post_body(self, text: str):
        locator = self.page.locator(f"xpath={self.BODY_TEXTAREA_XPATH}")
        locator.fill(text)

    #게시글 태그 입력
    def enter_post_tags(self, text: str):
        locator = self.page.locator(f"xpath={self.TAGS_INPUT_XPATH}")
        locator.fill(text)
        locator.press("Enter") # Keys.RETURN 대신 사용

    #네비게이션 바에 있는 현재 로그인된 사용자의 닉네임 클릭
    def click_user_profile(self):
        try:
            profile_link_locator = self.page.locator(self.NAVBAR_USER_PROFILE_LINK_CSS)
            # expect(profile_link_locator).to_be_clickable(timeout=10000) # 'to_be_clickable'은 없음
            expect(profile_link_locator).to_be_enabled(timeout=10000) # 클릭 가능한 상태(활성화)인지 확인
            profile_link_locator.click()
            print("네비게이션 바에서 현재 사용자 프로필 링크를 클릭했습니다.")
        except Exception as e: # Playwright는 TimeoutError를 발생시킴
            print(f"오류: 네비게이션 바에서 현재 사용자 프로필 링크({self.NAVBAR_USER_PROFILE_LINK_CSS})를 찾거나 클릭할 수 없습니다: {e}")
            raise

    #"My Articles" 탭이 활성화 확인
    def is_my_articles_tab_active(self) -> bool:
        return self.page.locator(f"xpath={self.MY_ARTICLES_ACTIVE_TAB_XPATH}").is_visible()

    #프로필 페이지에서 특정 제목의 게시글 존재 확인
    def is_article_visible_in_profile(self, title: str) -> bool:
        # XPath에서 문자열 비교 시 따옴표 문제 주의
        # f-string 내에서 변수를 사용할 때 적절히 이스케이프하거나, 다른 방식을 사용
        # 여기서는 text=title 옵션을 사용
        # article_preview_locator = self.page.locator("div.article-preview", has_text=title)
        # return article_preview_locator.locator("h1", text=title).is_visible()
        return self.page.locator(f"div.article-preview:has(h1:text-is(\"{title}\"))").is_visible()

    #프로필 페이지에서 특정 제목의 게시글 클릭
    def click_article_in_profile_by_title(self, title: str):
        # 좀 더 견고한 로케이터: 제목을 포함하는 article-preview 내의 preview-link 클릭
        article_preview_locator = self.page.locator("div.article-preview", has_text=title)
        preview_link_locator = article_preview_locator.locator("a.preview-link")
        preview_link_locator.click()

    #게시글 상세 페이지에서 작성자 프로필 링크 클릭 (사용자 이름 기반)
    def click_author_link_on_article_page(self, username: str):
        # XPath에서 normalize-space()를 사용하여 공백 문제를 처리할 수 있습니다.
        author_link_locator = self.page.locator(f"xpath=//div[contains(@class, 'article-meta')]//a[contains(@href, '/@{username}') and normalize-space()='{username}']")
        author_link_locator.click()

    #프로필 페이지에서 특정 제목의 게시글 링크(href) 가져오기
    def get_article_link_href_in_profile(self, title: str) -> str | None:
        article_preview_locator = self.page.locator("div.article-preview", has_text=title)
        preview_link_locator = article_preview_locator.locator("a.preview-link")
        if preview_link_locator.is_visible():
            return preview_link_locator.get_attribute('href')
        return None
    
    #게시글 수정 버튼 클릭
    def click_edit_article(self):
        self.page.locator(f"xpath={self.EDIT_ARTICLE_BUTTON_XPATH}").click()

    #게시글 삭제 버튼 클릭
    def click_delete_article(self):
        self.page.locator(f"xpath={self.DELETE_ARTICLE_BUTTON_XPATH}").click()

    #게시글 상세 페이지에서 제목 가져오기
    def get_article_title_on_detail_page(self) -> str | None:
        locator = self.page.locator(f"xpath={self.ARTICLE_TITLE_DETAIL_PAGE_XPATH}")
        if locator.is_visible():
            return locator.inner_text()
        return None

    #게시글 상세 페이지에서 본문 내용 가져오기
    def get_article_body_on_detail_page(self) -> str | None:
        locator = self.page.locator(f"xpath={self.ARTICLE_BODY_DETAIL_PAGE_XPATH}")
        # 여러 <p> 태그가 있을 수 있으므로, 모든 텍스트를 합치거나 첫 번째 <p>만 가져올 수 있음
        # 여기서는 첫 번째 <p> 태그의 텍스트를 가져오는 것으로 가정
        if locator.first.is_visible(): # first를 사용하여 여러 개 중 첫 번째 요소 확인
            return locator.first.inner_text()
        return None

    def verify_no_error_messages_present(self):
        expect(self.page.locator(self.ERROR_MESSAGES_CSS)).not_to_be_visible()


    #게시 실패 시 페이지 이동 안 함, 오류 메시지 없음 확인
    def attempt_publish_and_verify_failure_on_editor(self):
        self.click_publish_article()
        expect(self.page).to_have_url(re.compile(r"/editor"), timeout=3000) # 짧은 시간 내 URL 변경 없는지
        self.verify_no_error_messages_present()

    #글로벌 피드 클릭
    def click_global_feed(self):
        self.page.locator(f"xpath={self.GLOBAL_FEED_LINK_XPATH}").click()

    #게시글 수정 버튼이 보이는지 확인
    def is_edit_article_button_visible(self) -> bool:
        # is_visible은 요소가 없으면 False를 반환 (TimeoutError 발생 안 함, 기본 타임아웃 내)
        return self.page.locator(f"xpath={self.EDIT_ARTICLE_BUTTON_XPATH}").is_visible(timeout=1000) # 짧은 타임아웃
        
    #게시글 삭제 버튼이 보이는지 확인 (게시글 상세 페이지에서)
    def is_delete_article_button_visible(self) -> bool:
        return self.page.locator(f"xpath={self.DELETE_ARTICLE_BUTTON_XPATH}").is_visible(timeout=1000)
        
        
    #글로벌 피드에서 마지막 게시글 클릭
    def click_last_article_in_global_feed(self):
        # 모든 게시글 미리보기 요소를 찾습니다.
        # article_list_xpath = "//div[@class='article-list']/div[@class='article-preview'] | //div[@class='article-preview'][not(ancestor::div[@class='article-list'])]"
        # article_previews_locator = self.page.locator(f"xpath={article_list_xpath}")
        article_previews_locator = self.page.locator(self.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS)
        
        count = article_previews_locator.count()
        if count > 0:
            last_article_preview_locator = article_previews_locator.nth(count - 1) # 마지막 요소
            article_link_to_click = last_article_preview_locator.locator(f"xpath={self.ARTICLE_READ_MORE_LINK_IN_PREVIEW_XPATH}")
            article_link_to_click.scroll_into_view_if_needed()
            # time.sleep(0.5) # Playwright는 스크롤 후 바로 클릭 가능
            article_link_to_click.click()
        else:
            raise Exception("글로벌 피드에 게시글이 없습니다.")

    #네비게이션 바에 있는 현재 로그인된 닉네임 가져옴 
    def get_current_logged_in_username_from_navbar(self) -> str | None:
        profile_link_locator = self.page.locator(self.NAVBAR_USER_PROFILE_LINK_CSS)
        try:
            # 로케이터가 정확히 하나의 요소를 찾는지 확인
            count = profile_link_locator.count()
            if count == 0:
                print(f"오류: 네비게이션 바에서 사용자 프로필 링크({self.NAVBAR_USER_PROFILE_LINK_CSS})를 찾을 수 없습니다.")
                return None
            if count > 1:
                print(f"경고: 네비게이션 바에서 사용자 프로필 링크({self.NAVBAR_USER_PROFILE_LINK_CSS})가 {count}개 발견되었습니다. 첫 번째 요소를 사용합니다.")
            
            # 첫 번째 요소를 대상으로 작업 (로케이터가 정확하다면 항상 하나만 찾아야 함)
            target_link = profile_link_locator.first
            if not target_link.is_visible(timeout=5000):
                 print("오류: 네비게이션 바의 사용자 프로필 링크가 보이지 않습니다.")
                 return None

            # <img> 태그를 포함하므로, <a> 태그의 전체 텍스트에서 <img> 태그의 alt 텍스트를 제외하거나,
            # <a> 태그의 텍스트 노드만 가져와야 합니다.
            # 여기서는 href에서 사용자 이름을 추출하는 것이 더 안정적일 수 있습니다.
            href_value = target_link.get_attribute("href")
            if href_value and href_value.startswith("/@"):
                if href_value and href_value.startswith("/@"):
                    return href_value[2:] # "/@" 부분을 제외한 문자열 반환
            
            # href에서 추출 실패 시, 텍스트에서 추출 시도 (img 태그 제외)
            # JavaScript를 사용하여 텍스트 노드만 가져오는 방법:
            username_text = target_link.evaluate("node => node.cloneNode(true).childNodes[1] ? node.cloneNode(true).childNodes[1].textContent.trim() : node.textContent.trim()")
            if username_text: # <img> 다음의 텍스트 노드가 사용자 이름이라고 가정
                return username_text
            
            print(f"오류: 사용자 프로필 링크에서 사용자 이름을 추출하지 못했습니다. Href: {href_value}, Text: {target_link.inner_text().strip()}")
            return None
        except Exception as e: # NoSuchElementException 포함 가능
            print(f"네비게이션 바에서 사용자 이름을 가져오는 중 예기치 않은 오류 발생: {e}")
            return None
        
    #다른 사용자의 게시글 찾아서 클릭
    def find_and_click_other_user_article_in_global_feed(self, current_username: str, max_pages_to_check: int = 5) -> bool:
        #max_pages_to_check= ~ 페이지까지 찾음
        for page_attempt in range(max_pages_to_check):
            print(f"페이지 {page_attempt + 1}에서 다른 사용자 게시글 검색 중...")
            try:
                # 페이지 로드 대기 (예: 첫 번째 게시글 미리보기가 나타날 때까지)
                expect(self.page.locator(self.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS).first).to_be_visible(timeout=10000)
                articles_locators = self.page.locator(self.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS).all()
            except Exception: # Playwright TimeoutError 등
                print(f"페이지 {page_attempt + 1}에서 게시글을 로드하는 데 실패했거나 게시글이 없습니다.")
                return False #현재 페이지 또는 이전 페이지에서 게시글을 찾지 못함
      
            if not articles_locators and page_attempt == 0: #첫 페이지부터 글이 없는 경우
                print("글로벌 피드에 게시글이 없습니다.")
                return False

            for article_preview_locator in articles_locators:
                try:
                    author_locator = article_preview_locator.locator(self.AUTHOR_LINK_IN_PREVIEW_CSS)
                    author_name = author_locator.inner_text().strip()

                    if author_name != current_username:
                        read_more_locator = article_preview_locator.locator(f"xpath={self.ARTICLE_READ_MORE_LINK_IN_PREVIEW_XPATH}")
                        read_more_locator.scroll_into_view_if_needed()
                        read_more_locator.click()
                        print(f"'{author_name}' 사용자의 게시글을 클릭했습니다.")
                        return True #다른 사용자 게시글을 찾아 클릭 성공
                except Exception as e:
                    print(f"다른 사용자 게시글 찾는 중 개별 게시글 처리 오류: {e}")
                    continue

            #현재 페이지에서 다른 사용자의 글을 찾지 못했고, 마지막 시도가 아니면 다음 페이지로 이동
            if page_attempt < max_pages_to_check - 1:
                try:
                    pagination_ul_locator = self.page.locator(self.PAGINATION_UL_CSS)
                    all_page_list_items_locators = pagination_ul_locator.locator(self.PAGINATION_LI_ITEM_CSS).all()

                    current_active_index = -1
                    for i, item_locator in enumerate(all_page_list_items_locators):
                        if "active" in (item_locator.get_attribute("class") or "").split():
                            current_active_index = i
                            break
                    
                    if current_active_index != -1 and (current_active_index + 1) < len(all_page_list_items_locators):
                        next_page_item_locator = all_page_list_items_locators[current_active_index + 1]
                        
                        if "disabled" in (next_page_item_locator.get_attribute("class") or "").split():
                            print("다음 페이지 버튼이 비활성화되어 더 이상 진행할 수 없습니다.")
                            return False # 다음 페이지 없음

                        next_page_link_locator = next_page_item_locator.locator(self.PAGINATION_LINK_IN_ITEM_TAG)
                        print(f"다음 페이지({next_page_link_locator.inner_text().strip()})로 이동합니다...")
                        next_page_link_locator.click()
                        self.page.wait_for_load_state("networkidle", timeout=10000) # 페이지 로드 대기
                    else:
                        print("더 이상 다음 페이지가 없습니다 (활성 페이지가 마지막이거나 다음 페이지 아이템 없음).")
                        return False #다음 페이지로 이동 불가
                except Exception: 
                    print("페이지네이션 UI(ul.pagination)를 찾을 수 없습니다. 현재 페이지만 검색된 것으로 간주합니다.")
                    return False #페이지네이션 UI 없음
            else:
                print(f"최대 {max_pages_to_check} 페이지까지 확인했지만, 다른 사용자의 게시글을 찾지 못했습니다.")
                return False #최대 페이지까지 확인 완료
        
        return False #모든 페이지 확인 후에도 찾지 못한 경우


#게시글 제목, 주제, 내용(현재 시각 기준 매초 고유 숫자로 내용 중복 피함)
def generate_unique_text(prefix="Test"):
    return f"{prefix} {int(time.time())}"