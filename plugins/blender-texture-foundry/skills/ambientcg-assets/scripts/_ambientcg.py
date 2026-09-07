from __future__ import annotations

import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://ambientcg.com/api/v3/assets"
DOWNLOAD_HEADERS = {
    "User-Agent": "dcc-mcp/0.19 (+https://github.com/dcc-mcp)",
    "Referer": "https://ambientcg.com/",
}
INCLUDE_FIELDS = "type,title,url,tags,dimensions,downloads,thumbnails"
ASSET_TYPES = {
    "all": None,
    "3dmodel": "3d-model",
    "material": "material",
    "hdri": "hdri",
    "atlas": "atlas",
    "decal": "decal",
    "terrain": "terrain",
    "plaintexture": "plain-image",
    "substance": "substance",
    "brush": "brush",
}


def normalize_asset_type(value: str) -> str | None:
    compact = value.lower().replace("-", "").replace("_", "")
    return ASSET_TYPES.get(compact, value.lower())


def json_api(params: dict[str, Any]) -> dict[str, Any]:
    query = {k: v for k, v in params.items() if v is not None}
    query.setdefault("include", INCLUDE_FIELDS)
    url = BASE_URL + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers=DOWNLOAD_HEADERS)
    with urllib.request.urlopen(request, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_rows(asset_id: str) -> list[dict[str, str]]:
    assets = json_api({"id": asset_id, "limit": 1}).get("assets", [])
    if not assets:
        return []
    return [
        {
            "downloadAttribute": item.get("attributes", ""),
            "filetype": item.get("extension", ""),
            "size": str(item.get("size", 0)),
            "downloadLink": item.get("url", ""),
            "rawLink": item.get("url", ""),
        }
        for item in assets[0].get("downloads", [])
    ]


def fetch(url: str, output_dir: str) -> str:
    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlparse(url)
    query_name = urllib.parse.parse_qs(parsed.query).get("file", [""])[0]
    name = Path(urllib.parse.unquote(query_name or parsed.path.rsplit("/", 1)[-1])).name
    if not name:
        raise ValueError("ambientCG download URL has no file name")
    target = destination / name
    request = urllib.request.Request(url, headers=DOWNLOAD_HEADERS)
    partial = target.with_suffix(target.suffix + ".part")
    try:
        with (
            urllib.request.urlopen(request, timeout=180) as response,
            partial.open("wb") as output,
        ):
            shutil.copyfileobj(response, output)
        partial.replace(target)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return str(target)
