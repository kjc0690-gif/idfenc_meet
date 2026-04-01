# Claude Code 프롬프트: 방수명장 AS 시스템 구글드라이브 자동 백업

## 📋 프로젝트 요청

안녕하세요! 방수명장 AS 관리 시스템의 **구글드라이브 자동 백업 기능**을 구현해주세요.

---

## 🎯 목표

**웹 기반 AS 시스템의 데이터를 자동으로 구글드라이브에 백업하는 Flask API 서버 구축**

---

## 📦 프로젝트 구조

다음 파일들을 생성해주세요:

```
waterproof-as-sync/
├─ app.py                 # Flask 메인 서버
├─ google_drive.py       # Google Drive API 클라이언트
├─ requirements.txt      # Python 패키지
├─ .env.example         # 환경 변수 템플릿
├─ README.md            # 사용 방법
└─ .gitignore           # Git 제외 파일
```

---

## 🔧 기능 요구사항

### 1. Flask API 엔드포인트

#### `GET /api/status`
- Google Drive 인증 상태 확인
- 반환: `{ "authenticated": true/false, "ready": true/false }`

#### `GET /api/auth`
- OAuth 인증 URL 생성
- 반환: `{ "auth_url": "https://..." }`

#### `GET /oauth2callback?code=xxx`
- OAuth 콜백 처리
- 토큰 저장 (`token.json`)
- 반환: HTML "인증 완료!" 메시지

#### `POST /api/backup`
- AS 케이스 데이터 백업
- 요청 본문: AS 케이스 JSON 전체
- 수행:
  1. 현장별 폴더 생성 (`/방수명장AS백업/{현장명}/{케이스ID}/`)
  2. 하위 폴더 생성 (`공문/`, `활동기록/`, `시공일지/`, `완료검사/`)
  3. JSON 파일 업로드
  4. Base64 이미지를 JPG로 변환하여 업로드
- 반환: `{ "success": true, "folderId": "...", "fileId": "..." }`

#### `GET /api/list-sites`
- 구글드라이브의 현장 목록 조회
- 반환: `{ "sites": [{ "id": "...", "name": "...", "createdTime": "..." }] }`

---

### 2. Google Drive 클라이언트 기능

#### 인증 관리
```python
- load_credentials(): token.json에서 인증 정보 로드
- get_authorization_url(): OAuth URL 생성
- authenticate(code): OAuth 코드로 인증 완료
- is_authenticated(): 인증 상태 확인
```

#### 폴더 관리
```python
- get_or_create_root_folder(): "방수명장AS백업" 루트 폴더
- create_folder_structure(site_name, case_id): 현장/케이스 폴더 생성
- get_or_create_folder(name, parent_id): 폴더 가져오기 또는 생성
- create_subfolder(parent_id, name): 하위 폴더 생성
```

#### 파일 업로드
```python
- upload_json(data, folder_id, filename): JSON 업로드 (덮어쓰기 지원)
- upload_base64_image(base64_data, folder_id, filename): 이미지 업로드
- list_sites(): 현장 목록 조회
```

---

## 📋 requirements.txt

```txt
flask==3.0.0
flask-cors==4.0.0
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0
python-dotenv==1.0.0
```

---

## 🔑 환경 변수 (.env.example)

```bash
# Google Drive API
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback

# Server
PORT=5000
DEBUG=True
HOST=0.0.0.0

# Backup
BACKUP_FOLDER_NAME=방수명장AS백업
AUTO_SYNC_INTERVAL=300
```

---

## 📊 데이터 구조 (참고)

백업할 AS 케이스 데이터 예시:

```json
{
  "version": "2.0",
  "metadata": {
    "caseId": "AS20260401-0001",
    "siteName": "OO아파트 101동 옥상",
    "siteNameSafe": "OO아파트_101동_옥상",
    "createdAt": "2026-04-01T09:00:00Z",
    "updatedAt": "2026-04-01T15:30:00Z",
    "status": "진행중"
  },
  "document": {
    "uploaded": true,
    "files": [
      {
        "id": "doc_001",
        "name": "AS접수공문.jpg",
        "base64": "data:image/jpeg;base64,/9j/4AAQ...",
        "uploadedAt": "2026-04-01T09:05:00Z"
      }
    ]
  },
  "basicInfo": {
    "siteName": "OO아파트 101동 옥상",
    "siteOverview": "현장 개요...",
    "buildingType": "아파트",
    "location": "옥상",
    "symptoms": "천장에서 물이 떨어짐..."
  },
  "urgency": { ... },
  "activities": [ ... ],
  "construction": { ... }
}
```

---

## 🏗️ 구글드라이브 폴더 구조

생성해야 할 구조:

