"""
Vercel CLI 없이 로컬에서 API만 테스트할 때 사용.
실행: python local_server.py  또는  npm run local
"""
import os
import sys

# api 폴더를 path에 추가해서 address_xy 모듈 로드
_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_root, "api"))

# .env 파일이 있으면 환경 변수로 로드 (python-dotenv 없이)
_env_path = os.path.join(_root, ".env")
if os.path.isfile(_env_path):
    with open(_env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

from http.server import HTTPServer
from address_xy import handler

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    server = HTTPServer(("", port), handler)
    print(f"로컬 API: http://localhost:{port}/api/address_xy?address=주소")
    print("종료: Ctrl+C")
    server.serve_forever()
