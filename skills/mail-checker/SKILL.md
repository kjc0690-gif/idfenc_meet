---
name: mail-checker
description: 이메일 알림, 요약, 정리 스킬. Gmail(kjc0690@gmail.com), 한메일(001kjc@hanmail.net), 네이버메일(001kjc@naver.com) 3개 계정의 메일을 확인하고 요약/정리해준다. 사용자가 '메일 확인', '메일 알려줘', '메일 요약', '새 메일', '읽지 않은 메일', '메일 정리', '이메일', 'email', '받은편지함', '인박스', 'inbox', '메일함', '안 읽은 메일', '메일 왔어?', '메일 있어?', '중요한 메일', '답장할 메일' 등을 언급하면 반드시 이 스킬을 사용한다. 메일과 관련된 모든 확인/요약/정리 요청에 이 스킬을 사용해야 한다.
---

# 이메일 알림, 요약 및 자동 정리 스킬

Gmail, 한메일, 네이버메일 3개 계정의 이메일을 확인하고, 중요도별로 분류하고, 보관/삭제를 자동 관리하는 스킬이다.

## 계정 정보

| 서비스 | 이메일 주소 | 접근 방식 |
|--------|------------|-----------|
| Gmail | kjc0690@gmail.com | Gmail MCP 도구 (직접 API) |
| 한메일 | 001kjc@hanmail.net | Chrome 브라우저 (mail.daum.net) |
| 네이버 | 001kjc@naver.com | Chrome 브라우저 (mail.naver.com) |

## 메일 확인 흐름

### 1단계: Gmail 확인 (MCP 도구 사용)

Gmail은 MCP 도구로 직접 접근하므로 가장 먼저, 항상 확인한다.

```
gmail_search_messages(q="is:unread", maxResults=20)
```

검색된 메일 각각에 대해 `gmail_read_message`로 내용을 읽는다. 단, 전체 메일이 많으면 최근 10개만 상세 읽기를 수행한다.

**Gmail 추가 검색 옵션:**
- 읽지 않은 메일만: `q="is:unread"`
- 오늘 받은 메일: `q="after:YYYY/MM/DD"` (오늘 날짜)
- 중요 메일: `q="is:important is:unread"`
- 특정 발신자: `q="from:특정주소"`
- 프로모션: `q="category:promotions is:unread"`
- 소셜: `q="category:social is:unread"`

### 2단계: 한메일 확인 (Chrome 브라우저)

한메일은 직접 API가 없으므로 Chrome 브라우저 도구를 사용한다.

**절차:**
1. `tabs_context_mcp`로 현재 탭 확인
2. `tabs_create_mcp`로 새 탭 생성
3. `navigate`로 `https://mail.daum.net` 이동
4. 로그인 상태 확인 - 로그인이 안 되어 있으면 사용자에게 로그인을 요청
5. 로그인 상태라면:
   - `read_page`로 받은편지함 페이지 읽기
   - `get_page_text`로 메일 목록 텍스트 추출
   - 읽지 않은 메일 목록 파악 (굵은 글씨/안 읽음 표시)
6. 개별 메일 클릭하여 내용 확인 (최대 5개)
7. 확인 완료 후 탭 닫기

**로그인 안 된 경우:**
```
한메일(001kjc@hanmail.net)에 로그인이 필요합니다.
브라우저에서 mail.daum.net에 로그인한 후 다시 시도해주세요.
```

### 3단계: 네이버메일 확인 (Chrome 브라우저)

네이버도 한메일과 동일한 방식으로 Chrome 브라우저를 사용한다.

**절차:**
1. 새 탭 생성
2. `navigate`로 `https://mail.naver.com` 이동
3. 로그인 상태 확인
4. 로그인 상태라면:
   - `read_page`로 받은편지함 읽기
   - `get_page_text`로 메일 목록 추출
   - 읽지 않은 메일 파악
5. 개별 메일 클릭하여 내용 확인 (최대 5개)
6. 확인 완료 후 탭 닫기

**로그인 안 된 경우:**
```
네이버메일(001kjc@naver.com)에 로그인이 필요합니다.
브라우저에서 mail.naver.com에 로그인한 후 다시 시도해주세요.
```

## 중요도 분류 체계 (5단계)

메일을 수신하면 발신자, 제목, 내용을 분석하여 아래 5단계로 자동 분류한다:

