# 방수명장 AS 시스템 - 구글드라이브 자동 업로드 연동 가이드

## 📋 프로젝트 개요

**목적:** 방수명장 AS 시스템의 데이터를 자동으로 구글드라이브에 백업하는 기능 구현

**현재 상태:**
- ✅ HTML 기반 AS 관리 시스템 완성
- ✅ LocalStorage 자동 저장 구현
- ⏳ 구글드라이브 업로드는 수동 (JSON 다운로드 → 수동 업로드)

**목표:**
- 🎯 구글드라이브 자동 업로드 기능 추가
- 🎯 현장별 폴더 자동 생성
- 🎯 실시간 또는 주기적 백업

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 브라우저                           │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  방수명장 AS 시스템 (HTML/JavaScript)              │     │
│  │                                                     │     │
│  │  • 데이터 입력/수정                                │     │
│  │  • LocalStorage 자동 저장                         │     │
│  │  • UI 렌더링                                       │     │
│  └─────────────────┬──────────────────────────────────┘     │
│                    │                                         │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     │ HTTP POST
                     │ (JSON 데이터)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Claude Code 백엔드 서버                         │
│              (Python Flask/FastAPI)                          │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API 엔드포인트                                    │     │
│  │  • POST /api/backup - 백업 요청                   │     │
│  │  • GET  /api/status - 동기화 상태                 │     │
│  │  • POST /api/sync - 강제 동기화                   │     │
│  └─────────────────┬──────────────────────────────────┘     │
│                    │                                         │
│  ┌─────────────────┴──────────────────────────────────┐     │
│  │  Google Drive API 클라이언트                       │     │
│  │                                                     │     │
│  │  • OAuth 인증 관리                                │     │
│  │  • 파일 업로드                                     │     │
│  │  • 폴더 생성/관리                                  │     │
│  │  • 파일 검색/업데이트                              │     │
│  └─────────────────┬──────────────────────────────────┘     │
│                    │                                         │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     │ Google Drive API
                     │ (OAuth 2.0)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Google Drive                                │
│                                                               │
│  /방수명장AS백업/                                            │
│    ├─ OO아파트_101동_옥상/                                  │
│    │   ├─ AS20260401-0001/                                  │
│    │   │   ├─ 기본정보.json                                 │
│    │   │   ├─ 전체백업_20260401_120000.json                │
│    │   │   ├─ 공문/                                         │
│    │   │   │   └─ 공문사진.jpg                              │
│    │   │   ├─ 활동기록/                                     │
│    │   │   └─ 시공일지/                                     │
│    │   └─ AS20260405-0002/                                  │
│    ├─ XX빌딩_외벽/                                          │
│    └─ 동기화_로그.txt                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 데이터 구조

### AS 케이스 데이터 (JSON)
```json
{
  "version": "2.0",
  "metadata": {
    "caseId": "AS20260401-0001",
    "siteName": "OO아파트 101동 옥상",
    "siteNameSafe": "OO아파트_101동_옥상",
    "createdAt": "2026-04-01T09:00:00Z",
    "updatedAt": "2026-04-01T15:30:00Z",
    "status": "진행중",
    "assignee": "김철수",
    "googleDriveFolderId": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
    "lastSyncAt": "2026-04-01T15:30:00Z"
  },
  "document": {
    "uploaded": true,
    "files": [
      {
        "id": "doc_001",
        "name": "AS접수공문.jpg",
        "base64": "data:image/jpeg;base64,/9j/4AAQ...",
        "uploadedAt": "2026-04-01T09:05:00Z",
        "googleDriveFileId": "1XyZ..."
      }
    ],
    "aiAnalysis": { ... }
  },
  "basicInfo": {
    "siteName": "OO아파트 101동 옥상",
    "siteOverview": "2015년 준공, 우레탄 도막방수 시공...",
    "buildingType": "아파트",
    "location": "옥상",
    "address": "서울시 강남구...",
    "customerName": "홍길동",
    "phone": "010-1234-5678",
    "symptoms": "천장에서 물이 떨어짐..."
  },
  "urgency": { ... },
  "activities": [ ... ],
  "construction": { ... },
  "completion": null
}
```

---

## 🔧 Claude Code 구현 가이드

### 1. 프로젝트 구조
```
waterproof-as-sync/
├─ app.py                 # Flask/FastAPI 메인
├─ requirements.txt       # 패키지 목록
├─ config.py             # 설정 파일
├─ google_drive.py       # Google Drive API 클라이언트
├─ models.py             # 데이터 모델
├─ utils.py              # 유틸리티 함수
├─ credentials.json      # Google OAuth 인증 정보
├─ token.json            # OAuth 토큰 (자동 생성)
└─ README.md             # 문서
```

