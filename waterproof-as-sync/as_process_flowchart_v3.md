# 방수명장 AS 대응 프로세스 플로우차트

## 1. 전체 프로세스 개요

```mermaid
flowchart TD
    Start([AS 접수]) --> Step1[📋 공문 접수]
    Step1 --> Step1a[공문 사진 업로드]
    Step1a --> Step1b[AI 검토 의견 생성]
    Step1b --> Step1c[현장명/현장개요 입력]
    
    Step1c --> Step2[📝 기본정보 입력]
    Step2 --> Step2a[구조물 정보]
    Step2a --> Step2b[누수 증상]
    Step2b --> Step2c[고객 정보]
    
    Step2c --> Step3[⚡ 긴급도 판단]
    Step3 --> Step3a[체크리스트 작성]
    Step3a --> Step3b{긴급도 점수 계산}
    Step3b -->|5점 이상| High[높음 - 긴급 대응]
    Step3b -->|3-4점| Medium[보통 - 일반 대응]
    Step3b -->|0-2점| Low[낮음 - 예약 대응]
    
    High --> Step4[📅 활동 관리 허브]
    Medium --> Step4
    Low --> Step4
    
    Step4 --> Loop{활동 추가}
    Loop -->|현장 방문| Visit[🔍 현장 방문]
    Loop -->|회의| Meeting[💬 회의]
    Loop -->|시공| Construction[⚒️ 시공]
    
    Visit --> VisitDetail[방문 내용 기록<br/>사진 첨부]
    Meeting --> MeetingDetail[회의록 작성<br/>참석자/결정사항/액션아이템]
    Construction --> ConstructionDetail[시공일지 작성<br/>작업내용/진척도/자재]
    
    VisitDetail --> SaveActivity[활동 저장]
    MeetingDetail --> SaveActivity
    ConstructionDetail --> SaveActivity
    
    SaveActivity --> MoreActivity{추가 활동?}
    MoreActivity -->|Yes| Loop
    MoreActivity -->|No| Step5[📊 종합 보고서]
    
    Step5 --> Step5a[현장 요약 확인]
    Step5a --> Step5b[데이터 내보내기<br/>JSON/PDF]
    Step5b --> Complete([AS 완료])
    
    style Start fill:#10b981,color:#fff
    style Complete fill:#ef4444,color:#fff
    style High fill:#fee2e2,color:#ef4444
    style Medium fill:#fef3c7,color:#f59e0b
    style Low fill:#dbeafe,color:#2563eb
    style Step4 fill:#e0e7ff,color:#4f46e5
```

---

## 2. 상세 단계별 프로세스

### 2.1 공문 접수 프로세스

```mermaid
flowchart LR
    A[AS 공문 수신] --> B{사진 첨부?}
    B -->|Yes| C[드래그앤드롭<br/>업로드]
    B -->|No| D[직접 촬영<br/>업로드]
    
    C --> E[사진 미리보기]
    D --> E
    
    E --> F[AI 분석 버튼 클릭]
    F --> G[AI 검토 의견<br/>자동 생성]
    
    G --> H[현장명 입력]
    H --> I[현장개요 입력<br/>준공연도/방수이력/균열원인]
    
    I --> J[LocalStorage<br/>자동 저장]
    J --> K[다음 단계 이동]
```

### 2.2 긴급도 판단 알고리즘

```mermaid
flowchart TD
    Start[긴급도 체크리스트] --> C1{실내 침수?}
    C1 -->|Yes +3점| Score1[점수 +3]
    C1 -->|No| C2
    
    Score1 --> C2{구조 균열?}
    C2 -->|Yes +2점| Score2[점수 +2]
    C2 -->|No| C3
    
    Score2 --> C3{24시간 이내?}
    C3 -->|Yes +2점| Score3[점수 +2]
    C3 -->|No| C4
    
    Score3 --> C4{육안 균열?}
    C4 -->|Yes +1점| Score4[점수 +1]
    C4 -->|No| C5
    
    Score4 --> C5{우천 시만?}
    C5 -->|Yes +1점| Score5[점수 +1]
    C5 -->|No| Total
    
    Score5 --> Total[총점 계산]
    
    Total --> Result{총점}
    Result -->|≥5점| High[높음 긴급]
    Result -->|3-4점| Medium[보통]
    Result -->|≤2점| Low[낮음]
    
    style High fill:#fee2e2,color:#ef4444
    style Medium fill:#fef3c7,color:#f59e0b
    style Low fill:#dbeafe,color:#2563eb
```

