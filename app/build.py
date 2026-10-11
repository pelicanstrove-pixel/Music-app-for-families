#!/usr/bin/env python3
"""Build app/family-piano.html: one self-contained file to paste into a Squarespace Code block.

Inlines into app/src/family-piano.template.html:
  - content/levels.json and content/paths/*.json (the 12-week plans)
  - licenses/assets.csv (pieces; repo-relative links are turned into full links, see SCORE_BASE_URL)
  - content/placement/*.md (placement sheets as simple HTML, plus their items for the results form)
  - content/placement/placement-rules.json (how results turn into a suggested level)
  - app/drills.html (the drill sheet maker, shown on the Print screen)
  - app/fonts/nunito-latin-wght-normal.woff2 (as base64, so no font server is contacted)
  - app/vendor/vexflow-bravura-4.2.2.js (in place of the jsDelivr script tag, so drills need no internet)

  - app/vendor/piano/ (MIT piano samples for the built-in player)
  - notes and the drawn score (Verovio SVG + note timings, for highlighting) for the built-in player, made from approved simplified scores in scores/derived/ that pass the
    license gate in playable_reason() (needs music21: pip install -r scores/requirements.txt)
  - every third-party license, in full, in a comment at the top of the file

Usage: python3 app/build.py
       python3 app/build.py --include-test-fixtures --out /tmp/test.html   (testing only: never publish this)
"""
import argparse, base64, csv, gzip, hashlib, html, json, pathlib, re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app" / "src" / "family-piano.template.html"
OUT = ROOT / "app" / "family-piano.html"
MARK = "/*__FP_CONTENT__*/null"
DRILLS_MARK = "<!--__FP_DRILLS__-->"
FONT_MARK = "/*__FP_FONT__*/"
FONT = ROOT / "app" / "fonts" / "nunito-latin-wght-normal.woff2"
VEXFLOW = ROOT / "app" / "vendor" / "vexflow-bravura-4.2.2.js"
VEXFLOW_TAG = '<script src="https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js"></script>'
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


def placement_items(md):
    """Sections and items (rows like "| A1 | prompt |") from a placement template, for the results form."""
    sections, heading, yesno = [], "", False
    for line in md.splitlines():
        t = line.strip()
        m = re.match(r"## (.*)", t)
        if m:
            heading = re.sub(r"^(Section [A-Z]:|\d+\.)\s*", "", m.group(1))
            heading = re.sub(r"\s*\(.*\)$", "", heading)
            continue
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if "Yes / Not yet" in cells:
                yesno = True
            elif cells and cells[0] == "#":
                yesno = False
            if cells and re.fullmatch(r"[A-Z]\d+", cells[0]):
                sid = cells[0][0]
                if not sections or sections[-1]["id"] != sid:
                    sections.append({"id": sid, "name": heading, "kind": "yesno" if yesno else "points", "items": []})
                sections[-1]["items"].append({"id": cells[0], "prompt": cells[1] if len(cells) > 1 else ""})
    return sections


def placement(name):
    md = (ROOT / "content" / "placement" / name).read_text(encoding="utf-8")
    parts = re.split(r"^## ANSWER KEY.*$", md, maxsplit=1, flags=re.M)
    key = md_to_html(parts[1]).replace("<hr>", "") if len(parts) > 1 else ""
    return {"main": md_to_html(parts[0]), "key": key, "sections": placement_items(parts[0])}


PIANO = ROOT / "app" / "vendor" / "piano"
LICENSE_FILES = [
    ("VexFlow 4.2.2 (draws music on drill sheets)", ROOT / "app" / "vendor" / "VEXFLOW-LICENSE.txt"),
    ("Nunito font", ROOT / "app" / "fonts" / "OFL.txt"),
    ("Bravura music font (inside VexFlow)", None),
    ("Fluid R3 piano sound (FluidR3Mono_GM)", PIANO / "LICENSE.md"),
]
BRAVURA_NOTICE = ("Copyright (c) 2015, Steinberg Media Technologies GmbH (http://www.steinberg.net/), "
                  "with Reserved Font Name \"Bravura\". Licensed under the SIL Open Font License, Version 1.1 "
                  "(full text above, under Nunito font).")
