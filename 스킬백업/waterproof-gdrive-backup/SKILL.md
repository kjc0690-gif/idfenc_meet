---
name: waterproof-gdrive-backup
description: 방수명장 AS 시스템 구글드라이브 자동 백업 스킬. AS 백업 서버를 시작/중지하고, 구글드라이브 인증 상태를 확인하고, 수동 백업을 실행한다. '방수 백업', 'AS 백업', '구글드라이브 백업', '백업 서버', '방수명장 서버' 등을 언급하면 이 스킬을 사용한다.
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# 방수명장 AS 시스템 - 구글드라이브 백업 스킬

방수명장 AS 관리 시스템의 데이터를 구글드라이브에 자동 백업하는 Flask 서버를 관리한다.

## 프로젝트 위치

```
소스코드: C:\Users\kjc06\클로드 작업기록\idfenc_meet\waterproof-as-sync\
G드라이브 백업: G:\내 드라이브\클로드작업기록\방수명장\AS대응프로세스\
```

## 명령어

사용자가 요청할 수 있는 작업 종류:

### 1. 서버 시작

```bash
cd "C:/Users/kjc06/클로드 작업기록/idfenc_meet/waterproof-as-sync"
python app.py
```

- 서버 주소: http://localhost:5000
- 서버 상태 페이지: http://localhost:5000
- 백그라운드 실행 시 `run_in_background` 사용

### 2. 서버 상태 확인

```bash
curl -s http://localhost:5000/api/status
```

- `authenticated: true` → 구글드라이브 연결됨
- `authenticated: false` → 인증 필요

### 3. 구글 인증 (최초 1회)

```bash
curl -s http://localhost:5000/api/auth
```

- 반환된 `auth_url`을 브라우저에서 열어 구글 계정 인증
- 인증 후 `token.json` 자동 생성

### 4. 수동 백업 실행

```bash
curl -X POST http://localhost:5000/api/backup \
  -H "Content-Type: application/json" \
  -d @backup_data.json
```

### 5. 현장 목록 조회

```bash
curl -s http://localhost:5000/api/list-sites
```

### 6. 서버 중지

서버 프로세스를 찾아서 종료:
```bash
# Windows
taskkill /F /PID $(netstat -ano | grep :5000 | head -1 | awk '{print $5}')
```

## Google Cloud 설정 가이드

사용자가 처음 설정할 때 아래 절차를 안내한다:

1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성: `방수명장-AS-백업`
3. API 라이브러리 → `Google Drive API` 사용 설정
4. 사용자 인증 정보 → OAuth 클라이언트 ID 생성
   - 유형: 웹 애플리케이션
   - 리디렉션 URI: `http://localhost:5000/oauth2callback`
5. 클라이언트 ID와 Secret을 `.env` 파일에 입력

```bash
cd "C:/Users/kjc06/클로드 작업기록/idfenc_meet/waterproof-as-sync"
cp .env.example .env
# .env 파일에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 입력
```

## 구글드라이브 폴더 구조

백업 시 자동 생성되는 폴더:

```
방수명장AS백업/
  ├─ {현장명}/
  │   └─ {접수번호}/
  │       ├─ 기본정보.json
  │       ├─ 전체백업_{날짜}.json
  │       ├─ 공문/
  │       ├─ 활동기록/
  │       │   └─ N차_{유형}/
  │       │       ├─ 회의록.json
  │       │       └─ 사진.jpg
  │       ├─ 시공일지/
  │       │   └─ N일차/
  │       │       ├─ 일지.json
  │       │       └─ 작업사진.jpg
  │       └─ 완료검사/
```

## 문제 해결

### 서버가 안 켜질 때
```bash
cd "C:/Users/kjc06/클로드 작업기록/idfenc_meet/waterproof-as-sync"
pip install -r requirements.txt
python app.py
```

### 인증이 만료되었을 때
- `token.json` 삭제 후 `/api/auth`로 재인증
```bash
rm "C:/Users/kjc06/클로드 작업기록/idfenc_meet/waterproof-as-sync/token.json"
```

### 포트 충돌 시
- `.env`에서 `PORT=5001`로 변경

## 주의사항

- `credentials.json`, `token.json`, `.env` 파일은 절대 Git에 커밋하지 않는다
- 서버는 로컬에서만 실행 (외부 공개 금지)
- 백업 데이터에 개인정보가 포함될 수 있으므로 구글드라이브 공유 설정 주의
