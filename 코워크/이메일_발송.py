import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

GMAIL_USER = "kjc0690@gmail.com"
GMAIL_APP_PASSWORD = "cgycwdduzembwxdq"

# ===== 여기서 설정 =====
to = "admin@idfkorea.co.kr"
subject = "[TBM] 안전 TBM 회의록_20260321"
body = """안녕하세요,

오늘(2026년 3월 21일) TBM 안전 회의록을 첨부하여 드립니다.

확인 부탁드립니다.

감사합니다."""
file_path = os.path.join(os.path.dirname(__file__), "업무자동화", "TBM", "회의록", "TBM_회의록_20260321.xlsx")
# ====================

msg = MIMEMultipart()
msg['From'] = GMAIL_USER
msg['To'] = to
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain', 'utf-8'))

if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
        msg.attach(part)
    print(f"첨부: {os.path.basename(file_path)}")
else:
    print(f"파일 없음: {file_path}")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"\n✅ 발송 완료!")
    print(f"   받는 사람: {to}")
    print(f"   제목: {subject}")
except Exception as e:
    print(f"\n❌ 발송 실패: {e}")

input("\n엔터를 누르면 창이 닫힙니다...")
