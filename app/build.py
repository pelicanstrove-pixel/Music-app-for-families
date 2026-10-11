#!/usr/bin/env python3
"""Build app/family-piano.html: one self-contained file to paste into a Squarespace Code block.

Inlines into app/src/family-piano.template.html:
  - content/levels.json and content/paths/*.json (the 12-week plans)
  - licenses/assets.csv (pieces; repo-relative links are turned into full links, see SCORE_BASE_URL)
  - content/placement/*.md (placement sheets, as simple HTML)
  - app/drills.html (the drill sheet maker, shown on the Print screen)

Usage: python3 app/build.py
"""
import csv, html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app" / "src" / "family-piano.template.html"
OUT = ROOT / "app" / "family-piano.html"
MARK = "/*__FP_CONTENT__*/null"
DRILLS_MARK = "<!--__FP_DRILLS__-->"
# Where repo files (like scores/...) are reachable on the web. Change this if the files are hosted elsewhere.
SCORE_BASE_URL = "https://github.com/pelicanstrove-pixel/Music-app-for-families/blob/main/"


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def md_to_html(md):
    """Just enough Markdown for the placement templates: headings, paragraphs, quotes, tables, rules."""
    out, table = [], None
    for line in md.splitlines() + [""]:
        t = line.strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            if table is None:
                table = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>"]
            else:
                table.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if table is not None:
            out.append("".join(table) + "</tbody></table>")
            table = None
        if not t:
            continue
        m = re.match(r"(#{1,3}) (.*)", t)
        if m:
            lvl = {1: "h2", 2: "h3", 3: "h3"}[len(m.group(1))]
            out.append(f"<{lvl}>{inline(m.group(2))}</{lvl}>")
        elif t == "---":
            out.append("<hr>")
        elif t.startswith(">"):
            out.append(f"<blockquote>{inline(t.lstrip('> '))}</blockquote>")
        else:
            out.append(f"<p>{inline(t)}</p>")
    return "".join(out)


def placement(name):
    md = (ROOT / "content" / "placement" / name).read_text(encoding="utf-8")
    parts = re.split(r"^## ANSWER KEY.*$", md, maxsplit=1, flags=re.M)
    key = md_to_html(parts[1]).replace("<hr>", "") if len(parts) > 1 else ""
    return {"main": md_to_html(parts[0]), "key": key}


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
            a = {k: r[k] for k in ("asset_id", "title", "composer", "url", "attribution_text")}
            if a["url"] and not re.match(r"https?://", a["url"]):
                a["url"] = SCORE_BASE_URL + a["url"].lstrip("/")
            assets.append(a)
    content = {
        "levels": levels, "paths": paths, "assets": assets,
        "placement": {"quiz": placement("reader-quiz-template.md"),
                      "checklist": placement("prereader-observation-checklist.md")},
    }
    blob = json.dumps(content, ensure_ascii=False).replace("</", "<\\/")

    drills = (ROOT / "app" / "drills.html").read_text(encoding="utf-8")
    start = drills.index('<div id="pd-drills">')  # drop the stand-alone page header (doctype, title)
    drills = drills[start:]

    page = TEMPLATE.read_text(encoding="utf-8")
    assert MARK in page and DRILLS_MARK in page, "placeholder missing in template"
    page = page.replace(MARK, blob).replace(DRILLS_MARK, drills)
    header = ("<!DOCTYPE html>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
              "<title>Family Piano</title>\n<!-- BUILT FILE: do not edit. Edit app/src/family-piano.template.html and run python3 app/build.py -->\n")
    OUT.write_text(header + page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
