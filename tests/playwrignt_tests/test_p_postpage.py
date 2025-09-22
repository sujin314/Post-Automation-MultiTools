import pytest
import os
from playwright.sync_api import Page, expect # Playwright의 Page, expect 사용
from src.utils.helpers import Utils
from src.pages.postpage import PostPage, generate_unique_text # PostPage도 Playwright에 맞게 수정 필요
import re # 정규 표현식 사용을 위해 임포트
import urllib.parse
from dotenv import load_dotenv

#     python -m pytest tests/test_postpage.py 

load_dotenv("src/config/.env")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

#1. 게시글 성공적 작성
def test_new_post_successful_creation(page: Page): # driver 대신 page: Page 사용
    my_util = Utils(page) # Utils에 page 객체 전달
    my_util.utils_login(EMAIL, PASSWORD) #로그인
    postpage = PostPage(page) # PostPage에 page 객체 전달
    tags = "테스트"
    page.wait_for_load_state("networkidle") # 네트워크 안정화 대기

    # 글 작성 페이지로 이동
    postpage.go_to_editor_page()

    #내용 입력
    title = generate_unique_text("작성테스트_제목")
    topic = generate_unique_text("작성테스트_주제")
    body = generate_unique_text("작성테스트_내용")

    postpage.enter_post_title(title)
    postpage.enter_post_topic(topic)
    postpage.enter_post_body(body)
    postpage.enter_post_tags(tags)

    #publish article 클릭
    postpage.click_publish_article()
    page.wait_for_load_state("domcontentloaded") # DOM 로드 대기

    #작성 완료 확인
    # assert "/article" in page.url # 직접 page.url 사용 가능
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # URL에 "/article/" 포함 확인
    # driver.quit() # Playwright가 자동으로 브라우저 종료

