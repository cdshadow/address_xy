import json
import os
from urllib.parse import urlparse, parse_qs

import requests
from http.server import BaseHTTPRequestHandler

# 브라우저 등 다른 도메인에서 호출할 수 있도록 CORS 허용
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _send_json(self, status: int, data: dict) -> None:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-type", "application/json; charset=utf-8")
    for k, v in CORS_HEADERS.items():
        self.send_header(k, v)
    self.end_headers()
    self.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        address = params.get("address", [None])[0]

        if not address:
            _send_json(self, 400, {"error": "address 쿼리 파라미터가 필요합니다."})
            return

        api_key = os.environ.get("KAKAO_REST_API_KEY", "").strip()
        if not api_key:
            _send_json(self, 503, {"error": "서버에 KAKAO_REST_API_KEY가 설정되지 않았습니다."})
            return
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {api_key}"}
        req_params = {"query": address}

        try:
            resp = requests.get(url, headers=headers, params=req_params, timeout=10)
        except requests.RequestException as e:
            _send_json(self, 502, {"error": str(e)})
            return

        if resp.status_code != 200:
            _send_json(self, 400, {"error": "주소를 찾을 수 없거나 API 오류입니다."})
            return

        try:
            result = resp.json()
        except ValueError:
            _send_json(self, 502, {"error": "카카오 API 응답 형식 오류"})
            return

        docs = result.get("documents") or []
        if not docs:
            _send_json(self, 400, {"error": "주소를 찾을 수 없습니다."})
            return

        first = docs[0]
        x, y = first.get("x"), first.get("y")
        if x is None or y is None:
            _send_json(self, 502, {"error": "카카오 API 응답 형식 오류"})
            return
        _send_json(self, 200, {"x": x, "y": y})