### 🔴 긴급 (즉시 확인 + 보관)
- 제목/본문에 "긴급", "urgent", "ASAP", "즉시", "오늘까지" 포함
- 거래처/고객/상사에서 온 업무 요청
- 기한이 임박한 작업 요청
- 결제 승인/요청 관련

### 🟠 중요 (보관 필수)
- **보안 알림**: Google 보안, GitHub 토큰, 비밀번호 변경 등
- **결제/영수증**: Anthropic, Google Play, Apple, 카드사, 은행
- **시스템 오류**: Apps Script 실패, 서버 에러 알림
- **계정 관련**: 비밀번호 변경, 2FA, 로그인 알림
- **업무 연락**: 실제 사람이 보낸 업무 관련 메일

### 🟡 일반 (확인 후 판단)
- 일반 업무 안내/공지
- 서비스 업데이트 알림 (Claude Team, GitHub 릴리스 등)
- 개인 연락
- 뉴스레터 중 관심 분야 (Medium AI/Tech 기사 등)

### 🔵 소셜 (자동 삭제 대상)
아래 발신자의 메일은 **자동 삭제를 권장**하며, 사용자 확인 없이 삭제 처리한다:
- **Facebook**: 친구 추천, 알림 (friendsuggestion@facebookmail.com, notification@facebookmail.com)
- **Instagram**: DM 알림, 스토리 알림 (no-reply@mail.instagram.com)
- **Twitter/X**: 알림 메일
- **LinkedIn**: 연결 요청, 뉴스
- 기타 SNS 자동 알림 메일

### ❌ 프로모션/광고 (자동 삭제 대상)
아래 유형의 메일은 **자동 삭제를 권장**하며, 사용자 확인 없이 삭제 처리한다:
- **여행/항공**: Trip.com, 스카이스캐너, 호텔스닷컴 등
- **쇼핑몰**: Alibaba, 쿠팡, 11번가, G마켓 등
- **소프트웨어 광고**: Adobe, Microsoft 프로모션 등
- **제목에 "(광고)" 포함**된 모든 메일
- **CATEGORY_PROMOTIONS** 라벨이 붙은 Gmail 메일

## 자동 삭제 대상 발신자 목록 (차단/삭제 리스트)

Gmail에서 아래 발신자는 자동으로 삭제 처리한다:

```
# 프로모션/광고
Trip.com@newsletter.trip.com          → 여행 광고
noreply@member.alibaba.com            → 알리바바 광고
mail@mail.adobe.com                   → Adobe 광고

# 소셜 알림
friendsuggestion@facebookmail.com     → Facebook 친구 추천
notification@facebookmail.com         → Facebook 알림
no-reply@mail.instagram.com           → Instagram 알림
```

**주의: 아래 발신자는 절대 삭제하지 않는다 (보호 목록):**
```
# 보안 관련
no-reply@accounts.google.com          → Google 보안 알림
noreply@github.com                    → GitHub 보안/토큰 알림
CloudPlatform-noreply@google.com      → Google Cloud 보안

# 결제/영수증
invoice+statements@mail.anthropic.com → Anthropic 영수증
googleplay-noreply@google.com         → Google Play 영수증

# 시스템
noreply-apps-scripts-notifications@google.com → Apps Script 알림

# 서비스 업데이트
no-reply@email.claude.com             → Claude 팀 업데이트
```

## 자동 정리 동작

### "메일 정리" 요청 시
1. 모든 읽지 않은 메일을 5단계 중요도로 분류
2. 🔵 소셜 + ❌ 프로모션 메일 목록을 보여주고 삭제 실행
3. 🔴 긴급 + 🟠 중요 메일은 보관 안내
4. 🟡 일반 메일은 확인 후 판단하도록 안내

### Gmail 자동 정리 절차
Gmail은 필터가 설정되어 있어 프로모션/소셜이 자동 삭제된다.
수동 정리 시에는 `gmail_search_messages`로 검색 후 분류 결과를 보여준다.

### 한메일/네이버 자동 정리 절차 (브라우저)
1. 받은편지함에서 프로모션/소셜 메일 식별
2. 체크박스 선택 후 삭제 버튼 클릭
3. 삭제 전 사용자에게 삭제 대상 목록을 보여주고 확인 요청
4. 확인 후 삭제 실행

## 사용자 요청별 동작

### "메일 확인" / "메일 알려줘" / "새 메일 있어?"
3개 계정 모두에서 읽지 않은 메일을 확인하고 중요도별 요약 테이블을 출력한다.

