"""
IMAP으로 한메일/네이버메일 읽지 않은 메일을 가져오는 스크립트
사용법:
  python check_imap_mail.py          # 둘 다 확인
  python check_imap_mail.py hanmail  # 한메일만
  python check_imap_mail.py naver    # 네이버만
"""
import imaplib
import email
from email.header import decode_header
import json
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .env 로드
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    # dotenv 없으면 직접 파싱
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


def decode_mime_header(header_value):
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            for enc in [charset, 'utf-8', 'euc-kr', 'cp949', 'iso-8859-1']:
                if enc:
                    try:
                        result.append(part.decode(enc))
                        break
                    except (LookupError, UnicodeDecodeError):
                        continue
            else:
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(part)
    return ' '.join(result)


def parse_date(date_str):
    if not date_str:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return date_str[:20]


def check_imap_unread(server, port, email_addr, password, max_count=20):
    try:
        mail = imaplib.IMAP4_SSL(server, port, timeout=30)
        mail.login(email_addr, password)
        mail.select('INBOX')

        status, data = mail.search(None, 'UNSEEN')
        if status != 'OK':
            mail.logout()
            return {"status": "error", "email": email_addr, "error": "메일 검색 실패"}

        mail_ids = data[0].split()
        unread_count = len(mail_ids)

        # 최신 메일부터 max_count개만
        recent_ids = mail_ids[-max_count:] if len(mail_ids) > max_count else mail_ids
        recent_ids = list(reversed(recent_ids))

        mails = []
        for mid in recent_ids:
            status, msg_data = mail.fetch(mid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
            if status != 'OK':
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            from_addr = decode_mime_header(msg.get('From', ''))
            subject = decode_mime_header(msg.get('Subject', ''))
            date_str = parse_date(msg.get('Date', ''))

            mails.append({
                "from": from_addr,
                "subject": subject,
                "date": date_str
            })

        mail.logout()

        return {
            "status": "ok",
            "email": email_addr,
            "unread_count": unread_count,
            "mails": mails
        }

    except imaplib.IMAP4.error as e:
        return {"status": "error", "email": email_addr, "error": f"IMAP 오류: {str(e)}"}
    except Exception as e:
        return {"status": "error", "email": email_addr, "error": f"접속 실패: {str(e)}"}


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['hanmail', 'naver']
    results = {}

    if 'hanmail' in targets:
        results['hanmail'] = check_imap_unread(
            'imap.daum.net', 993,
            os.getenv('HANMAIL_EMAIL', ''),
            os.getenv('HANMAIL_APP_PASSWORD', '')
        )

    if 'naver' in targets:
        results['naver'] = check_imap_unread(
            'imap.naver.com', 993,
            os.getenv('NAVER_EMAIL', ''),
            os.getenv('NAVER_APP_PASSWORD', '')
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
