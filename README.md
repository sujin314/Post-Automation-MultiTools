# 다중 자동화 도구 적용 웹 테스트 – RealWorld QA 자동화 프로젝트

## 1. 프로젝트 개요
- RealWorld 애플리케이션을 대상으로 테스트 자동화를 수행하는 QA 프로젝트입니다. 
- 해당 애플리케이션은 Medium.com의 클론 형태로, 실제 웹 애플리케이션 개발과 QA 테스트 전략 수립에 필요한 지식을 실습하기 위한 목적으로 사용됩니다. 

---

## 2. 프로젝트 구조
```bash
├── src/                        
|   ├── pages/                   # 기능별 페이지 객체 (현재: 게시글)  
|   |   ├── *.py          
|   |   ├── p.*.py               # Playwright 전용 페이지 객체
|   ├── utils/                   # 팀 공용 유틸 함수(로그인 등)  
|   |   ├── *.py                
|   |   ├── p.*.py               # Playwright 전용 유틸  
├── tests/                       # 자동화 테스트 코드 (Selenium + Pytest) 
|   ├── robot_tests/             # Robot Framework 기반 테스트  
|   ├── playwright_tests/        # Playwright 기반 테스트  
|   ├── selenium_tests/          # Selenium 기반 테스트 
├── .gitignore                   # 환경파일 및 캐시 제외
└── README.md
```

---

## 3. 설치, 실행 방법

본 프로젝트는 **RealWorld Demo 서버 (Conduit)** 를 대상으로 자동화 테스트를 수행하도록 설계되었습니다.  
별도의 프론트엔드/백엔드 실행 환경을 포함하지 않고, 외부 제공되는 데모 서버에 테스트를 수행합니다.

- **테스트 대상 서비스:** [RealWorld Demo (Conduit)](https://demo.realworld.io)
- **참고 레퍼런스**
-    Frontend: [react-redux-realworld-example-app](https://github.com/gothinkster/react-redux-realworld-example-app)
-    Backend: [node-express-realworld-example-app](https://github.com/gothinkster/node-express-realworld-example-app)

### 로컬 실행 방법
1. Python 환경 준비
   ```bash
   pip install selenium pytest
   ```
2. 원하는 테스트 프레임워크 선택 후 실행
   #### Selenuim (Pytest)
   ```bash
   pytest tests/selenium_tests/ -v
   ```
   #### Robot Framework
   ```bash
   robot tests/robot_tests/
   ```
   #### Playwright
   ```bash
   pytest tests/playwright_tests/ -v
   ```

---

## 4. 테스트 전략 요약
| 구분 | 내용 |
| --- | --- |
| 테스트 범위 | 게시글 작성, 수정 및 삭제, 권한 확인 |
| 자동화 비율 | 11개 중 11개 자동화 (**100%**) |
| 핵심 사용자 플로우 | 게시글 작성 → 조회 → 수정 → 삭제 → 권한 확인 |

---

## 5. 예시 테스트 코드
#### Selenium (Pytest)
```bash
#현재 URL이 게시글 상세 페이지인지 확인
assert "/article/" in driver.current_url, "타인의 게시글 상세 페이지로 이동하지 못했습니다."

#수정(Edit Article) 버튼이 없는지 확인
assert not postpage.is_edit_article_button_visible(), "타인의 게시글에 'Edit Article' 버튼이 표시됩니다."
    
#삭제(Delete Article) 버튼이 없는지 확인
assert not postpage.is_delete_article_button_visible(), "타인의 게시글에 'Delete Article' 버튼이 표시됩니다."
```
#### Robot Framework
```bash
타인의 게시글 수정/삭제 제한
    [Documentation]    타인의 게시글을 수정/삭제할 수 없는지 확인합니다.
    웹사이트 접속 및 로그인
    글로벌 피드로 이동
    다른 사용자의 게시글 찾아서 클릭
    게시글 상세 화면에서 수정/삭제 버튼이 없는지 확인
    [Teardown]    Close Browser
```
#### Playwright
```bash
    #현재 URL이 게시글 상세 페이지인지 확인
    expect(page).to_have_url(re.compile(r"/article/"))

    #수정(Edit Article) 버튼이 없는지 확인
    assert not postpage.is_edit_article_button_visible(), "타인의 게시글에 'Edit Article' 버튼이 표시됩니다."
    
    #삭제(Delete Article) 버튼이 없는지 확인
    assert not postpage.is_delete_article_button_visible(), "타인의 게시글에 'Delete Article' 버튼이 표시됩니다."
```

