#!/usr/bin/env python3
"""한메일(Daum) SMTP를 통한 이메일 발송 스크립트
발신자: 001kjc@hanmail.net
첨부파일 필수
"""

import smtplib
import argparse
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


# 한메일 SMTP 설정
SMTP_SERVER = "smtp.daum.net"
SMTP_PORT = 465
SMTP_USER = "001kjc"
SMTP_PASSWORD = "kidyldzzunstbcvt"
SENDER_EMAIL = "001kjc@hanmail.net"


def send_email(to, subject, body, attachments, cc=None, html=False):
    """이메일 발송"""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc

    # 본문
    content_type = "html" if html else "plain"
    msg.attach(MIMEText(body, content_type, "utf-8"))

    # 첨부파일 추가
    for filepath in attachments:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"  [경고] 파일 없음: {filepath}")
            continue

        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)

            filename = filepath.name
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"',
            )
            msg.attach(part)

        size_kb = filepath.stat().st_size / 1024
        print(f"  첨부 완료: {filename} ({size_kb:.1f} KB)")

    # 수신자 목록
    recipients = [addr.strip() for addr in to.split(",")]
    if cc:
        recipients += [addr.strip() for addr in cc.split(",")]

    # SMTP SSL 발송
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

    print(f"\n[성공] 이메일 발송 완료!")
    print(f"   발신자: {SENDER_EMAIL}")
    print(f"   받는 사람: {to}")
    if cc:
        print(f"   참조: {cc}")
    print(f"   제목: {subject}")


def main():
    parser = argparse.ArgumentParser(description="한메일 이메일 발송")
    parser.add_argument("--to", required=True, help="받는 사람 이메일")
    parser.add_argument("--subject", required=True, help="메일 제목")
    parser.add_argument("--body", required=True, help="메일 본문")
    parser.add_argument("--attach", nargs="+", required=True, help="첨부파일 경로 (필수)")
    parser.add_argument("--cc", help="참조 이메일")
    parser.add_argument("--html", action="store_true", help="HTML 본문 여부")

    args = parser.parse_args()

    if not args.attach:
        print("[오류] 첨부파일은 필수입니다.")
        sys.exit(1)

    send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        attachments=args.attach,
        cc=args.cc,
        html=args.html,
    )


if __name__ == "__main__":
    main()
