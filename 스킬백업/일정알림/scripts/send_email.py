"""Gmail SMTP를 이용한 이메일 발송 스크립트"""
import smtplib
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "kjc0690@gmail.com"
APP_PASSWORD = "cgyc wddu zemb wxdq"


def send_email(to_email: str, subject: str, body: str) -> dict:
    """이메일을 발송한다."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Claude 캘린더 알림 <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return {"success": True, "message": f"이메일 발송 완료: {to_email}"}
    except Exception as e:
        return {"success": False, "message": f"발송 실패: {str(e)}"}


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"success": False, "message": "Usage: send_email.py <to> <subject> <body>"}))
        sys.exit(1)

    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    result = send_email(to, subject, body)
    print(json.dumps(result, ensure_ascii=False))
