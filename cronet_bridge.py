import json as _json
import logging
from urllib.parse import urlencode

log = logging.getLogger(__name__)

try:
    from java import jclass
    _CronetHttpClient = jclass("com.evanpaul.rdvwr.CronetHttpClient")
    CRONET_AVAILABLE = True
except Exception as e:
    log.warning("Cronet bridge unavailable, falling back to plain requests: %s", e)
    _CronetHttpClient = None
    CRONET_AVAILABLE = False


class CronetResponseWrapper:
    def __init__(self, status_code, headers, body, error=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._body = body or b""
        self.error = error

    @property
    def ok(self):
        return self.error is None and 200 <= self.status_code < 400

    @property
    def content(self):
        return self._body

    @property
    def text(self):
        return self._body.decode("utf-8", errors="replace")

    def json(self):
        return _json.loads(self.text)

    def raise_for_status(self):
        if self.error:
            raise RuntimeError(f"Cronet request failed: {self.error}")
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def cronet_request(method, url, headers=None, params=None, json=None, data=None,
                    timeout=10, **_ignored):
    """Subset of the requests API, backed by Cronet's real Chromium network stack."""
    if params:
        sep = "&" if "?" in url else "?"
        url = url + sep + urlencode(params)

    body = None
    hdrs = dict(headers or {})
    if json is not None:
        body = _json.dumps(json).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json; charset=UTF-8")
    elif data is not None:
        body = data if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8")

    resp = _CronetHttpClient.request(method, url, _json.dumps(hdrs), body, int(timeout or 10))
    if resp.error:
        return CronetResponseWrapper(0, {}, b"", error=str(resp.error))
    resp_headers = _json.loads(resp.headersJson) if resp.headersJson else {}
    return CronetResponseWrapper(resp.statusCode, resp_headers, bytes(resp.body))
