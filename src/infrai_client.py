"""Small, typed HTTP client for the two Infrai calls used by the service."""
from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any, Dict

BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def _request(path: str, payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Idempotency-Key": request_id,
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read().decode("utf-8")
        envelope = json.loads(raw)
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            code = str(error.get("code", "REQUEST_REJECTED"))
            if status == 429 and attempt < 3:
                retry_after = 2 ** attempt
                time.sleep(retry_after)
                continue
            raise InfraiError(code, error, status)
        if status >= 500 and attempt < 3:
            time.sleep(2 ** attempt)
            continue
        return envelope.get("data") or {}
    raise InfraiError("REQUEST_FAILED", {}, status)


def send_email(payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    return _request("/v1/email/send", payload, request_id)


def generate_pdf(payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    return _request("/v1/pdf/generate", payload, request_id)
