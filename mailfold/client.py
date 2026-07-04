from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from .errors import MailfoldAPIError, MailfoldConnectionError
from .models import (
    AttachmentContent,
    Folder,
    Message,
    MessageHeader,
    SendResult,
)


class Client:
    """Client for the Mailfold REST API.

    Construct with the base URL of your Mailfold instance and a per-mailbox
    API key (a bearer token, e.g. "mf_live_...").
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def send(
        self,
        to: Optional[list] = None,
        cc: Optional[list] = None,
        bcc: Optional[list] = None,
        subject: str = "",
        text: str = "",
        html: str = "",
    ) -> SendResult:
        body = {
            "to": to or [],
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "text": text,
            "html": html,
        }
        data = self._request("POST", "/api/v1/mail/send", json_body=body)
        return SendResult.from_dict(data)

    def folders(self) -> list:
        data = self._request("GET", "/api/v1/mail/folders")
        return [Folder.from_dict(f) for f in data]

    def messages(self, folder: Optional[str] = None, limit: Optional[int] = None) -> list:
        params = {}
        if folder is not None:
            params["folder"] = folder
        if limit is not None:
            params["limit"] = limit
        data = self._request("GET", "/api/v1/mail/messages", query=params)
        return [MessageHeader.from_dict(m) for m in data]

    def message(self, folder: str, uid: int) -> Message:
        params = {"folder": folder, "uid": uid}
        data = self._request("GET", "/api/v1/mail/message", query=params)
        return Message.from_dict(data)

    def delete_message(self, folder: str, uid: int) -> None:
        self._request("DELETE", "/api/v1/mail/message", json_body={"folder": folder, "uid": uid})

    def search(self, folder: Optional[str] = None, q: str = "") -> list:
        params = {"q": q}
        if folder is not None:
            params["folder"] = folder
        data = self._request("GET", "/api/v1/mail/search", query=params)
        return [MessageHeader.from_dict(m) for m in data]

    def attachment(self, folder: str, uid: int, index: int) -> AttachmentContent:
        params = {"folder": folder, "uid": uid, "index": index}
        raw, headers = self._request_raw("GET", "/api/v1/mail/attachment", query=params)
        content_type = headers.get("Content-Type", "") if headers else ""
        filename = _filename_from_content_disposition(
            headers.get("Content-Disposition", "") if headers else ""
        )
        return AttachmentContent(data=raw, content_type=content_type, filename=filename)

    def set_flag(self, folder: str, uid: int, flag: str, set: bool) -> None:
        body = {"folder": folder, "uid": uid, "flag": flag, "set": set}
        self._request("POST", "/api/v1/mail/flag", json_body=body)

    def _build_url(self, path: str, query: Optional[dict] = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            clean = {k: v for k, v in query.items() if v is not None}
            if clean:
                url = f"{url}?{urllib.parse.urlencode(clean)}"
        return url

    def _headers(self, has_body: bool) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        query: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> Any:
        raw, _ = self._request_raw(method, path, query=query, json_body=json_body)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _request_raw(
        self,
        method: str,
        path: str,
        query: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> tuple:
        url = self._build_url(path, query)
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")

        req = urllib.request.Request(
            url, data=data, method=method, headers=self._headers(has_body=data is not None)
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read()
                return body, dict(resp.headers.items())
        except urllib.error.HTTPError as e:
            error_body = e.read()
            message = "unknown error"
            try:
                parsed = json.loads(error_body.decode("utf-8"))
                message = parsed.get("error", message)
            except Exception:
                if error_body:
                    message = error_body.decode("utf-8", errors="replace")

            retry_after = None
            retry_header = e.headers.get("Retry-After") if e.headers else None
            if retry_header is not None:
                try:
                    retry_after = int(retry_header)
                except ValueError:
                    retry_after = None

            raise MailfoldAPIError(
                status_code=e.code, message=message, retry_after=retry_after
            ) from None
        except urllib.error.URLError as e:
            raise MailfoldConnectionError(str(e.reason)) from None


def _filename_from_content_disposition(value: str) -> str:
    if not value:
        return ""
    for part in value.split(";"):
        part = part.strip()
        if part.lower().startswith("filename="):
            filename = part[len("filename="):].strip()
            return filename.strip('"')
    return ""
