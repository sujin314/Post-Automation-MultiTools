import pytest
import os
from src.pages.postpage import PostPage, generate_unique_text
from src.utils.helpers import Utils # Utils 클래스를 import 합니다.
import urllib.parse
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

#     python -m pytest tests/test_postpage.py 

load_dotenv("src/config/.env")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

#1. 게시글 성공적 작성
def test_new_post_successful_creation(driver):
    my_util = Utils(driver)
    my_util.utils_login(EMAIL, PASSWORD) #로그인
    postpage = PostPage(driver)
    tags = "테스트"
    time.sleep(2)

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
    time.sleep(2) # 페이지 이동 및 로드 대기

    #작성 완료 확인
    assert "/article" in postpage.driver.current_url

#2. 게시글 공란으로 게시 시도
def test_publish_with_all_fields_blank(driver):
    my_util = Utils(driver) # driver fixture 사용
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(driver)
    time.sleep(2)
    postpage.go_to_editor_page() #새 글 작성 페이지로 이동
    #모든 필드가 비어있는 상태에서 게시 시도
    postpage.attempt_publish_and_verify_failure_on_editor()
    print("모든 필드 공란 시 게시 실패 확인 완료")

    #제목만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #제목 제외하고 나머지 필드 채우기
    postpage.enter_post_topic(generate_unique_text("주제만_있음"))
    postpage.enter_post_body(generate_unique_text("내용만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor() #작성 페이지에 그대로 남아있음
    print("제목 공란 시 게시 실패 확인 완료")

    #주제만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #주제 제외하고 나머지 필드 채우기
    postpage.enter_post_title(generate_unique_text("제목만_있음"))
    postpage.enter_post_body(generate_unique_text("내용만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor() #작성 페이지에 그대로 남아있음
    print("주제 공란 시 게시 실패 확인 완료")

    #본문만 공란으로 게시 시도
    postpage.go_to_editor_page()
    #본문 제외하고 나머지 필드 채우기
    postpage.enter_post_title(generate_unique_text("제목만_있음"))
    postpage.enter_post_topic(generate_unique_text("주제만_있음"))
    postpage.attempt_publish_and_verify_failure_on_editor() #작성 페이지에 그대로 남아있음
    print("본문 공란 시 게시 실패 확인 완료") # driver.quit() # fixture 사용으로 변경

#2. 내 프로필(작성 글 확인)
def test_profile(driver): # driver fixture 사용
    my_util = Utils(driver)
    my_util.utils_login(EMAIL, PASSWORD) 
    postpage = PostPage(driver)
    time.sleep(2)

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
    time.sleep(1)

    #홈에서 내 프로필 이동
    postpage.click_user_profile()
    time.sleep(1)

    #My Articles탭이 자동으로 선택되었는지 확인
    assert postpage.is_my_articles_tab_active(), "My Articles 탭이 활성화되지 않았습니다."

    #본인이 작성한 게시글을 목록으로 확인 (방금 작성한 게시글 확인)
    assert postpage.is_article_visible_in_profile(unique_title), f"'{unique_title}' 게시글이 프로필 목록에 없습니다."

    #글 상세보기 (방금 작성한 게시글 클릭)
    expected_article_url = postpage.get_article_link_href_in_profile(unique_title)
    assert expected_article_url is not None, f"'{unique_title}' 게시글의 링크를 프로필 목록에서 찾을 수 없습니다."

    postpage.click_article_in_profile_by_title(unique_title)
    time.sleep(1) # 페이지 로드 대기

    #현재 URL이 가져온 href 값과 일치하는지 확인
    assert driver.current_url == expected_article_url, \
        f"게시글 상세 페이지로 이동하지 못했습니다. 현재 URL: {driver.current_url}, 예상 URL: {expected_article_url}"

    #글 상세보기 페이지에서 본인 닉네임 클릭 시 내 프로필로 이동
    postpage.click_author_link_on_article_page(logged_in_username)
    time.sleep(1)
    expected_profile_path = f"/@{urllib.parse.quote(logged_in_username)}"
    assert expected_profile_path in driver.current_url, f"작성자 프로필 페이지로 이동하지 못했습니다. 예상 경로: {expected_profile_path}, 현재 URL: {driver.current_url}"

    # driver.quit() # conftest.py의 fixture에서 처리하므로 제거합니다.
#3. 게시글 수정
def test_edit_post(driver): # driver fixture 사용
    my_util = Utils(driver) # driver fixture 사용
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(driver)
    tags = "테스트"
    time.sleep(2)

    #새 게시글 작성
    postpage.go_to_editor_page()
    unique_title = generate_unique_text("수정테스트_제목")
    unique_topic = generate_unique_text("수정테스트_주제")
    unique_body = generate_unique_text("수정테스트_내용")

    postpage.enter_post_title(unique_title)
    postpage.enter_post_topic(unique_topic)
    postpage.enter_post_body(unique_body)
    postpage.click_publish_article()
    time.sleep(1)

    #Edit Article 버튼 클릭시 수정 화면으로 이동
    postpage.click_edit_article()
    time.sleep(1)

    #수정 페이지로 이동되었는지 확인
    assert "/editor" in postpage.driver.current_url

    #기존 제목, 주제, 내용 수정
    edited_title = generate_unique_text("수정완료_제목")
    edited_topic = generate_unique_text("수정완료_주제")
    edited_body = generate_unique_text("수정완료_내용입니다. 정말 수정되었습니다.")

    postpage.enter_post_tags(tags) # 태그 입력
    driver.find_element(By.CSS_SELECTOR, "i.ion-close-round").click() #태그 삭제

    postpage.enter_post_title(edited_title)
    postpage.enter_post_body(edited_body)
    time.sleep(1)

    #publish article 버튼 클릭 (수정 완료)
    postpage.click_publish_article()
    time.sleep(2)

    #수정된 게시글 상세 페이지로 이동되었는지 확인
    assert "/article/" in driver.current_url, "게시글 수정 후 상세 페이지로 이동하지 못했습니다."

    #수정된 제목과 내용이 잘 반영되었는지 확인
    actual_title_on_page = postpage.get_article_title_on_detail_page()
    actual_body_on_page = postpage.get_article_body_on_detail_page()

    assert actual_title_on_page == edited_title, f"수정된 제목이 일치하지 않습니다. 예상: '{edited_title}', 실제: '{actual_title_on_page}'"
    assert edited_body in actual_body_on_page, f"수정된 본문 내용이 포함되어 있지 않습니다. 예상 포함: '{edited_body}', 실제: '{actual_body_on_page}'"

    # driver.quit() # conftest.py의 fixture에서 처리하므로 제거합니다.
#4. 게시글 삭제
def test_delete_post(driver): # driver fixture 사용
    my_util = Utils(driver) # driver fixture 사용
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(driver)
    time.sleep(2)

    #새 게시글 작성
    postpage.go_to_editor_page()
    unique_title = generate_unique_text("삭제테스트_제목")
    unique_topic = generate_unique_text("삭제테스트_주제")
    unique_body = generate_unique_text("삭제테스트_내용")

    postpage.enter_post_title(unique_title)
    postpage.enter_post_topic(unique_topic)
    postpage.enter_post_body(unique_body)
    postpage.click_publish_article()
    time.sleep(1)

    #Delete Article버튼 클릭 (게시글 삭제)
    postpage.click_delete_article()
    time.sleep(2)

    #삭제 후 내 프로필로 이동
    postpage.click_user_profile()
    time.sleep(1)

    #My Articles 목록에서 방금 작성한 게시글이 더 이상 없는지 확인
    assert not postpage.is_article_visible_in_profile(unique_title), f"'{unique_title}' 게시글이 삭제되지 않음"

    # driver.quit() # conftest.py의 fixture에서 처리하므로 제거합니다.
#5. 타인의 게시글 수정/삭제 제한
def test_no_del_other_user_post(driver): # driver fixture 사용
    my_util = Utils(driver) # driver fixture 사용
    my_util.utils_login(EMAIL, PASSWORD)
    postpage = PostPage(driver)
    time.sleep(2)
    
    logged_in_username = postpage.get_current_logged_in_username_from_navbar()
    if not logged_in_username:
        pytest.fail("페이지에서 현재 로그인된 사용자 이름을 가져오는 데 실패")
   
    #글로벌 피드로 이동
    postpage.click_global_feed()
    time.sleep(1)

    #다른 사용자의 게시글을 찾아 클릭
    found_other_user_article = postpage.find_and_click_other_user_article_in_global_feed(logged_in_username)
    if not found_other_user_article:
        pytest.skip(f"글로벌 피드의 여러 페이지(최대 약 5페이지)에서 '{logged_in_username}' 사용자가 아닌 다른 사용자의 게시글을 찾을 수 없습니다.")
    time.sleep(2)
    
    #현재 URL이 게시글 상세 페이지인지 확인
    assert "/article/" in driver.current_url, "타인의 게시글 상세 페이지로 이동하지 못했습니다."

    #수정(Edit Article) 버튼이 없는지 확인
    assert not postpage.is_edit_article_button_visible(), "타인의 게시글에 'Edit Article' 버튼이 표시됩니다."
    
    #삭제(Delete Article) 버튼이 없는지 확인
    assert not postpage.is_delete_article_button_visible(), "타인의 게시글에 'Delete Article' 버튼이 표시됩니다."

    # driver.quit() # conftest.py의 fixture에서 처리하므로 제거합니다.