```
방수명장AS백업/
  ├─ OO아파트_101동_옥상/
  │   ├─ AS20260401-0001/
  │   │   ├─ 기본정보.json          (최신 상태)
  │   │   ├─ 전체백업_20260401_120000.json
  │   │   ├─ 공문/
  │   │   │   └─ AS접수공문.jpg
  │   │   ├─ 활동기록/
  │   │   ├─ 시공일지/
  │   │   └─ 완료검사/
  │   └─ AS20260405-0002/
  └─ XX빌딩_외벽/
```

---

## 🔐 OAuth 설정 안내 (README.md에 포함)

### Google Cloud Console 설정
```
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트: "방수명장-AS-백업"
3. API 라이브러리 → "Google Drive API" 사용 설정
4. OAuth 클라이언트 ID 생성:
   - 유형: 웹 애플리케이션
   - 리디렉션 URI: http://localhost:5000/oauth2callback
5. credentials.json 다운로드 → 프로젝트 루트에 저장
```

### OAuth Scopes
```python
SCOPES = [
    'https://www.googleapis.com/auth/drive.file'
]
```

---

## 🚀 실행 방법 (README.md에 포함)

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
cp .env.example .env
# .env 파일 편집 (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
```

### 3. credentials.json 배치
```
Google Cloud Console에서 다운로드한 credentials.json을
프로젝트 루트에 저장
```

### 4. 서버 실행
```bash
python app.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 5. 첫 인증
```
1. http://localhost:5000/api/auth 접속
2. 반환된 auth_url로 이동
3. 구글 계정 인증
4. 자동으로 /oauth2callback으로 리디렉션
5. "인증 완료!" 메시지 확인
```

---

## 🧪 테스트 방법

### 상태 확인
```bash
curl http://localhost:5000/api/status
# 반환: {"authenticated": true, "ready": true}
```

### 백업 테스트
```bash
curl -X POST http://localhost:5000/api/backup \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

### 현장 목록 조회
```bash
curl http://localhost:5000/api/list-sites
```

---

## 🎯 주요 구현 포인트

### 1. 에러 처리
```python
- OAuth 인증 실패 시 명확한 에러 메시지
- 네트워크 오류 핸들링
- API 쿼터 초과 처리
- 파일명 중복 처리 (덮어쓰기)
```

### 2. 성능 최적화
```python
- 폴더 검색 시 캐싱
- 배치 업로드 지원
- 대용량 파일 청크 업로드
```

### 3. 보안
```python
- credentials.json은 .gitignore에 추가
- token.json도 .gitignore에 추가
- 환경 변수로 민감 정보 관리
```

### 4. 로깅
```python
- 모든 API 호출 로깅
- 업로드 성공/실패 기록
- 에러 스택 트레이스
```

---

## 📝 .gitignore

```
# Python
__pycache__/
*.py[cod]
*.so
*.egg
*.egg-info/
dist/
build/

# 환경
.env
venv/
env/

# Google OAuth
credentials.json
token.json

# 로그
*.log

# IDE
.vscode/
.idea/
```

---

## 🔧 CORS 설정

프론트엔드(HTML)에서 접근 가능하도록 CORS 활성화:

```python
from flask_cors import CORS
CORS(app, origins=["*"])  # 개발 중에는 모든 origin 허용
```

프로덕션에서는:
```python
CORS(app, origins=["https://your-domain.com"])
```

---

## 📚 참고 자료 링크

- Flask 공식 문서: https://flask.palletsprojects.com/
- Google Drive API: https://developers.google.com/drive/api/guides/about-sdk
- OAuth 2.0: https://developers.google.com/identity/protocols/oauth2

---

## ✅ 완료 기준

다음이 모두 작동하면 완료:

1. ✅ `python app.py` 실행 시 서버 정상 시작
2. ✅ `/api/status` 호출 시 JSON 반환
3. ✅ OAuth 인증 플로우 완료
4. ✅ `/api/backup` 호출 시 구글드라이브에 파일 생성
5. ✅ 폴더 구조 자동 생성
6. ✅ JSON 파일 업로드
7. ✅ Base64 이미지 → JPG 변환 및 업로드
8. ✅ 기존 파일 덮어쓰기 (업데이트)
9. ✅ 에러 처리 및 로깅
10. ✅ README.md 작성 완료

---

## 💬 추가 요청사항

1. **타입 힌팅**: 모든 함수에 타입 힌트 추가
2. **Docstring**: 모든 클래스와 함수에 docstring 작성
3. **예외 처리**: try-except로 모든 외부 API 호출 감싸기
4. **로깅**: logging 모듈 사용하여 DEBUG 레벨 로그 추가
5. **설정 파일**: config.py로 설정 분리

---

이 프롬프트대로 구현해주시고, 완료 후 다음을 알려주세요:

1. 생성된 파일 목록
2. 서버 실행 명령어
3. 첫 인증 방법
4. 테스트 방법

감사합니다! 🙏
