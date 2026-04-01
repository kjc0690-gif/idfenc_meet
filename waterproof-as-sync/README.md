# 방수명장 AS 시스템 - 구글드라이브 자동 백업

AS 관리 시스템의 데이터를 구글드라이브에 자동 백업하는 Flask API 서버.

## 시작하기

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Google Cloud 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성: `방수명장-AS-백업`
3. **API 라이브러리** → `Google Drive API` 사용 설정
4. **사용자 인증 정보** → OAuth 클라이언트 ID 생성
   - 유형: **웹 애플리케이션**
   - 리디렉션 URI: `http://localhost:5000/oauth2callback`
5. 클라이언트 ID와 Secret 복사

### 3. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열고 아래 값을 입력:

```
GOOGLE_CLIENT_ID=복사한_클라이언트_ID
GOOGLE_CLIENT_SECRET=복사한_시크릿
```

### 4. 서버 실행

```bash
python app.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 5. 구글 인증 (최초 1회)

1. 브라우저에서 http://localhost:5000 접속
2. `/api/auth` 링크 클릭
3. 구글 계정 로그인 및 권한 승인
4. "인증 완료!" 메시지 확인

## API 목록

| 엔드포인트 | 메서드 | 설명 |
|---|---|---|
| `/api/status` | GET | 인증 상태 확인 |
| `/api/auth` | GET | OAuth 인증 URL 생성 |
| `/oauth2callback` | GET | OAuth 콜백 (자동) |
| `/api/backup` | POST | AS 데이터 백업 |
| `/api/list-sites` | GET | 현장 목록 조회 |
| `/api/list-cases/<현장명>` | GET | 케이스 목록 조회 |

## 구글드라이브 폴더 구조

```
방수명장AS백업/
  ├─ OO아파트_101동_옥상/
  │   └─ AS20260401-0001/
  │       ├─ 기본정보.json
  │       ├─ 전체백업_20260401_120000.json
  │       ├─ 공문/
  │       │   └─ AS접수공문.jpg
  │       ├─ 활동기록/
  │       │   └─ 1차_현장방문/
  │       │       ├─ 회의록.json
  │       │       └─ 사진1.jpg
  │       ├─ 시공일지/
  │       │   └─ 1일차/
  │       │       ├─ 일지.json
  │       │       └─ 작업1.jpg
  │       └─ 완료검사/
  └─ XX빌딩_외벽/
      └─ ...
```

## 테스트

```bash
# 상태 확인
curl http://localhost:5000/api/status

# 백업 테스트
curl -X POST http://localhost:5000/api/backup \
  -H "Content-Type: application/json" \
  -d '{"metadata":{"caseId":"AS20260401-TEST","siteName":"테스트현장"},"basicInfo":{"siteName":"테스트현장"}}'

# 현장 목록
curl http://localhost:5000/api/list-sites
```

## (주)아이디에프이앤씨
