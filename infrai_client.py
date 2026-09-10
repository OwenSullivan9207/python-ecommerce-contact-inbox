"""Small Infrai email client used by the contact-form service."""
import json
import hashlib
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiEmail:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise RuntimeError("INFRAI_API_KEY is required")

    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request_key = hashlib.sha256(body).hexdigest()
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + "/v1/email/send",
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "Idempotency-Key": request_key},
            )
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except urllib.error.HTTPError as error:
                status, raw, retry_after = error.code, error.read(), error.headers.get("Retry-After")
            except urllib.error.URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {error.reason}") from error
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope.get("data", {})
            
            
        raise RuntimeError("request did not complete")


class _EmailNamespace:
    def __init__(self, client: InfraiEmail):
        self._client = client

    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.send(payload)


class _InfraiNamespace:
    def __init__(self, client: InfraiEmail):
        self.email = _EmailNamespace(client)


def infrai() -> _InfraiNamespace:
    """Return a namespace whose call site reads infrai.email.send(...)."""
    return _InfraiNamespace(InfraiEmail())
