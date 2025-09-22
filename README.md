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
```bash
- **대상 서비스:** RealWorld (Conduit) - https://demo.realworld.io
- **프론트엔드:** React + Redux
  - https://github.com/gothinkster/react-redux-realworld-example-app
- **백엔드:** Node.js + Express
  - https://github.com/gothinkster/node-express-realworld-example-app
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
```bash
#첫 번째 후기의 내용 가져오기
first_review = review[0].get_attribute("innerHTML")
assert "혼밥" in first_review, "❌ 후기가 정상적으로 작성되지 않았습니다."
print("✅ 후기가 정상적으로 작성되었습니다.")
time.sleep(1)
```