### 2.3 활동 관리 프로세스

```mermaid
flowchart TD
    Hub[활동 관리 허브] --> Choice{활동 유형 선택}
    
    Choice -->|현장 방문| Visit[현장 방문 모드]
    Choice -->|회의| Meeting[회의 모드]
    Choice -->|시공| Construction[시공 모드]
    
    Visit --> V1[날짜/시간 입력]
    V1 --> V2[방문 내용 작성]
    V2 --> V3[사진 첨부]
    V3 --> SaveV[저장]
    
    Meeting --> M1[날짜/시간 입력]
    M1 --> M2[회의 내용 작성]
    M2 --> M3[참석자 추가]
    M3 --> M4[주요 결정사항 작성]
    M4 --> M5[보류 사항 작성]
    M5 --> M6[액션 아이템 추가<br/>담당자/기한]
    M6 --> M7[사진 첨부]
    M7 --> SaveM[저장]
    
    Construction --> C1[날짜/기상 입력]
    C1 --> C2[투입 인원 입력]
    C2 --> C3[작업 내용 작성]
    C3 --> C4[사용 자재 입력]
    C4 --> C5[진척도 입력 %]
    C5 --> C6[특이사항 작성]
    C6 --> C7[작업 사진 첨부]
    C7 --> SaveC[저장]
    
    SaveV --> DB[LocalStorage<br/>activities 배열에 추가]
    SaveM --> DB
    SaveC --> DB
    
    DB --> Render[활동 목록 렌더링]
    Render --> More{추가 활동?}
    More -->|Yes| Hub
    More -->|No| Report[보고서 작성]
```

### 2.4 데이터 흐름도

```mermaid
flowchart LR
    UI[사용자 입력] --> Validate{검증}
    Validate -->|Pass| DataModel[currentCase<br/>객체]
    Validate -->|Fail| Alert[경고 메시지]
    
    Alert --> UI
    
    DataModel --> LocalStorage[(LocalStorage)]
    LocalStorage --> AutoSave[자동 저장<br/>실시간]
    
    DataModel --> Export{내보내기}
    Export -->|JSON| JSON[JSON 파일<br/>다운로드]
    Export -->|PDF| PDF[PDF 보고서<br/>추후 지원]
    
    JSON --> GoogleDrive[수동 업로드<br/>Google Drive]
    PDF --> GoogleDrive
    
    GoogleDrive --> Folder[현장명별 폴더<br/>/방수명장AS백업/]
```

---

## 3. 데이터 구조

### 3.1 currentCase 객체 구조

```json
{
  "caseId": "AS-20260401-0001",
  "version": "3.0",
  "createdAt": "2026-04-01T00:00:00.000Z",
  "updatedAt": "2026-04-01T12:00:00.000Z",
  
  "officialDocPhotos": ["base64...", "base64..."],
  "aiAnalysis": "AI 검토 의견 텍스트",
  "siteName": "OO아파트 101동 옥상",
  "siteOverview": "2010년 준공, 기존 우레탄 방수...",
  
  "basicInfo": {
    "buildingType": "아파트",
    "constructionArea": "옥상",
    "constructionSize": "150",
    "completionYear": "2010",
    "mainSymptoms": "우천 시 실내 누수",
    "existingMethod": "우레탄 도막방수",
    "firstOccurrence": "2026-03-15",
    "clientName": "홍길동",
    "clientPhone": "010-1234-5678",
    "clientAddress": "서울시 강남구..."
  },
  
  "urgency": {
    "checklist": ["실내 침수", "구조 균열"],
    "score": 5,
    "level": "높음 (긴급)"
  },
  
  "activities": [
    {
      "id": 1711958400000,
      "type": "visit",
      "date": "2026-04-01",
      "time": "14:00",
      "content": "현장 사전 조사",
      "photos": ["base64..."]
    },
    {
      "id": 1711962000000,
      "type": "meeting",
      "date": "2026-04-02",
      "time": "10:00",
      "content": "보수 방안 협의",
      "photos": ["base64..."],
      "meetingMinutes": {
        "attendees": ["홍길동", "김기술", "이시공"],
        "decisions": "우레탄 전면 재시공 결정",
        "pending": "예산 최종 승인 대기",
        "actionItems": [
          {
            "task": "견적서 제출",
            "assignee": "김기술",
            "deadline": "2026-04-05"
          }
        ]
      }
    },
    {
      "id": 1711975600000,
      "type": "construction",
      "date": "2026-04-10",
      "time": "09:00",
      "content": "1일차 시공",
      "photos": ["base64..."],
      "constructionLog": {
        "weather": "맑음",
        "workers": "5",
        "work": "바탕면 정리 및 프라이머 도포",
        "materials": "프라이머 10L, 우레탄 방수재 30kg",
        "progress": "20",
        "notes": "바탕면 함수율 양호"
      }
    }
  ]
}
```