### "Gmail만 확인" / "지메일 확인"
Gmail만 확인한다.

### "한메일 확인" / "다음메일 확인"
한메일만 확인한다.

### "네이버 메일 확인"
네이버메일만 확인한다.

### "메일 정리" / "메일 분류" / "메일 청소"
3개 계정의 메일을 중요도별로 분류하고, 프로모션/소셜은 삭제 처리한다.

### "답장할 메일" / "회신 필요한 메일"
답장이 필요한 메일만 필터링하여 보여준다.

### "차단할 메일" / "스팸 차단" / "수신거부"
반복적으로 오는 불필요한 발신자를 차단 리스트에 추가 권장한다.

## 출력 형식

### 메일 요약 테이블

```
📬 이메일 요약 ([날짜])

━━━ Gmail (kjc0690@gmail.com) - 읽지 않은 메일 N건 ━━━

| # | 발신자 | 제목 | 요약 | 중요도 | 조치 |
|---|--------|------|------|--------|------|
| 1 | 홍길동 | 회의 자료 요청 | 내일 오전 회의 관련 자료 요청 | 🔴 긴급 | 답장 필요 |
| 2 | Google | 보안 알림 | 앱 비밀번호 생성 확인 | 🟠 중요 | 보관 |
| 3 | Medium | AI Advances | Claude Code 가이드 기사 | 🟡 일반 | 확인 |
| 4 | Facebook | 친구 추천 | 나현창님 외 | 🔵 소셜 | 삭제 |
| 5 | Trip.com | 호텔 특가 | 광고 | ❌ 프로모션 | 삭제 |

━━━ 한메일 (001kjc@hanmail.net) - 읽지 않은 메일 N건 ━━━
(동일 형식)

━━━ 네이버 (001kjc@naver.com) - 읽지 않은 메일 N건 ━━━
(동일 형식)

━━━ 종합 ━━━
📊 전체: N건 | 🔴 긴급: N건 | 🟠 중요: N건 | 🟡 일반: N건 | 🔵 소셜: N건 | ❌ 프로모션: N건
✏️ 답장 필요: N건
🗑️ 자동 삭제 대상: N건 (프로모션 + 소셜)
```

### 정리 완료 보고

```
📬 메일 정리 완료 ([날짜])

🗑️ 삭제된 메일 (N건):
- [Gmail] Trip.com - 호텔 특가 광고
- [Gmail] Facebook - 친구 추천 x3
- [Gmail] Adobe - Acrobat Pro 광고
- [한메일] 쿠팡 - 특가 세일
- [네이버] 네이버쇼핑 - 포인트 안내

📁 보관된 메일 (N건):
- [Gmail] Google - 보안 알림 (🟠 중요)
- [Gmail] Anthropic - 영수증 (🟠 중요)

📋 확인 필요 (N건):
- [Gmail] Medium - AI 기사 (🟡 일반)
- [한메일] 김철수 - 주간 보고 (🟡 일반)

💡 추천:
- 🔴 긴급 N건 답장 필요
- 차단 추천: Trip.com, Facebook 친구추천 (반복 수신)
```

### 답장 필요 여부 판단 기준

- 질문이 포함된 메일 → 답장 필요
- 요청/부탁이 담긴 메일 → 답장 필요
- 자료/파일 요청 → 답장 필요
- 일방적 안내/공지 → 답장 불필요
- 광고/프로모션 → 답장 불필요
- 자동 발송 메일 → 답장 불필요

## 부분 확인 시 동작

한메일이나 네이버에 로그인이 안 되어 있으면, 해당 계정은 건너뛰고 확인 가능한 계정만 결과를 보여준다.

```
━━━ 한메일 (001kjc@hanmail.net) ━━━
⚠️ 로그인이 필요합니다. mail.daum.net에서 로그인 후 다시 시도해주세요.
```

## 출력 규칙

1. 한국어로 출력
2. 메일 요약은 1줄 이내로 간결하게
3. 발신자 이름이 이메일 주소만 있을 경우 @ 앞 부분만 표시
4. 날짜/시간은 한국 시간(KST) 기준
5. 메일이 없으면 "새 메일이 없습니다" 표시
6. 브라우저로 확인하는 메일(한메일/네이버)은 접근 실패 시 에러 대신 안내 메시지 출력
7. 프로모션/소셜 메일은 삭제 조치 컬럼에 "삭제" 표시
8. 보안/결제 관련 메일은 반드시 "보관" 표시