### 2. 필수 패키지 (requirements.txt)
```txt
flask==3.0.0
flask-cors==4.0.0
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0
python-dotenv==1.0.0
```

### 3. 환경 변수 (.env)
```bash
# Google Drive API
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback

# Server
PORT=5000
DEBUG=True

# Backup
BACKUP_FOLDER_NAME=방수명장AS백업
AUTO_SYNC_INTERVAL=300  # 5분마다 자동 동기화
```

---

## 🔑 Google Drive API 설정

### Step 1: Google Cloud Console 설정
```
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성: "방수명장-AS-백업"
3. "API 및 서비스" → "라이브러리"
4. "Google Drive API" 검색 → 사용 설정
5. "사용자 인증 정보" → "OAuth 클라이언트 ID 만들기"
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI: http://localhost:5000/oauth2callback
6. credentials.json 다운로드
```

### Step 2: OAuth 범위 (Scopes)
```python
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',  # 생성한 파일만 접근
    'https://www.googleapis.com/auth/drive.appdata'  # 앱 데이터 폴더
]
```

---

## 💻 핵심 코드 구현

### app.py (Flask 메인)
```python
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from google_drive import GoogleDriveClient
import json
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)  # HTML에서 접근 가능하도록

# Google Drive 클라이언트 초기화
drive_client = GoogleDriveClient()

@app.route('/api/auth', methods=['GET'])
def auth():
    """OAuth 인증 시작"""
    auth_url = drive_client.get_authorization_url()
    return jsonify({'auth_url': auth_url})

@app.route('/oauth2callback')
def oauth2callback():
    """OAuth 콜백"""
    code = request.args.get('code')
    drive_client.authenticate(code)
    return "인증 완료! 이 창을 닫아도 됩니다."

@app.route('/api/backup', methods=['POST'])
def backup():
    """AS 데이터 백업"""
    try:
        data = request.json
        case_id = data['metadata']['caseId']
        site_name = data['metadata']['siteNameSafe']
        
        # 폴더 구조 생성
        folder_id = drive_client.create_folder_structure(site_name, case_id)
        
        # JSON 백업
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'전체백업_{timestamp}.json'
        file_id = drive_client.upload_json(data, folder_id, filename)
        
        # 기본정보.json 업데이트
        drive_client.upload_json(data, folder_id, '기본정보.json')
        
        # 사진 업로드 (공문)
        if data.get('document', {}).get('files'):
            doc_folder_id = drive_client.create_subfolder(folder_id, '공문')
            for file_data in data['document']['files']:
                drive_client.upload_base64_image(
                    file_data['base64'],
                    doc_folder_id,
                    file_data['name']
                )
        
        # 메타데이터 업데이트
        data['metadata']['googleDriveFolderId'] = folder_id
        data['metadata']['lastSyncAt'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'folderId': folder_id,
            'fileId': file_id,
            'message': '백업 완료'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """동기화 상태 확인"""
    is_authenticated = drive_client.is_authenticated()
    return jsonify({
        'authenticated': is_authenticated,
        'ready': is_authenticated
    })

@app.route('/api/list-sites', methods=['GET'])
def list_sites():
    """현장 목록 조회"""
    try:
        sites = drive_client.list_sites()
        return jsonify({'sites': sites})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

### google_drive.py (Google Drive 클라이언트)
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
import json
import base64
import io
import os

class GoogleDriveClient:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.root_folder_id = None
        self.load_credentials()
    
    def load_credentials(self):
        """저장된 인증 정보 로드"""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            self.service = build('drive', 'v3', credentials=self.creds)
    
    def get_authorization_url(self):
        """OAuth 인증 URL 생성"""
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=self.SCOPES,
            redirect_uri='http://localhost:5000/oauth2callback'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def authenticate(self, code):
        """OAuth 인증 완료"""
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=self.SCOPES,
            redirect_uri='http://localhost:5000/oauth2callback'
        )
        flow.fetch_token(code=code)
        self.creds = flow.credentials
        
        # 토큰 저장
        with open('token.json', 'w') as token:
            token.write(self.creds.to_json())
        
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def is_authenticated(self):
        """인증 상태 확인"""
        return self.creds is not None and self.creds.valid
    
    def get_or_create_root_folder(self):
        """루트 폴더 가져오기 또는 생성"""
        if self.root_folder_id:
            return self.root_folder_id
        
        # 기존 폴더 검색
        query = "name='방수명장AS백업' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            self.root_folder_id = files[0]['id']
        else:
            # 새 폴더 생성
            file_metadata = {
                'name': '방수명장AS백업',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            self.root_folder_id = folder['id']
        
        return self.root_folder_id
    
    def create_folder_structure(self, site_name, case_id):
        """현장별 폴더 구조 생성"""
        root_id = self.get_or_create_root_folder()
        
        # 현장 폴더
        site_folder_id = self.get_or_create_folder(site_name, root_id)
        
        # AS 케이스 폴더
        case_folder_id = self.get_or_create_folder(case_id, site_folder_id)
        
        # 하위 폴더들
        self.get_or_create_folder('공문', case_folder_id)
        self.get_or_create_folder('활동기록', case_folder_id)
        self.get_or_create_folder('시공일지', case_folder_id)
        self.get_or_create_folder('완료검사', case_folder_id)
        
        return case_folder_id
    
    def get_or_create_folder(self, name, parent_id):
        """폴더 가져오기 또는 생성"""
        query = f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        else:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder['id']
    
    def create_subfolder(self, parent_id, name):
        """하위 폴더 생성"""
        return self.get_or_create_folder(name, parent_id)
    
    def upload_json(self, data, folder_id, filename):
        """JSON 데이터 업로드"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaInMemoryUpload(
            json_str.encode('utf-8'),
            mimetype='application/json',
            resumable=True
        )
        
        # 기존 파일 검색
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])
        
        if files:
            # 업데이트
            file_id = files[0]['id']
            file = self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
        else:
            # 새로 생성
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
        
        return file['id']
    
    def upload_base64_image(self, base64_data, folder_id, filename):
        """Base64 이미지 업로드"""
        # Base64 디코딩
        if ',' in base64_data:
            header, data = base64_data.split(',', 1)
        else:
            data = base64_data
        
        image_data = base64.b64decode(data)
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # MIME 타입 추정
        if filename.lower().endswith('.png'):
            mime_type = 'image/png'
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        else:
            mime_type = 'image/jpeg'
        
        media = MediaInMemoryUpload(
            image_data,
            mimetype=mime_type,
            resumable=True
        )
        
        # 기존 파일 확인
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])
        
        if files:
            file_id = files[0]['id']
            file = self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
        else:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
        
        return file['id']
    
    def list_sites(self):
        """현장 목록 조회"""
        root_id = self.get_or_create_root_folder()
        query = f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
            q=query,
            fields='files(id, name, createdTime, modifiedTime)'
        ).execute()
        return results.get('files', [])
```