---

## 4. 핵심 모듈 설명

### 4.1 Navigation Module

```javascript
function goToStep(stepId) {
    // 1. 현재 스텝 검증
    if (!validateCurrentStep()) return;
    
    // 2. 모든 스텝 숨김
    hideAllSteps();
    
    // 3. 타겟 스텝 표시
    showStep(stepId);
    
    // 4. 네비게이션 업데이트
    updateNavigation(stepId);
    
    // 5. 자동 저장
    saveToLocalStorage();
}
```

### 4.2 Photo Upload Module

```javascript
function handlePhotoUpload(e, targetArray) {
    const files = Array.from(e.target.files);
    
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                // Base64로 변환
                targetArray.push(e.target.result);
                
                // 미리보기 렌더링
                renderPhotos();
                
                // 자동 저장
                saveToLocalStorage();
            };
            
            reader.readAsDataURL(file);
        }
    });
}
```

### 4.3 Activity Management Module

```javascript
function saveActivity() {
    // 1. 유형별 데이터 수집
    const baseData = collectBaseData();
    
    // 2. 회의록/시공일지 추가 데이터
    if (type === 'meeting') {
        baseData.meetingMinutes = collectMeetingData();
    }
    if (type === 'construction') {
        baseData.constructionLog = collectConstructionData();
    }
    
    // 3. activities 배열에 추가
    currentCase.activities.push(baseData);
    
    // 4. UI 업데이트
    renderActivities();
    
    // 5. 저장
    saveToLocalStorage();
}
```

### 4.4 LocalStorage Module

```javascript
function saveToLocalStorage() {
    // 1. 업데이트 시간 갱신
    currentCase.updatedAt = new Date().toISOString();
    
    // 2. JSON 직렬화
    const jsonString = JSON.stringify(currentCase);
    
    // 3. LocalStorage 저장
    localStorage.setItem('waterproofing_as_case', jsonString);
    
    // 4. 자동 저장 표시
    showAutoSaveIndicator();
}

function loadFromLocalStorage() {
    // 1. 데이터 로드
    const saved = localStorage.getItem('waterproofing_as_case');
    
    if (!saved) return;
    
    // 2. JSON 파싱
    currentCase = JSON.parse(saved);
    
    // 3. UI 복원
    restoreAllFields();
    renderAllPhotos();
    renderActivities();
}
```

---

## 5. 사용자 시나리오

### 시나리오 1: 긴급 누수 접수

```mermaid
sequenceDiagram
    actor User as 담당자
    participant System as AS 시스템
    participant AI as AI 분석
    participant Storage as LocalStorage
    
    User->>System: 공문 사진 업로드
    System->>AI: 사진 분석 요청
    AI-->>System: 검토 의견 반환
    System-->>User: AI 의견 표시
    
    User->>System: 현장명/개요 입력
    System->>Storage: 자동 저장
    
    User->>System: 기본정보 입력
    System->>Storage: 자동 저장
    
    User->>System: 긴급도 체크
    System->>System: 점수 계산
    System-->>User: "높음 (긴급)" 표시
    
    User->>System: 현장 방문 기록
    System->>Storage: 활동 저장
    
    User->>System: 회의 기록
    System->>Storage: 활동 저장
    
    User->>System: 시공 기록
    System->>Storage: 활동 저장
    
    User->>System: JSON 백업
    System-->>User: 파일 다운로드
```

### 시나리오 2: 데이터 복원

```mermaid
flowchart TD
    Start[브라우저 재접속] --> Load[시스템 로드]
    Load --> Check{LocalStorage<br/>데이터 존재?}
    
    Check -->|Yes| Parse[JSON 파싱]
    Check -->|No| New[신규 케이스 생성]
    
    Parse --> Restore1[현장명/개요 복원]
    Restore1 --> Restore2[기본정보 복원]
    Restore2 --> Restore3[사진 복원]
    Restore3 --> Restore4[활동 목록 복원]
    
    Restore4 --> Ready[작업 재개 가능]
    New --> Ready
```

---

## 6. 저장소 구조

### 6.1 LocalStorage 구조

