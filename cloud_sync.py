# cloud_sync.py
"""Облачная синхронизация через GitHub Gist API."""
import json
import base64
import urllib.request
import urllib.error


GIST_API = "https://api.github.com/gists"
GIST_FILENAME = "numerical_methods_data.json"


def encode_data(data):
    json_str = json.dumps(data, ensure_ascii=False)
    return base64.b64encode(json_str.encode("utf-8")).decode("ascii")


def decode_data(encoded):
    json_str = base64.b64decode(encoded.encode("ascii")).decode("utf-8")
    return json.loads(json_str)


def upload_to_gist(token, data, gist_id=None, description="NumericalMethods sync"):
    encoded = encode_data(data)
    payload = {
        "description": description,
        "public": False,
        "files": {GIST_FILENAME: {"content": encoded}}
    }
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "NumericalMethods/2.0"
    }
    if gist_id:
        url = f"{GIST_API}/{gist_id}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers=headers, method="PATCH")
    else:
        req = urllib.request.Request(GIST_API, data=json.dumps(payload).encode("utf-8"),
                                     headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {
                "id": result["id"],
                "url": result["url"],
                "html_url": result["html_url"],
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at")
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API error {e.code}: {error_body}")


def download_from_gist(token, gist_id):
    url = f"{GIST_API}/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "NumericalMethods/2.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            files = result.get("files", {})
            if GIST_FILENAME not in files:
                raise RuntimeError(f"Файл {GIST_FILENAME} не найден в gist")
            file_data = files[GIST_FILENAME]
            if "content" in file_data:
                encoded = file_data["content"]
            else:
                raw_url = file_data.get("raw_url")
                if not raw_url:
                    raise RuntimeError("Нет содержимого файла")
                req_raw = urllib.request.Request(raw_url, headers=headers)
                with urllib.request.urlopen(req_raw, timeout=15) as resp_raw:
                    encoded = resp_raw.read().decode("utf-8")
            return decode_data(encoded)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API error {e.code}: {error_body}")


def list_user_gists(token):
    url = "https://api.github.com/gists?per_page=100"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "NumericalMethods/2.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            gists = json.loads(resp.read().decode("utf-8"))
            return [g for g in gists if GIST_FILENAME in g.get("files", {})]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Ошибка API: {e.code}")


def validate_token(token):
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "NumericalMethods/2.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            user = json.loads(resp.read().decode("utf-8"))
            return user.get("login")
    except urllib.error.HTTPError:
        return None