#!/usr/bin/env python3
"""Build app/family-piano.html: one self-contained file to paste into a Squarespace Code block.

Reads content/levels.json, content/paths/*.json and licenses/assets.csv,
and inlines them into app/src/family-piano.template.html.

Usage: python3 app/build.py
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app" / "src" / "family-piano.template.html"
OUT = ROOT / "app" / "family-piano.html"
MARK = "/*__FP_CONTENT__*/null"


def main():
    levels = json.loads((ROOT / "content" / "levels.json").read_text(encoding="utf-8"))
    paths = {}
    for p in sorted((ROOT / "content" / "paths").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        paths[d["level"]] = d
    assets = []
    with open(ROOT / "licenses" / "assets.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["asset_id"].endswith("test-fixture"):
                continue  # pipeline test file, not teaching content
            assets.append({k: r[k] for k in ("asset_id", "title", "composer", "url", "attribution_text")})
    content = {"levels": levels, "paths": paths, "assets": assets}
    blob = json.dumps(content, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    assert MARK in html, "placeholder missing in template"
    OUT.write_text(html.replace(MARK, blob), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