#2. 게시글 공란으로 게시 시도
def test_publish_with_all_fields_blank(page: Page):
    my_util = Utils(page)
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(page)
    page.wait_for_load_state("networkidle") # 예: 네트워크가 안정될 때까지 대기
    postpage.go_to_editor_page() #새 글 작성 페이지로 이동
    #모든 필드가 비어있는 상태에서 게시 시도
    postpage.attempt_publish_and_verify_failure_on_editor()
    print("모든 필드 공란 시 게시 실패 확인 완료")

    #제목만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #제목 제외하고 나머지 필드 채우기
    postpage.enter_post_topic(generate_unique_text("주제만_있음"))
    postpage.enter_post_body(generate_unique_text("내용만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor()
    print("제목 공란 시 게시 실패 확인 완료")

    #주제만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #주제 제외하고 나머지 필드 채우기
    postpage.enter_post_title(generate_unique_text("제목만_있음"))
    postpage.enter_post_body(generate_unique_text("내용만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor()
    print("주제 공란 시 게시 실패 확인 완료")

    #본문만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #본문 제외하고 나머지 필드 채우기
    postpage.enter_post_title(generate_unique_text("제목만_있음"))
    postpage.enter_post_topic(generate_unique_text("주제만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor()
    print("본문 공란 시 게시 실패 확인 완료")

#3. 내 프로필(작성 글 확인)
def test_profile(page: Page):
    # driver = webdriver.Chrome() # 이 줄은 반드시 제거! page fixture를 사용합니다.
    my_util = Utils(page)
    my_util.utils_login(EMAIL, PASSWORD) 
    postpage = PostPage(page)
    page.wait_for_load_state("networkidle")

    # 네비게이션 바에서 현재 로그인된 사용자의 이름을 가져옵니다.
    logged_in_username = postpage.get_current_logged_in_username_from_navbar()
    if not logged_in_username:
        pytest.fail("페이지에서 현재 로그인된 사용자 이름을 가져오는 데 실패")

    #테스트를 위해 새 게시글 작성
    postpage.go_to_editor_page()
    unique_title = generate_unique_text("프로필테스트_제목")
    unique_topic = generate_unique_text("프로필테스트_주제")
    unique_body = generate_unique_text("프로필테스트_내용")

    postpage.enter_post_title(unique_title)
    postpage.enter_post_topic(unique_topic)
    postpage.enter_post_body(unique_body)
    postpage.click_publish_article()
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # 게시글 상세 페이지로 이동 확인

    #홈에서 내 프로필 이동
    postpage.click_user_profile()
    expected_profile_url_regex_profile_test = re.compile(f".*/@{re.escape(urllib.parse.quote(logged_in_username))}")
    expect(page).to_have_url(expected_profile_url_regex_profile_test, timeout=10000) # 프로필 페이지 이동 확인

       # 프로필 페이지의 게시글 목록이 로드될 때까지 대기 (예: 첫 번째 article-preview 요소가 나타날 때까지)
       # PostPage에 article-preview 로케이터가 정의되어 있다면 그것을 사용하는 것이 좋음
       # 여기서는 PostPage.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS를 임시로 사용 (프로필 페이지용 로케이터가 있다면 그것으로 변경)
    expect(page.locator(postpage.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS).first).to_be_visible(timeout=10000)

    #My Articles탭이 자동으로 선택되었는지 확인
    assert postpage.is_my_articles_tab_active(), "My Articles 탭이 활성화되지 않았습니다."
    #본인이 작성한 게시글을 목록으로 확인 (방금 작성한 게시글 확인)
    page.wait_for_timeout(1000) # DOM 안정화를 위한 짧은 대기 (필요에 따라 조절)
    assert postpage.is_article_visible_in_profile(unique_title), f"'{unique_title}' 게시글이 프로필 목록에 없습니다."

    #글 상세보기 (방금 작성한 게시글 클릭)
    expected_article_url = postpage.get_article_link_href_in_profile(unique_title)
    assert expected_article_url is not None, f"'{unique_title}' 게시글의 링크를 프로필 목록에서 찾을 수 없습니다."

    postpage.click_article_in_profile_by_title(unique_title)
    # URL이 동적으로 바뀌므로, 단순히 /article/ 경로를 포함하는지만 확인
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000)

    #현재 URL이 가져온 href 값과 일치하는지 확인
    expect(page).to_have_url(re.compile(r"/article/"))

    #글 상세보기 페이지에서 본인 닉네임 클릭 시 내 프로필로 이동
    postpage.click_author_link_on_article_page(logged_in_username)
    expected_profile_path_regex = re.compile(f".*/@{re.escape(urllib.parse.quote(logged_in_username))}")
    expect(page).to_have_url(expected_profile_path_regex)

#4. 게시글 수정
def test_edit_post(page: Page):
    my_util = Utils(page)
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(page)
    page.wait_for_load_state("networkidle")

    #새 게시글 작성
    postpage.go_to_editor_page()
    unique_title = generate_unique_text("수정테스트_제목")
    unique_topic = generate_unique_text("수정테스트_주제")
    unique_body = generate_unique_text("수정테스트_내용")

    postpage.enter_post_title(unique_title)
    postpage.enter_post_topic(unique_topic)
    postpage.enter_post_body(unique_body)
    postpage.click_publish_article()
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # 게시글 상세 페이지로 이동 확인

    #Edit Article 버튼 클릭시 수정 화면으로 이동
    postpage.click_edit_article()
    expect(page).to_have_url(re.compile(r"/editor/"), timeout=10000) # 에디터 페이지 이동 확인

    #수정 페이지로 이동되었는지 확인
    expect(page).to_have_url(re.compile(r"/editor"))

    #기존 제목, 주제, 내용 수정
    edited_title = generate_unique_text("수정완료_제목")
    edited_topic = generate_unique_text("수정완료_주제")
    edited_body = generate_unique_text("수정완료_내용입니다. 정말 수정되었습니다.")

    postpage.enter_post_title(edited_title)
    postpage.enter_post_body(edited_body)

    #publish article 버튼 클릭 (수정 완료)
    postpage.click_publish_article()
    # 수정 후에는 새로운 URL로 이동하므로, 해당 URL을 직접 확인하거나,
    # 수정된 제목으로 게시글을 다시 찾아 그 링크로 검증합니다.
    # 여기서는 단순히 /article/ 경로로 이동했는지 먼저 확인하고,
    # 그 다음 페이지 내용(제목)이 수정된 내용과 일치하는지 확인하는 것이 더 안정적일 수 있습니다.
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # 수정된 게시글 상세 페이지로 이동했는지 (경로 일부만 확인)
    # edited_title_slug = re.escape(edited_title.split(" ")[0].lower()) # 실제 URL 생성 규칙에 따라 슬러그 생성 방식 확인 필요
    # expect(page).to_have_url(re.compile(f"/article/.*{edited_title_slug}"), timeout=10000) # 수정된 게시글 페이지로 이동 확인

    #수정된 게시글 상세 페이지로 이동되었는지 확인
    expect(page).to_have_url(re.compile(r"/article/"))

    #수정된 제목과 내용이 잘 반영되었는지 확인
    actual_title_on_page = postpage.get_article_title_on_detail_page()
    actual_body_on_page = postpage.get_article_body_on_detail_page()

    assert actual_title_on_page == edited_title, f"수정된 제목이 일치하지 않습니다. 예상: '{edited_title}', 실제: '{actual_title_on_page}'"
    # expect(actual_body_on_page).to_contain_text(edited_body) # 문자열에 직접 expect 사용 불가
    assert edited_body in actual_body_on_page, f"수정된 본문 내용 '{edited_body}'가 실제 내용 '{actual_body_on_page}'에 포함되어 있지 않습니다."

#5. 게시글 삭제
def test_delete_post(page: Page):
    my_util = Utils(page)
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(page)
    page.wait_for_load_state("networkidle")

    #새 게시글 작성
    postpage.go_to_editor_page()
    unique_title = generate_unique_text("삭제테스트_제목")
    unique_topic = generate_unique_text("삭제테스트_주제")
    unique_body = generate_unique_text("삭제테스트_내용")

    postpage.enter_post_title(unique_title)
    postpage.enter_post_topic(unique_topic)
    postpage.enter_post_body(unique_body)
    postpage.click_publish_article()
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # 게시글 상세 페이지로 이동 확인

    #Delete Article버튼 클릭 (게시글 삭제)
    postpage.click_delete_article()
    # 삭제 후에는 해당 게시글의 URL로 접근할 수 없어야 함.
    # unique_title_slug = re.escape(unique_title.split(" ")[0].lower()) # 실제 URL 생성 규칙에 따라
    # expect(page).not_to_have_url(re.compile(f"/article/.*{unique_title_slug}"), timeout=10000) # 삭제된 게시글 URL이 아닌지 확인
    # 또는 삭제 후 리디렉션되는 페이지 (예: 홈페이지)를 확인
    expect(page).to_have_url(re.compile(r"http://localhost:4100/$"), timeout=10000) # 예: 홈페이지로 이동했는지

    #삭제 후 내 프로필로 이동
    postpage.click_user_profile()
    # 삭제 후 프로필로 이동했을 때의 URL 확인 (logged_in_username을 다시 가져오거나, my_util을 통해 현재 사용자 이름 확인)
    current_user_after_delete = postpage.get_current_logged_in_username_from_navbar() # 삭제 후에도 동일한 사용자인지 확인
    if current_user_after_delete: # 사용자가 여전히 로그인 상태라면
        expected_profile_url_regex_delete_test = re.compile(f".*/@{re.escape(urllib.parse.quote(current_user_after_delete))}")
        expect(page).to_have_url(expected_profile_url_regex_delete_test, timeout=10000)

    #My Articles 목록에서 방금 작성한 게시글이 더 이상 없는지 확인
    assert not postpage.is_article_visible_in_profile(unique_title), f"'{unique_title}' 게시글이 삭제되지 않음"

#6. 타인의 게시글 수정/삭제 제한
def test_no_del_other_user_post(page: Page):
    my_util = Utils(page)
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(page)
    page.wait_for_load_state("networkidle")
    
    logged_in_username = postpage.get_current_logged_in_username_from_navbar()
    if not logged_in_username:
        pytest.fail("페이지에서 현재 로그인된 사용자 이름을 가져오는 데 실패")
   
    #글로벌 피드로 이동
    postpage.click_global_feed()
    expect(page.locator(postpage.ARTICLE_PREVIEWS_GLOBAL_FEED_CSS).first).to_be_visible(timeout=10000) # 글로벌 피드 로드 확인

    #다른 사용자의 게시글을 찾아 클릭
    found_other_user_article = postpage.find_and_click_other_user_article_in_global_feed(logged_in_username)
    if not found_other_user_article:
        pytest.skip(f"글로벌 피드의 여러 페이지(최대 약 5페이지)에서 '{logged_in_username}' 사용자가 아닌 다른 사용자의 게시글을 찾을 수 없습니다.")
    expect(page).to_have_url(re.compile(r"/article/"), timeout=10000) # 게시글 상세 페이지로 이동 확인
    
    #현재 URL이 게시글 상세 페이지인지 확인
    expect(page).to_have_url(re.compile(r"/article/"))

    #수정(Edit Article) 버튼이 없는지 확인
    assert not postpage.is_edit_article_button_visible(), "타인의 게시글에 'Edit Article' 버튼이 표시됩니다."
    
    #삭제(Delete Article) 버튼이 없는지 확인
    assert not postpage.is_delete_article_button_visible(), "타인의 게시글에 'Delete Article' 버튼이 표시됩니다."

    #명령어
    #얼루어 결과 저장하기:
    #python -m pytest tests/test_postpage.py --browser chromium --alluredir=allure-results/chromium

    #싱글 레포트 생성:
    #allure generate "얼루어 결과 저장되어있는 위치" --single-file -o "레포트 저장할위치"

    #트레이스 생성(zip 파일):
    #python -m pytest "test_postpage.py위치" --browser=firefox --tracing=on

    #트레이스 뷰어 열기
    #playwright show-trace "trace.zip 파일이 있는 위치\trace.zip"