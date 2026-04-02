#!/usr/bin/env python3
"""한메일(Daum) SMTP를 통한 이메일 발송 스크립트
발신자: 001kjc@hanmail.net
첨부파일 필수
"""

import smtplib
import imaplib
import argparse
import sys
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


# 한메일 SMTP/IMAP 설정
SMTP_SERVER = "smtp.daum.net"
SMTP_PORT = 465
IMAP_SERVER = "imap.daum.net"
IMAP_PORT = 993
SMTP_USER = "001kjc"
SMTP_PASSWORD = os.environ.get("HANMAIL_APP_PASSWORD", "")
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
            # 한글 파일명 인코딩 (RFC 2231)
            from email.utils import encode_rfc2231
            encoded_name = encode_rfc2231(filename, 'utf-8')
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=(('utf-8', '', filename)),
            )
            part.add_header(
                "Content-Type",
                "application/octet-stream",
                name=(('utf-8', '', filename)),
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

    # IMAP으로 보낸편지함에 저장
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap.login(SMTP_USER, SMTP_PASSWORD)
        imap.append('"Sent Messages"', '(\\Seen)', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        print(f"\n[성공] 이메일 발송 완료! (보낸편지함 저장됨)")
    except Exception as e:
        print(f"\n[성공] 이메일 발송 완료! (보낸편지함 저장 실패: {e})")

    print(f"   발신자: {SENDER_EMAIL}")
    print(f"   받는 사람: {to}")
    if cc:
        print(f"   참조: {cc}")
    print(f"   제목: {subject}")


def show_confirmation(to, subject, body, attachments, cc=None):
    """발송 전 확인 화면 표시"""
    print()
    print("=" * 40)
    print("  [이메일 발송 확인]")
    print("=" * 40)
    print(f"발신: {SENDER_EMAIL}")
    print(f"수신: {to}")
    if cc:
        print(f"참조: {cc}")
    print(f"제목: {subject}")
    print("-" * 20 + " 본문 " + "-" * 20)
    print(body)
    print("-" * 20 + " 첨부 " + "-" * 20)
    if attachments:
        for i, f in enumerate(attachments, 1):
            p = Path(f)
            if p.exists():
                size_kb = p.stat().st_size / 1024
                print(f"{i}. {p.name} ({size_kb:.1f} KB)")
            else:
                print(f"{i}. {p.name} (파일 없음!)")
    else:
        print("(첨부파일 없음)")
    print("=" * 40)
    return True


def main():
    parser = argparse.ArgumentParser(description="한메일 이메일 발송")
    parser.add_argument("--to", required=True, help="받는 사람 이메일")
    parser.add_argument("--subject", required=True, help="메일 제목")
    parser.add_argument("--body", required=True, help="메일 본문")
    parser.add_argument("--attach", nargs="+", help="첨부파일 경로")
    parser.add_argument("--cc", help="참조 이메일")
    parser.add_argument("--html", action="store_true", help="HTML 본문 여부")
    parser.add_argument("--confirm", action="store_true", help="확인 화면만 표시 (발송 안 함)")
    parser.add_argument("--yes", action="store_true", help="확인 없이 바로 발송")

    args = parser.parse_args()
    attachments = args.attach or []

    # 확인 화면 표시
    show_confirmation(args.to, args.subject, args.body, attachments, args.cc)

    if args.confirm:
        print("\n[미리보기] 확인 화면만 표시합니다. 발송하려면 --yes 옵션을 추가하세요.")
        return

    if not args.yes:
        print("\n발송하시겠습니까? (y/n): ", end="")
        answer = input().strip().lower()
        if answer not in ("y", "yes", "예"):
            print("[취소] 발송을 취소했습니다.")
            return

    send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        attachments=attachments,
        cc=args.cc,
        html=args.html,
    )


if __name__ == "__main__":
    main()