# Edition licenses whose terms let us make and share a simplified version with only a credit line.
# Share-alike (CC-BY-SA), NonCommercial (NC) and NoDerivatives (ND) are left out on purpose.
OK_EDITION = re.compile(r"^(CC0(\s*1\.0)?|public[- ]domain|PD|CC[- ]BY(\s*[0-9.]+)?)$", re.I)


def playable_reason(row, meta):
    """Return None if this score may be played in the app, else the reason it may not (copyright gate)."""
    if not str(row.get("composition_status", "")).lower().startswith("public-domain"):
        return "composition is not marked public domain"
    if row.get("derivatives_allowed") != "yes":
        return "derivatives_allowed is not 'yes'"
    lic = (row.get("edition_license") or "").strip()
    if not OK_EDITION.match(lic):
        return f"edition license '{lic}' is not CC0, public domain or CC-BY"
    if lic.upper().startswith("CC") and "BY" in lic.upper() and not (row.get("attribution_text") or "").strip():
        return "CC-BY edition needs attribution_text"
    if meta is None:
        return "no simplified score in scores/derived/"
    if meta.get("status") != "approved":
        return "simplified score is not approved (scores/pipeline/approve.py)"
    if (meta.get("license") or {}).get("derivatives_allowed") != "yes":
        return "meta.json license does not allow derivatives"
    return None


def score_notes(xml_path):
    """Notes for the player: [start, length, midi, hand] in quarter notes; hand 0 = right, 1 = left."""
    from music21 import converter, harmony, meter, tempo  # only needed when there is something to play
    sc = converter.parse(str(xml_path)).stripTies()
    events = []
    for hand, part in enumerate(sc.parts[:2]):
        for n in part.flatten().notes:
            if isinstance(n, harmony.ChordSymbol) or n.quarterLength <= 0:
                continue
            for pt in n.pitches:
                events.append([round(float(n.offset), 4), round(float(n.quarterLength), 4), pt.midi, hand])
    events.sort()
    marks = sc.flatten().getElementsByClass(tempo.MetronomeMark)
    bpm = float(marks[0].getQuarterBPM()) if marks else 80.0  # playback default when the score gives no tempo
    ts = sc.flatten().getElementsByClass(meter.TimeSignature)
    beat = float(ts[0].beatDuration.quarterLength) if ts else 1.0
    beats = int(ts[0].beatCount) if ts else 4
    bars = [round(float(m.offset), 4) for m in sc.parts[0].getElementsByClass("Measure")]
    return {"bpm": bpm, "beat": beat, "beatsPerBar": beats, "bars": bars, "end": round(float(sc.highestTime), 4), "events": events}


def score_view(xml_path):
    """The score drawn by Verovio (gzipped SVG pages) plus each note's start, end and hand, for highlighting."""
    import verovio  # in scores/requirements.txt
    tk = verovio.toolkit()
    tk.setOptions({"pageWidth": 2100, "pageHeight": 60000, "adjustPageHeight": True, "scale": 40, "breaks": "auto",
                   "header": "none", "footer": "none", "svgViewBox": True, "svgRemoveXlink": True, "xmlIdSeed": 1})
    tk.loadFile(str(xml_path))
    pages = [re.sub(r">\s+<", "><", tk.renderToSVG(i + 1)) for i in range(tk.getPageCount())]
    hand = {}
    ns = "{http://www.w3.org/2000/svg}"
    for page in pages:
        for meas in ET.fromstring(page).iter(ns + "g"):
            if meas.get("class") != "measure":
                continue
            staffs = [g for g in meas if g.get("class") == "staff"]
            for i, st in enumerate(staffs[:2]):
                for g in st.iter(ns + "g"):
                    if g.get("class") == "note":
                        hand[g.get("id")] = i
    notes = {}
    for e in tk.renderToTimemap({}):
        for nid in e.get("on", []):
            notes.setdefault(nid, [e["qstamp"], None, hand.get(nid, 0)])
        for nid in e.get("off", []):
            if nid in notes:
                notes[nid][1] = e["qstamp"]
    blob = gzip.compress("\u0000".join(pages).encode("utf-8"), 9, mtime=0)
    return {"svg": base64.b64encode(blob).decode("ascii"), "notes": notes}


