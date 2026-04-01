"""
방수명장 AS 시스템 - Google Drive API 클라이언트

구글드라이브에 AS 케이스 데이터를 자동 백업하는 모듈.
폴더 생성, JSON 업로드, 이미지 업로드 등을 담당한다.
"""

import os
import io
import json
import base64
import logging
import re
from datetime import datetime
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

# Google Drive API 스코프 - drive.file: 앱이 생성한 파일만 접근
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveClient:
    """Google Drive API를 래핑한 클라이언트 클래스."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        root_folder_name: str = "방수명장AS백업",
        token_path: str = "token.json",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.root_folder_name = root_folder_name
        self.token_path = token_path
        self.creds: Optional[Credentials] = None
        self.service = None
        # 폴더 ID 캐시 (검색 횟수 줄이기)
        self._folder_cache: dict[str, str] = {}

        self._try_load_credentials()

    # ──────────────────────────────────────────────
    # 인증 관련
    # ──────────────────────────────────────────────

    def _try_load_credentials(self) -> None:
        """token.json이 있으면 인증 정보를 로드한다."""
        if not os.path.exists(self.token_path):
            return

        try:
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self._save_token()
            if self.creds and self.creds.valid:
                self.service = build("drive", "v3", credentials=self.creds)
                logger.info("Google Drive 인증 정보 로드 완료")
        except Exception as e:
            logger.warning("토큰 로드 실패, 재인증 필요: %s", e)
            self.creds = None
            self.service = None

    def _save_token(self) -> None:
        """현재 인증 정보를 token.json에 저장한다."""
        with open(self.token_path, "w", encoding="utf-8") as f:
            f.write(self.creds.to_json())
        logger.info("토큰 저장 완료: %s", self.token_path)

    def _build_flow(self) -> Flow:
        """OAuth Flow 객체를 생성한다."""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri],
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = self.redirect_uri
        return flow

    def get_authorization_url(self) -> str:
        """OAuth 인증 URL을 생성한다."""
        flow = self._build_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        logger.info("인증 URL 생성 완료")
        return auth_url

    def authenticate(self, code: str) -> bool:
        """OAuth 코드로 인증을 완료하고 토큰을 저장한다."""
        try:
            flow = self._build_flow()
            flow.fetch_token(code=code)
            self.creds = flow.credentials
            self._save_token()
            self.service = build("drive", "v3", credentials=self.creds)
            logger.info("Google Drive 인증 성공")
            return True
        except Exception as e:
            logger.error("인증 실패: %s", e)
            return False

    def is_authenticated(self) -> bool:
        """인증 상태를 반환한다."""
        return self.creds is not None and self.creds.valid and self.service is not None

    # ──────────────────────────────────────────────
    # 폴더 관리
    # ──────────────────────────────────────────────

    @staticmethod
    def sanitize_name(name: str) -> str:
        """파일/폴더명에 사용할 수 없는 문자를 제거한다."""
        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        safe = re.sub(r"\s+", "_", safe).strip("_")
        return safe or "untitled"

    def _find_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """이름으로 폴더를 검색한다. 캐시를 먼저 확인."""
        cache_key = f"{parent_id or 'root'}:{name}"
        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]

        query = (
            f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"

        try:
            results = (
                self.service.files()
                .list(q=query, spaces="drive", fields="files(id, name)", pageSize=1)
                .execute()
            )
            files = results.get("files", [])
            if files:
                folder_id = files[0]["id"]
                self._folder_cache[cache_key] = folder_id
                return folder_id
        except Exception as e:
            logger.error("폴더 검색 실패 '%s': %s", name, e)
        return None

    def _create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """새 폴더를 생성하고 ID를 반환한다."""
        metadata: dict = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        try:
            folder = self.service.files().create(body=metadata, fields="id").execute()
            folder_id = folder["id"]
            cache_key = f"{parent_id or 'root'}:{name}"
            self._folder_cache[cache_key] = folder_id
            logger.info("폴더 생성: %s (ID: %s)", name, folder_id)
            return folder_id
        except Exception as e:
            logger.error("폴더 생성 실패 '%s': %s", name, e)
            raise

    def get_or_create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """폴더가 있으면 ID를, 없으면 생성 후 ID를 반환한다."""
        existing = self._find_folder(name, parent_id)
        if existing:
            return existing
        return self._create_folder(name, parent_id)

    def get_root_folder_id(self) -> str:
        """루트 백업 폴더('방수명장AS백업')의 ID를 반환한다."""
        return self.get_or_create_folder(self.root_folder_name)

    def create_folder_structure(self, site_name: str, case_id: str) -> dict[str, str]:
        """
        현장/케이스 폴더 구조를 생성한다.

        반환값:
            {
                "root": ...,
                "site": ...,
                "case": ...,
                "공문": ...,
                "활동기록": ...,
                "시공일지": ...,
                "완료검사": ...
            }
        """
        safe_site = self.sanitize_name(site_name)
        root_id = self.get_root_folder_id()
        site_id = self.get_or_create_folder(safe_site, root_id)
        case_id_folder = self.get_or_create_folder(case_id, site_id)

        sub_folders = {}
        for sub_name in ["공문", "활동기록", "시공일지", "완료검사"]:
            sub_folders[sub_name] = self.get_or_create_folder(sub_name, case_id_folder)

        result = {
            "root": root_id,
            "site": site_id,
            "case": case_id_folder,
            **sub_folders,
        }
        logger.info(
            "폴더 구조 생성 완료: %s/%s (하위폴더 %d개)", safe_site, case_id, len(sub_folders)
        )
        return result

    # ──────────────────────────────────────────────
    # 파일 업로드
    # ──────────────────────────────────────────────

    def _find_file(self, name: str, parent_id: str) -> Optional[str]:
        """부모 폴더에서 파일명으로 검색한다."""
        query = f"name='{name}' and '{parent_id}' in parents and trashed=false"
        try:
            results = (
                self.service.files()
                .list(q=query, spaces="drive", fields="files(id)", pageSize=1)
                .execute()
            )
            files = results.get("files", [])
            return files[0]["id"] if files else None
        except Exception as e:
            logger.error("파일 검색 실패 '%s': %s", name, e)
            return None

    def upload_json(self, data: dict, folder_id: str, filename: str) -> str:
        """
        JSON 데이터를 구글드라이브에 업로드한다.
        같은 이름의 파일이 있으면 덮어쓴다.
        """
        json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        media = MediaInMemoryUpload(json_bytes, mimetype="application/json")

        existing_id = self._find_file(filename, folder_id)
        try:
            if existing_id:
                # 기존 파일 업데이트
                result = (
                    self.service.files()
                    .update(fileId=existing_id, media_body=media, fields="id")
                    .execute()
                )
                logger.info("JSON 업데이트: %s (ID: %s)", filename, result["id"])
            else:
                # 새 파일 생성
                metadata = {"name": filename, "parents": [folder_id]}
                result = (
                    self.service.files()
                    .create(body=metadata, media_body=media, fields="id")
                    .execute()
                )
                logger.info("JSON 업로드: %s (ID: %s)", filename, result["id"])
            return result["id"]
        except Exception as e:
            logger.error("JSON 업로드 실패 '%s': %s", filename, e)
            raise

    def upload_base64_image(self, base64_data: str, folder_id: str, filename: str) -> str:
        """
        Base64 인코딩된 이미지를 JPG로 변환하여 업로드한다.
        'data:image/...;base64,' 접두어가 있으면 자동 제거.
        """
        # data URL 접두어 제거
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]

        image_bytes = base64.b64decode(base64_data)

        # 확장자로 mimetype 결정
        ext = os.path.splitext(filename)[1].lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mimetype = mime_map.get(ext, "image/jpeg")

        media = MediaInMemoryUpload(image_bytes, mimetype=mimetype)

        existing_id = self._find_file(filename, folder_id)
        try:
            if existing_id:
                result = (
                    self.service.files()
                    .update(fileId=existing_id, media_body=media, fields="id")
                    .execute()
                )
                logger.info("이미지 업데이트: %s (ID: %s)", filename, result["id"])
            else:
                metadata = {"name": filename, "parents": [folder_id]}
                result = (
                    self.service.files()
                    .create(body=metadata, media_body=media, fields="id")
                    .execute()
                )
                logger.info("이미지 업로드: %s (ID: %s)", filename, result["id"])
            return result["id"]
        except Exception as e:
            logger.error("이미지 업로드 실패 '%s': %s", filename, e)
            raise

    # ──────────────────────────────────────────────
    # 조회
    # ──────────────────────────────────────────────

    def list_sites(self) -> list[dict]:
        """루트 폴더 아래의 현장(사이트) 목록을 반환한다."""
        root_id = self.get_root_folder_id()
        query = f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="files(id, name, createdTime, modifiedTime)",
                    orderBy="name",
                    pageSize=100,
                )
                .execute()
            )
            sites = results.get("files", [])
            logger.info("현장 목록 조회: %d건", len(sites))
            return sites
        except Exception as e:
            logger.error("현장 목록 조회 실패: %s", e)
            raise

    def list_cases(self, site_name: str) -> list[dict]:
        """특정 현장의 AS 케이스 목록을 반환한다."""
        root_id = self.get_root_folder_id()
        safe_site = self.sanitize_name(site_name)
        site_id = self._find_folder(safe_site, root_id)
        if not site_id:
            return []

        query = f"'{site_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="files(id, name, createdTime, modifiedTime)",
                    orderBy="createdTime desc",
                    pageSize=100,
                )
                .execute()
            )
            return results.get("files", [])
        except Exception as e:
            logger.error("케이스 목록 조회 실패 '%s': %s", site_name, e)
            raise

    # ──────────────────────────────────────────────
    # 통합 백업
    # ──────────────────────────────────────────────

    def backup_case(self, case_data: dict) -> dict:
        """
        AS 케이스 전체를 구글드라이브에 백업한다.

        1. 폴더 구조 생성
        2. 기본정보 JSON 업로드
        3. 타임스탬프 전체 백업 JSON 업로드
        4. 공문 사진 업로드
        5. 활동기록 사진 업로드
        6. 시공일지 사진 업로드

        반환값: { "success": True, "folders": {...}, "uploaded_files": [...] }
        """
        metadata = case_data.get("metadata", {})
        site_name = metadata.get("siteName", "알수없는현장")
        case_id = metadata.get("caseId", "UNKNOWN")

        logger.info("백업 시작: %s / %s", site_name, case_id)

        # 1. 폴더 구조 생성
        folders = self.create_folder_structure(site_name, case_id)
        uploaded_files = []

        # 2. 기본정보 JSON (사진 base64 제외한 가벼운 버전)
        light_data = self._strip_base64(case_data)
        file_id = self.upload_json(light_data, folders["case"], "기본정보.json")
        uploaded_files.append({"name": "기본정보.json", "id": file_id})

        # 3. 타임스탬프 전체 백업
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_backup_name = f"전체백업_{now_str}.json"
        file_id = self.upload_json(light_data, folders["case"], full_backup_name)
        uploaded_files.append({"name": full_backup_name, "id": file_id})

        # 4. 공문 사진 업로드
        doc_files = case_data.get("document", {}).get("files", [])
        for doc in doc_files:
            b64 = doc.get("base64", "")
            if not b64:
                continue
            fname = doc.get("name", f"공문_{doc.get('id', 'unknown')}.jpg")
            try:
                fid = self.upload_base64_image(b64, folders["공문"], fname)
                uploaded_files.append({"name": f"공문/{fname}", "id": fid})
            except Exception as e:
                logger.warning("공문 사진 업로드 실패 '%s': %s", fname, e)

        # 5. 활동기록 사진 업로드
        activities = case_data.get("activities", [])
        for act in activities:
            seq = act.get("sequence", 0)
            act_type = act.get("type", "활동")
            act_folder_name = f"{seq}차_{self.sanitize_name(act_type)}"
            act_folder_id = self.get_or_create_folder(act_folder_name, folders["활동기록"])

            # 회의록 JSON
            if act.get("minutes"):
                fid = self.upload_json(act["minutes"], act_folder_id, "회의록.json")
                uploaded_files.append({"name": f"활동기록/{act_folder_name}/회의록.json", "id": fid})

            # 사진
            for i, photo in enumerate(act.get("photos", [])):
                b64 = photo.get("base64", "")
                if not b64:
                    continue
                caption = self.sanitize_name(photo.get("caption", f"사진{i+1}"))
                fname = f"사진{i+1}_{caption}.jpg"
                try:
                    fid = self.upload_base64_image(b64, act_folder_id, fname)
                    uploaded_files.append(
                        {"name": f"활동기록/{act_folder_name}/{fname}", "id": fid}
                    )
                except Exception as e:
                    logger.warning("활동 사진 업로드 실패: %s", e)

        # 6. 시공일지 사진 업로드
        construction = case_data.get("construction", {})
        daily_logs = construction.get("dailyLogs", [])
        for log in daily_logs:
            day = log.get("day", 0)
            log_folder_name = f"{day}일차"
            log_folder_id = self.get_or_create_folder(log_folder_name, folders["시공일지"])

            # 일지 JSON
            log_copy = {k: v for k, v in log.items() if k != "photos"}
            fid = self.upload_json(log_copy, log_folder_id, f"일지_{log.get('date', 'unknown')}.json")
            uploaded_files.append({"name": f"시공일지/{log_folder_name}/일지.json", "id": fid})

            # 작업 사진
            for i, photo in enumerate(log.get("photos", [])):
                b64 = photo.get("base64", "")
                if not b64:
                    continue
                caption = self.sanitize_name(photo.get("caption", f"작업{i+1}"))
                fname = f"작업{i+1}_{caption}.jpg"
                try:
                    fid = self.upload_base64_image(b64, log_folder_id, fname)
                    uploaded_files.append(
                        {"name": f"시공일지/{log_folder_name}/{fname}", "id": fid}
                    )
                except Exception as e:
                    logger.warning("시공 사진 업로드 실패: %s", e)

        logger.info("백업 완료: 파일 %d개 업로드", len(uploaded_files))

        return {
            "success": True,
            "siteName": site_name,
            "caseId": case_id,
            "folders": {k: v for k, v in folders.items()},
            "uploadedFiles": uploaded_files,
            "uploadedAt": datetime.now().isoformat(),
        }

    @staticmethod
    def _strip_base64(data: dict) -> dict:
        """
        깊은 복사 후 base64 데이터를 제거한다.
        JSON 파일 크기를 줄이기 위해 사용.
        """
        import copy

        stripped = copy.deepcopy(data)

        # 공문 파일에서 base64 제거
        for doc in stripped.get("document", {}).get("files", []):
            if "base64" in doc:
                doc["base64"] = "(이미지 데이터 - 별도 파일로 저장됨)"

        # 활동 사진에서 base64 제거
        for act in stripped.get("activities", []):
            for photo in act.get("photos", []):
                if "base64" in photo:
                    photo["base64"] = "(이미지 데이터 - 별도 파일로 저장됨)"

        # 시공일지 사진에서 base64 제거
        for log in stripped.get("construction", {}).get("dailyLogs", []):
            for photo in log.get("photos", []):
                if "base64" in photo:
                    photo["base64"] = "(이미지 데이터 - 별도 파일로 저장됨)"

        return stripped
