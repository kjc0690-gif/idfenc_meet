---
name: send-email
description: 한메일(001kjc@hanmail.net)로 파일 첨부 이메일 발송. "회사메일로 보내줘" = admin@idfkorea.co.kr. 사람 이름으로 보내면 연락처 엑셀에서 이메일 자동 조회.
argument-hint: [수신자 또는 "회사메일"] [파일경로]
allowed-tools: [Bash, Read, Glob, Grep]
---

# 이메일 발송 스킬 (한메일 전용)

## 발신 정보
- **발신자**: 001kjc@hanmail.net (한메일/Daum)
- **SMTP**: smtp.daum.net:465 (SSL)
- **첨부파일**: 필수 (첨부 없이 발송 불가)

## 수신자 단축어
- "회사메일로 보내줘" → admin@idfkorea.co.kr

## 연락처 참조 (핵심!)

**연락처 엑셀 파일**: `G:\내 드라이브\클로드작업기록\영업자료\연락처.xlsx`

| 컬럼 | 내용 |
|------|------|
| 이름 | 수신자 이름 |
| 직책 | 직책 |
| 회사 | 소속 회사 |
| 부서 | 부서 |
| 모바일 | 모바일 번호 |
| 전화 | 전화번호 |
| 팩스 | 팩스번호 |
| 이메일 | 이메일 주소 |
| 주소 | 주소 |
| 등록일 | 등록일 |

### 수신자 확인 절차
1. 사용자가 **사람 이름**으로 요청하면 → 연락처 엑셀에서 이름 검색하여 이메일 주소 자동 조회
2. "회사메일"이면 → admin@idfkorea.co.kr
3. 이메일 주소 직접 지정 → 그대로 사용
4. **연락처에 없는 새 사람**이면 → 사용자에게 이메일 주소를 물어보고, 연락처 엑셀에 추가(이름, 회사, 이메일, 등록일)한 후 발송

## 사용법

사용자가 이메일 발송을 요청하면:

1. **수신자 확인**: 위 "수신자 확인 절차"에 따라 이메일 주소 확보
2. **연락처 업데이트**: 처음 보내는 사람이면 연락처 엑셀에 추가
3. **첨부파일 찾기**: 사용자가 지정한 파일을 Glob으로 검색
4. **발송 전 확인 (필수)**: 아래 내용을 사용자에게 보여주고 승인받기
   ```
   ═══════════════════════════════
     📧 이메일 발송 확인
   ═══════════════════════════════
   발신: 001kjc@hanmail.net
   수신: (수신자 이메일)
   제목: (제목)
   ───────── 본문 ─────────
   (본문 내용 전체를 생략 없이 표시)
   ───────── 첨부 ─────────
   1. 파일명1.xlsx (00 KB)
   2. 파일명2.xlsx (00 KB)
   ═══════════════════════════════
   발송하시겠습니까? (Y/N)
   ```
   - 사용자가 승인(Y, 네, 보내, 확인 등)하면 발송 실행
   - 사용자가 거부하면 수정사항 확인 후 재작성
5. **발송 실행**:

```bash
python "C:/Users/note/Desktop/클로드_작업기록/email-results/scripts/send_email.py" \
  --to "수신자@email.com" \
  --subject "제목" \
  --body "본문 내용" \
  --attach "파일1.xlsx" "파일2.xlsx"
```

## 연락처 엑셀 읽기/쓰기 예시

### 이름으로 이메일 조회
```python
import pandas as pd
df = pd.read_excel('G:/내 드라이브/클로드작업기록/영업자료/연락처.xlsx', dtype=str)
match = df[df['이름'].str.contains('이준호', na=False)]
email = match.iloc[0]['이메일']  # yijuno.yi@samsung.com
```

### 새 연락처 추가
```python
from openpyxl import load_workbook
from copy import copy
wb = load_workbook('G:/내 드라이브/클로드작업기록/영업자료/연락처.xlsx')
ws = wb.active
next_row = ws.max_row + 1
ws.cell(row=next_row, column=1, value='이름')
ws.cell(row=next_row, column=3, value='회사')
ws.cell(row=next_row, column=8, value='email@example.com')
ws.cell(row=next_row, column=10, value='2026-04-05')
wb.save('G:/내 드라이브/클로드작업기록/영업자료/연락처.xlsx')
```

## 인자 파싱

$ARGUMENTS 에서 다음을 추출:
- 수신자 이름, 이메일 또는 "회사메일" 키워드
- 첨부할 파일명 또는 검색 키워드

## 주의사항
- Gmail 사용 금지 - 모든 발송은 한메일(001kjc@hanmail.net)로만
- 첨부파일 없이는 발송하지 않음
- 참조(CC) 추가 시 `--cc` 옵션 사용
- 연락처 엑셀 수정 시 파일이 엑셀에서 열려있으면 저장 불가 → 닫아달라고 안내
