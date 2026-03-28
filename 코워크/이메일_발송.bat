@echo off
chcp 65001 >nul
echo ============================================
echo   TBM 회의록 이메일 발송합니다!
echo ============================================
echo.

cd /d "%~dp0"

python "%~dp0..\클로드 작업기록\idfenc_meet\email-results\scripts\send_email.py" ^
  --to "admin@idfkorea.co.kr" ^
  --subject "[TBM] 안전 TBM 회의록_20260321" ^
  --body "안녕하세요, 오늘(2026년 3월 21일) TBM 안전 회의록을 첨부하여 드립니다. 확인 부탁드립니다. 감사합니다." ^
  --attach "%~dp0업무자동화\TBM\회의록\TBM_회의록_20260321.xlsx"

echo.
pause
