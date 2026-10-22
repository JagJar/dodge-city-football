#!/usr/bin/env python3
"""Import public, pre-2018 Wayback content saved by Safari. Never import scripts.

Usage: python3 scripts/import_webarchive.py /tmp/capture.webarchive [more ...]
The original response URL, rather than the requested replay date, is recorded.
"""
import hashlib
import json
import plistlib
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/recovered-assets.json"
records = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
records = {r["local_path"]: r for r in records}


def response_url(resource):
    try:
        objects = plistlib.loads(resource["WebResourceResponse"])["$objects"]
        for obj in objects:
            if isinstance(obj, dict) and "NS.relative" in obj:
                return objects[obj["NS.relative"].data]
    except (KeyError, ValueError, TypeError):
        pass
    return resource["WebResourceURL"]


def save(resource, main=False):
    replay = response_url(resource)
    match = re.search(r"/web/(\d{14})[a-z_]*?/(https?://.*)", replay)
    if not match or match[1] >= "20180101000000":
        return
    original = urlsplit(match[2])
    mime = resource.get("WebResourceMIMEType", "")
    data = resource.get("WebResourceData", b"")
    own = original.hostname in ("dodgecityfootball.com", "www.dodgecityfootball.com")
    if main and own and mime == "text/html":
        name = original.path.strip("/").replace("/", "__") or "homepage.html"
        local = "research/recovered/" + match[1] + "-" + name
    elif own and mime.startswith("image/"):
        # Only content and template imagery; no third-party pixels or widgets.
        if not original.path.startswith(("/images/", "/cache/mod_bt_contentslider/", "/media/gridiron/", "/templates/shaper_sportson/")):
            return
        local = "public" + original.path
    elif own and mime == "application/pdf":
        local = "public" + original.path
    elif own and mime == "text/css":
        local = "research/original-css" + original.path
    elif original.hostname == "fonts.gstatic.com" and "/titilliumweb/" in original.path and mime.startswith("font/"):
        local = "public/assets/fonts/" + Path(original.path).name
    else:
        return
    path = (ROOT / local).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Unsafe archive path")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    records[local] = {
        "local_path": local, "original_url": match[2], "capture": match[1],
        "replay_url": replay, "mime": mime, "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(), "recovery": "Wayback response saved in Safari webarchive",
    }


for filename in sys.argv[1:]:
    archive = plistlib.loads(Path(filename).read_bytes())
    save(archive["WebMainResource"], main=True)
    for resource in archive.get("WebSubresources", []):
        save(resource)
MANIFEST.write_text(json.dumps(sorted(records.values(), key=lambda r: r["local_path"]), indent=2) + "\n")
print(f"Recorded {len(records)} original resources (scripts and third-party widgets excluded).")