```
localStorage
├─ waterproofing_as_case (JSON string)
│  └─ currentCase 객체 전체
```

### 6.2 Google Drive 폴더 구조 (수동 업로드)

```
Google Drive/
└─ 방수명장AS백업/
    └─ OO아파트_101동_옥상/
        └─ AS-20260401-0001/
            ├─ AS백업_OO아파트_AS-20260401-0001_2026-04-01.json
            ├─ 공문사진_1.jpg
            ├─ 공문사진_2.jpg
            ├─ 현장방문1차_사진1.jpg
            ├─ 회의_사진1.jpg
            └─ 시공1일차_사진1.jpg
```

---

## 7. 주요 기능 흐름

### 7.1 공문 접수 → AI 분석

```mermaid
stateDiagram-v2
    [*] --> 공문업로드
    공문업로드 --> 사진미리보기
    사진미리보기 --> AI분석대기
    AI분석대기 --> AI분석중 : 버튼클릭
    AI분석중 --> AI의견표시
    AI의견표시 --> 현장정보입력
    현장정보입력 --> [*]
```

### 7.2 활동 추가 → 저장

```mermaid
stateDiagram-v2
    [*] --> 활동유형선택
    활동유형선택 --> 기본정보입력
    
    기본정보입력 --> 현장방문양식 : type=visit
    기본정보입력 --> 회의록양식 : type=meeting
    기본정보입력 --> 시공일지양식 : type=construction
    
    현장방문양식 --> 사진첨부
    회의록양식 --> 참석자입력
    시공일지양식 --> 진척도입력
    
    참석자입력 --> 결정사항입력
    결정사항입력 --> 액션아이템입력
    액션아이템입력 --> 사진첨부
    
    진척도입력 --> 자재입력
    자재입력 --> 사진첨부
    
    사진첨부 --> 저장버튼
    저장버튼 --> 배열추가
    배열추가 --> LocalStorage저장
    LocalStorage저장 --> 목록렌더링
    목록렌더링 --> [*]
```

---

## 8. 옵션 A 특징 요약

| 항목 | 설명 |
|------|------|
| **저장 방식** | LocalStorage (브라우저 내 자동 저장) |
| **백업 방식** | JSON 파일 수동 다운로드 |
| **Google Drive 연동** | 수동 업로드 (사용자가 직접) |
| **AI 분석** | Mock 버전 (실제 AI는 미연동) |
| **데이터 영속성** | 브라우저 저장 (수정해도 보존) |
| **사진 저장** | Base64 인코딩 (JSON 내 포함) |
| **PDF 내보내기** | 추후 업데이트 예정 |
| **모바일 대응** | 반응형 디자인 지원 |
| **설치 필요** | 없음 (HTML 파일만) |
| **서버 필요** | 없음 (완전 오프라인 동작) |

---

## 9. 개발 로드맵

### Phase 1: 옵션 A (현재) ✅
- HTML 단일 파일
- LocalStorage 저장
- JSON 백업
- Mock AI 분석

### Phase 2: 옵션 B (차후)
- Google Drive API 연동
- 자동 백업 기능
- Flask 백엔드 서버
- OAuth 인증

### Phase 3: 옵션 C (차후)
- 실제 AI 사진 분석
- PDF 자동 생성
- 이메일 자동 발송
- 대시보드 통계

---

## 10. 기술 스택

| 구분 | 기술 |
|------|------|
| **프론트엔드** | HTML5, CSS3, Vanilla JavaScript |
| **저장소** | LocalStorage API |
| **이미지 처리** | FileReader API (Base64) |
| **반응형** | CSS Grid, Flexbox, Media Queries |
| **아이콘** | Emoji (별도 라이브러리 없음) |
| **데이터 포맷** | JSON |
| **브라우저 지원** | Chrome, Edge, Safari, Firefox (최신 버전) |

---

## 11. 성능 최적화 전략

```mermaid
graph LR
    A[성능 최적화] --> B[이미지 압축]
    A --> C[지연 로딩]
    A --> D[캐싱 전략]
    
    B --> B1[사진 리사이징<br/>권장]
    B --> B2[Base64 용량<br/>주의]
    
    C --> C1[필요 시점에만<br/>렌더링]
    
    D --> D1[LocalStorage<br/>1회 로드]
    D --> D2[실시간 저장<br/>throttling]
```

---

*본 플로우차트는 방수명장 AS 대응 프로세스 v3.0 (옵션 A) 기준으로 작성되었습니다.*