---

## 🌐 HTML 수정 (프론트엔드)

### JavaScript 추가 코드
```javascript
// Google Drive 동기화 클라이언트
class GoogleDriveSyncClient {
    constructor() {
        this.serverUrl = 'http://localhost:5000';
        this.authenticated = false;
        this.checkAuthStatus();
    }
    
    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/api/status`);
            const data = await response.json();
            this.authenticated = data.authenticated;
            this.updateUI();
        } catch (error) {
            console.error('서버 연결 실패:', error);
        }
    }
    
    async authenticate() {
        try {
            const response = await fetch(`${this.serverUrl}/api/auth`);
            const data = await response.json();
            window.open(data.auth_url, '_blank');
            
            // 인증 완료 대기
            setTimeout(() => this.checkAuthStatus(), 5000);
        } catch (error) {
            alert('인증 실패: ' + error.message);
        }
    }
    
    async backup(caseData) {
        if (!this.authenticated) {
            alert('먼저 구글드라이브 인증을 완료해주세요.');
            return false;
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/api/backup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(caseData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('구글드라이브에 백업되었습니다!');
                return true;
            } else {
                alert('백업 실패: ' + result.error);
                return false;
            }
        } catch (error) {
            alert('백업 중 오류 발생: ' + error.message);
            return false;
        }
    }
    
    updateUI() {
        const statusEl = document.getElementById('gdrive-status');
        if (statusEl) {
            statusEl.textContent = this.authenticated ? '✅ 연결됨' : '❌ 미연결';
        }
    }
}

// 전역 인스턴스
const gdriveSync = new GoogleDriveSyncClient();

// 자동 백업 (5분마다)
setInterval(() => {
    if (gdriveSync.authenticated && currentCase) {
        gdriveSync.backup(currentCase);
    }
}, 5 * 60 * 1000);  // 5분

// 수동 백업 버튼
function backupToGoogleDrive() {
    if (!currentCase) {
        alert('백업할 데이터가 없습니다.');
        return;
    }
    gdriveSync.backup(currentCase);
}

// 구글드라이브 인증 버튼
function authenticateGoogleDrive() {
    gdriveSync.authenticate();
}
```

### HTML에 버튼 추가
```html
<!-- 헤더에 추가 -->
<div class="header-right">
    <span id="gdrive-status">❌ 미연결</span>
    <button class="header-btn" onclick="authenticateGoogleDrive()">
        🔐 구글드라이브 연결
    </button>
    <button class="header-btn" onclick="backupToGoogleDrive()">
        ☁️ 즉시 백업
    </button>
    <button class="header-btn" onclick="showCaseList()">📂 AS 목록</button>
    <button class="header-btn" onclick="exportData()">💾 로컬 백업</button>
    <button class="header-btn" onclick="newCase()">➕ 새 AS</button>