def piano_samples():
    info = json.loads((PIANO / "piano.json").read_text(encoding="utf-8"))
    samples = [{"root": x["root"], "cents": x["cents"],
                "b64": base64.b64encode((PIANO / x["file"]).read_bytes()).decode("ascii")} for x in info["samples"]]
    return {"samples": samples, "keys": info["keys"]}


def licenses_comment():
    parts = ["Family Piano includes the following third-party software, fonts and sounds. Their licenses follow in full."]
    for name, path in LICENSE_FILES:
        body = BRAVURA_NOTICE if path is None else path.read_text(encoding="utf-8")
        parts.append("=" * 70 + "\n" + name + "\n" + "=" * 70 + "\n" + body.strip())
    text = "\n\n".join(parts).replace("--", "\u2013")  # "--" is not allowed inside an HTML comment
    return "<!--\n" + text + "\n-->\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--include-test-fixtures", action="store_true", help="testing only; never publish the result")
    args = ap.parse_args()
    out_path = pathlib.Path(args.out)
    levels = json.loads((ROOT / "content" / "levels.json").read_text(encoding="utf-8"))
    paths = {}
    for p in sorted((ROOT / "content" / "paths").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        paths[d["level"]] = d
    assets = []
    with open(ROOT / "licenses" / "assets.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["asset_id"].endswith("test-fixture") and not args.include_test_fixtures:
                continue  # pipeline test file, not teaching content
            a = {k: r[k] for k in ("asset_id", "title", "composer", "url", "attribution_text")}
            if a["url"] and not re.match(r"https?://", a["url"]):
                a["url"] = SCORE_BASE_URL + a["url"].lstrip("/")
            meta_path = ROOT / "scores" / "derived" / r["asset_id"] / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else None
            if args.include_test_fixtures and r["asset_id"].endswith("test-fixture") and meta:
                meta = dict(meta, status="approved")  # testing only
            why = playable_reason(r, meta)
            if why is None:
                xml = meta_path.parent / meta["outputs"]["musicxml"]
                if hashlib.sha256(xml.read_bytes()).hexdigest() != meta.get("musicxml_sha256"):
                    why = "simplified score changed after it was approved"
            if why is None:
                a["play"] = score_notes(xml)
                a["score"] = score_view(xml)
            else:
                print(f"  player off for {r['asset_id']}: {why}")
            assets.append(a)
    content = {
        "levels": levels, "paths": paths, "assets": assets, "piano": piano_samples(),
        "placement": {"quiz": placement("reader-quiz-template.md"),
                      "checklist": placement("prereader-observation-checklist.md"),
                      "rules": json.loads((ROOT / "content" / "placement" / "placement-rules.json").read_text(encoding="utf-8"))},
    }
    blob = json.dumps(content, ensure_ascii=False).replace("</", "<\\/")

    drills = (ROOT / "app" / "drills.html").read_text(encoding="utf-8")
    start = drills.index('<div id="pd-drills">')  # drop the stand-alone page header (doctype, title)
    drills = drills[start:]
    vexflow = VEXFLOW.read_text(encoding="utf-8")
    assert "</script" not in vexflow.lower(), "vexflow text would close the script tag"
    assert drills.count(VEXFLOW_TAG) == 1, "VexFlow script tag in app/drills.html changed; update VEXFLOW_TAG"
    drills = drills.replace(VEXFLOW_TAG, "<script>/* VexFlow 4.2.2 (MIT) + Bravura font (OFL): see app/vendor/README.md */\n" + vexflow + "\n</script>")

    page = TEMPLATE.read_text(encoding="utf-8")
    assert MARK in page and DRILLS_MARK in page and FONT_MARK in page, "placeholder missing in template"
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    page = page.replace(FONT_MARK, font).replace(MARK, blob).replace(DRILLS_MARK, drills)
    header = ("<!DOCTYPE html>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
              "<title>Family Piano</title>\n<!-- BUILT FILE: do not edit. Edit app/src/family-piano.template.html and run python3 app/build.py -->\n")
    if args.include_test_fixtures:
        header += "<!-- TEST BUILD with pipeline test fixtures: do not publish -->\n"
    out_path.write_text(header + licenses_comment() + page, encoding="utf-8")
    print(f"wrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
