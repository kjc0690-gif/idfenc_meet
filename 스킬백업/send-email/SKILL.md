---
name: send-email
description: 한메일(001kjc@hanmail.net)로 파일 첨부 이메일 발송. "회사메일로 보내줘" = admin@idfkorea.co.kr
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

## 사용법

사용자가 이메일 발송을 요청하면:

1. **수신자 확인**: "회사메일"이면 admin@idfkorea.co.kr, 그 외는 직접 지정
2. **첨부파일 찾기**: 사용자가 지정한 파일을 Glob으로 검색
3. **발송 전 확인 (필수)**: 아래 내용을 사용자에게 보여주고 승인받기
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
4. **발송 실행**:

```bash
python "C:/Users/kjc06/클로드 작업기록/idfenc_meet/email-results/scripts/send_email.py" \
  --to "수신자@email.com" \
  --subject "제목" \
  --body "본문 내용" \
  --attach "파일1.xlsx" "파일2.xlsx"
```

## 인자 파싱

$ARGUMENTS 에서 다음을 추출:
- 수신자 이메일 또는 "회사메일" 키워드
- 첨부할 파일명 또는 검색 키워드

## 주의사항
- Gmail 사용 금지 - 모든 발송은 한메일(001kjc@hanmail.net)로만
- 첨부파일 없이는 발송하지 않음
- 참조(CC) 추가 시 `--cc` 옵션 사용