</div>
```

---

## 🚀 실행 방법

### 1. Claude Code에게 요청
```
아래 파일들을 생성하고 Flask 서버를 실행해주세요:

1. app.py (위 코드)
2. google_drive.py (위 코드)
3. requirements.txt (위 패키지 목록)
4. .env (환경 변수)

그리고:
- pip install -r requirements.txt
- python app.py

서버가 http://localhost:5000 에서 실행되도록 해주세요.
```

### 2. 사용자 워크플로우
```
1. Claude Code 서버 실행
   → Terminal: python app.py

2. HTML 페이지 열기
   → 방수명장 AS 시스템 실행

3. 첫 사용 시 인증
   → "🔐 구글드라이브 연결" 클릭
   → 팝업에서 구글 계정 인증
   → "인증 완료" 메시지 확인

4. 자동 백업 활성화
   → 5분마다 자동 백업
   → 상태: "✅ 연결됨" 표시

5. 수동 백업
   → "☁️ 즉시 백업" 클릭
   → 구글드라이브에 즉시 업로드
```

---

## 📁 구글드라이브 폴더 구조

```
📁 방수명장AS백업/
  │
  ├─📁 OO아파트_101동_옥상/
  │  │
  │  ├─📁 AS20260401-0001/
  │  │  ├─ 📄 기본정보.json (최신 상태)
  │  │  ├─ 📄 전체백업_20260401_120000.json
  │  │  ├─ 📄 전체백업_20260401_153000.json
  │  │  ├─📁 공문/
  │  │  │  ├─ 📷 AS접수공문.jpg
  │  │  │  └─ 📷 첨부서류.jpg
  │  │  ├─📁 활동기록/
  │  │  │  ├─📁 1차_현장방문/
  │  │  │  │  ├─ 📄 회의록.json
  │  │  │  │  ├─ 📷 사진1.jpg
  │  │  │  │  └─ 📷 사진2.jpg
  │  │  │  └─📁 2차_회의/
  │  │  ├─📁 시공일지/
  │  │  │  ├─📁 1일차/
  │  │  │  │  ├─ 📄 일지.json
  │  │  │  │  └─📁 작업사진/
  │  │  │  └─📁 2일차/
  │  │  └─📁 완료검사/
  │  │
  │  └─📁 AS20260405-0002/
  │     └─ ...
  │
  ├─📁 XX빌딩_외벽/
  │  └─ ...
  │
  └─ 📄 동기화_로그.txt
```

---

## 🎯 기능 요약

### 자동화된 기능
```
✅ 5분마다 자동 백업
✅ 현장별 폴더 자동 생성
✅ AS 케이스별 하위 폴더 자동 생성
✅ JSON 데이터 자동 업로드
✅ 사진 파일 자동 업로드
✅ 기존 파일 자동 업데이트 (덮어쓰기)
✅ 동기화 상태 실시간 표시
```

### 수동 기능
```
🔐 최초 1회 구글 계정 인증
☁️ 즉시 백업 버튼
📂 구글드라이브에서 직접 파일 확인
```

---

## 📋 체크리스트

### Claude Code에게 전달할 것
- [ ] 이 MD 파일
- [ ] credentials.json (Google Cloud Console에서 다운로드)
- [ ] 포트 5000 사용 가능한지 확인

### 사용자가 준비할 것
- [ ] Google 계정
- [ ] Google Cloud Console 프로젝트 생성
- [ ] OAuth 클라이언트 ID 생성
- [ ] credentials.json 다운로드

---

## 🔧 트러블슈팅

### 문제 1: 인증이 안됨
```
해결:
1. credentials.json 파일 확인
2. 리디렉션 URI 확인: http://localhost:5000/oauth2callback
3. Google Cloud Console에서 OAuth 동의 화면 설정
```

### 문제 2: CORS 에러
```
해결:
flask-cors 설치 확인
CORS(app) 코드 추가 확인
```

### 문제 3: 파일 업로드 실패
```
해결:
1. Google Drive API 사용 설정 확인
2. OAuth 범위(Scopes) 확인
3. 토큰 재생성: token.json 삭제 후 재인증
```

---

## 🎉 완료 후 결과

사용자는:
- ✅ 데이터 입력만 하면 자동으로 구글드라이브에 백업됨
- ✅ 브라우저 꺼도 서버가 백그라운드에서 동작
- ✅ 구글드라이브에서 언제든 파일 확인 가능
- ✅ 팀원들과 폴더 공유 가능
- ✅ 모바일에서도 구글드라이브 앱으로 확인

---

이 파일을 Claude Code에게 전달하고 구현을 요청하세요!
