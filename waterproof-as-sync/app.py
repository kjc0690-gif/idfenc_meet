"""
방수명장 AS 시스템 - Google Drive 자동 백업 서버

Flask 기반 API 서버. HTML 프론트엔드에서 호출하여
AS 케이스 데이터를 자동으로 구글드라이브에 백업한다.

실행: python app.py
"""

import os
import logging
from datetime import datetime

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from dotenv import load_dotenv

from google_drive import GoogleDriveClient

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "True").lower() == "true" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])  # 개발 중 모든 origin 허용

# Google Drive 클라이언트 초기화
drive_client = GoogleDriveClient(
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback"),
    root_folder_name=os.getenv("BACKUP_FOLDER_NAME", "방수명장AS백업"),
)


# ──────────────────────────────────────────────
# API 엔드포인트
# ──────────────────────────────────────────────


@app.route("/api/status", methods=["GET"])
def api_status():
    """Google Drive 인증 상태를 확인한다."""
    authenticated = drive_client.is_authenticated()
    has_credentials = bool(os.getenv("GOOGLE_CLIENT_ID"))

    return jsonify({
        "authenticated": authenticated,
        "ready": authenticated and has_credentials,
        "hasCredentials": has_credentials,
        "serverTime": datetime.now().isoformat(),
    })


@app.route("/api/auth", methods=["GET"])
def api_auth():
    """OAuth 인증 URL을 생성한다."""
    if not os.getenv("GOOGLE_CLIENT_ID"):
        return jsonify({
            "error": "GOOGLE_CLIENT_ID가 설정되지 않았습니다. .env 파일을 확인하세요.",
        }), 400

    try:
        auth_url = drive_client.get_authorization_url()
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        logger.error("인증 URL 생성 실패: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/oauth2callback", methods=["GET"])
def oauth2callback():
    """OAuth 콜백을 처리한다. 구글 인증 후 리디렉션된다."""
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        logger.error("OAuth 에러: %s", error)
        return f"""
        <html><body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1 style="color:red;">❌ 인증 실패</h1>
            <p>에러: {error}</p>
            <p>다시 시도해주세요.</p>
        </body></html>
        """, 400

    if not code:
        return jsonify({"error": "인증 코드가 없습니다."}), 400

    success = drive_client.authenticate(code)
    if success:
        return """
        <html><body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1 style="color:green;">✅ 인증 완료!</h1>
            <p>구글드라이브 연결이 성공적으로 완료되었습니다.</p>
            <p>이 창을 닫고 AS 시스템으로 돌아가세요.</p>
            <script>
                // 5초 후 자동 닫기 시도
                setTimeout(function() { window.close(); }, 5000);
            </script>
        </body></html>
        """
    else:
        return """
        <html><body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1 style="color:red;">❌ 인증 실패</h1>
            <p>토큰 교환에 실패했습니다. 다시 시도해주세요.</p>
        </body></html>
        """, 500


@app.route("/api/backup", methods=["POST"])
def api_backup():
    """AS 케이스 데이터를 구글드라이브에 백업한다."""
    if not drive_client.is_authenticated():
        return jsonify({
            "error": "구글드라이브 인증이 필요합니다. /api/auth로 먼저 인증하세요.",
        }), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "백업할 데이터가 없습니다."}), 400

    metadata = data.get("metadata", {})
    if not metadata.get("caseId") or not metadata.get("siteName"):
        return jsonify({"error": "metadata에 caseId와 siteName이 필요합니다."}), 400

    try:
        result = drive_client.backup_case(data)
        return jsonify(result)
    except Exception as e:
        logger.error("백업 실패: %s", e, exc_info=True)
        return jsonify({"error": f"백업 실패: {str(e)}"}), 500


@app.route("/api/list-sites", methods=["GET"])
def api_list_sites():
    """구글드라이브의 현장 목록을 조회한다."""
    if not drive_client.is_authenticated():
        return jsonify({"error": "인증 필요"}), 401

    try:
        sites = drive_client.list_sites()
        return jsonify({"sites": sites})
    except Exception as e:
        logger.error("현장 목록 조회 실패: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/list-cases/<site_name>", methods=["GET"])
def api_list_cases(site_name: str):
    """특정 현장의 AS 케이스 목록을 조회한다."""
    if not drive_client.is_authenticated():
        return jsonify({"error": "인증 필요"}), 401

    try:
        cases = drive_client.list_cases(site_name)
        return jsonify({"siteName": site_name, "cases": cases})
    except Exception as e:
        logger.error("케이스 목록 조회 실패: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """서버 상태 페이지."""
    auth_status = "✅ 연결됨" if drive_client.is_authenticated() else "❌ 미연결"
    return f"""
    <html>
    <head><meta charset="utf-8"><title>방수명장 AS 백업 서버</title></head>
    <body style="font-family:'Malgun Gothic',sans-serif; max-width:600px; margin:50px auto; padding:20px;">
        <h1>🔧 방수명장 AS 백업 서버</h1>
        <hr>
        <p><strong>서버 상태:</strong> ✅ 실행 중</p>
        <p><strong>구글드라이브:</strong> {auth_status}</p>
        <p><strong>시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <h3>📋 API 목록</h3>
        <ul>
            <li><a href="/api/status">GET /api/status</a> - 인증 상태 확인</li>
            <li><a href="/api/auth">GET /api/auth</a> - 구글 인증 시작</li>
            <li>POST /api/backup - AS 데이터 백업</li>
            <li><a href="/api/list-sites">GET /api/list-sites</a> - 현장 목록</li>
            <li>GET /api/list-cases/&lt;현장명&gt; - 케이스 목록</li>
        </ul>
        <hr>
        <p style="color:gray; font-size:0.9em;">
            방수명장 AS 시스템 v2.0 | (주)아이디에프이앤씨
        </p>
    </body>
    </html>
    """


# ──────────────────────────────────────────────
# 서버 실행
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"

    logger.info("=" * 50)
    logger.info("방수명장 AS 백업 서버 시작")
    logger.info("주소: http://%s:%d", host, port)
    logger.info("인증 상태: %s", "연결됨" if drive_client.is_authenticated() else "미연결")
    logger.info("=" * 50)

    app.run(host=host, port=port, debug=debug)
