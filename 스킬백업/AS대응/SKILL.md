---
name: AS대응
description: >
  방수/바닥 하자 AS 대응 프로세스 관리 스킬.
  AS 접수, 현장 방문, 시공일지, 완료검사 등 AS 전 과정을 웹 UI로 관리하고
  구글드라이브에 자동 백업한다.
  "AS대응", "AS처리", "하자처리", "방수AS", "AS접수", "AS관리" 등의
  표현이 나오면 트리거한다.
---

# AS 대응 프로세스 스킬

## 역할

방수/바닥 공사 하자 AS를 체계적으로 접수·처리·관리하는 스킬.
웹 UI에서 케이스를 생성하고, 구글드라이브에 자동 백업한다.

## 핵심 경로

| 구분 | 경로 |
|------|------|
| **프로젝트 폴더** | `G:\내 드라이브\클로드작업기록\이메일발송\waterproof-as-sync\` |
| **메인 서버** | `app.py` (Flask, http://localhost:5000) |
| **웹 UI** | `waterproofing_as_v3_optionA.html` |
| **엑셀 생성** | `create_excel.py` |
| **캘린더 연동** | `as_calendar.py` |

## 실행 모드

### 1. AS 웹 UI 실행 - "AS대응해줘" / "AS시스템 열어줘"
```bash
cd "G:\내 드라이브\클로드작업기록\이메일발송\waterproof-as-sync"
python app.py
```
서버 실행 후 브라우저에서 `waterproofing_as_v3_optionA.html` 열기

### 2. AS 현황 조회 - "AS 현황 보여줘" / "AS 목록"
Flask 서버가 실행 중이면:
```bash
curl http://localhost:5000/api/list-sites
```

### 3. 엑셀 양식 생성 - "AS 엑셀 만들어줘"
```bash
python create_excel.py
```

## AS 처리 단계

1. **AS 접수** - 현장명, 고객 연락처, 하자 내용 입력
2. **현장 방문** - 방문 일정, 담당자, 사진 첨부
3. **시공일지** - 작업 내용, 사용 자재, 인원
4. **완료검사** - 검사 결과, 고객 서명
5. **구글드라이브 백업** - 자동 저장

## Python 경로

```
export PATH="/c/Users/CEO/AppData/Local/Programs/Python/Python312:/c/Users/CEO/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
```

## 필요 패키지 설치

```bash
pip install flask flask-cors python-dotenv google-auth google-auth-oauthlib google-api-python-client openpyxl
```

## 주의사항

- 최초 실행 시 구글 OAuth 인증 필요 (브라우저에서 1회)
- `.env` 파일에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 필요
- 서버가 이미 실행 중이면 재시작 불필요
