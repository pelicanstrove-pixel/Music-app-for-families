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
  - pieces under review (licenses/candidates.csv, public-domain Mutopia editions not yet checked by an educator):
    their notes go inside the app; each drawn score goes to app/pieces/<asset_id>.js, loaded when the piece is opened
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
# Where the app/pieces/ folder is on the web (the drawn score of each piece under review loads from here when the
# piece is opened): GitHub Pages for this repository. Use --pieces-url pieces/ for a copy that sits next to that folder.
# See README.md, "Hosting the piece files".
PIECES_URL = "https://pelicanstrove-pixel.github.io/Music-app-for-families/app/pieces/"


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


def candidate_reason(row):
    """Copyright gate for pieces still under review (licenses/candidates.csv): the same license rules as
    playable_reason(), but no educator approval yet. The app labels these "Under review"."""
    if not str(row.get("composition_status", "")).lower().startswith("public-domain"):
        return "composition is not marked public domain"
    if row.get("derivatives_allowed") != "yes":
        return "derivatives_allowed is not 'yes'"
    lic = (row.get("edition_license") or "").strip()
    if not re.match(r"^(CC0(\s*1\.0)?|public[- ]domain|PD)$", lic, re.I):
        return f"edition license '{lic}' is not CC0 or public domain"
    if row.get("conversion") != "ok":
        return "conversion did not pass its checks"
    if not (ROOT / row["file"]).exists():
        return f"{row['file']} is missing"
    return None


def piece_file(row, pieces_dir):
    """Make app/pieces/<asset_id>.js (the drawn score, loaded by the app when the piece is opened) and return the
    small note list that goes inside the app. Skipped when the piece file is newer than the score."""
    import tempfile, zipfile
    mxl = ROOT / row["file"]
    out = pieces_dir / (row["asset_id"] + ".js")
    cache = pieces_dir / ".play" / (row["asset_id"] + ".json")
    if out.exists() and cache.exists() and min(out.stat().st_mtime, cache.stat().st_mtime) >= mxl.stat().st_mtime:
        return json.loads(cache.read_text(encoding="utf-8"))
    with zipfile.ZipFile(mxl) as z, tempfile.TemporaryDirectory() as tmp:
        name = next(n for n in z.namelist() if n.endswith(".musicxml") or (n.endswith(".xml") and not n.startswith("META-INF")))
        xml = pathlib.Path(tmp) / "score.musicxml"
        text = z.read(name).decode("utf-8")
        # Verovio expects voices numbered from 1; music21 can write voice 0, which Verovio then misplaces.
        text = re.sub(r"<part id=.*?</part>", lambda m: re.sub(r"<voice>(\d+)</voice>", lambda v: f"<voice>{int(v.group(1)) + 1}</voice>", m.group(0))
                      if "<voice>0</voice>" in m.group(0) else m.group(0), text, flags=re.S)
        xml.write_text(text, encoding="utf-8")
        play, view = score_notes(xml), score_view(xml)
    body = json.dumps(view, ensure_ascii=False, separators=(",", ":"))
    out.write_text("/* Family Piano piece file: " + row["title"].replace("*/", "") + ", " + row["composer"].replace("*/", "") +
                   ". Mutopia Project edition (public domain), drawn with Verovio. Made by app/build.py. */\n" +
                   "window.fpPiece&&window.fpPiece(" + json.dumps(row["asset_id"]) + "," + body + ");\n", encoding="utf-8")
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps(play, separators=(",", ":")), encoding="utf-8")
    return play


def score_notes(xml_path):
    """Notes for the player: [start, length, midi, hand] in quarter notes; hand 0 = right, 1 = left."""
    from music21 import converter, harmony, meter, tempo  # only needed when there is something to play
    sc = converter.parse(str(xml_path))
    events = []
    for hand, part in enumerate(sc.parts[:2]):
        # Join tied notes per hand (music21's stripTies() misses ties between voices and some chord ties).
        items = []
        for n in part.flatten().notes:
            if isinstance(n, harmony.ChordSymbol) or n.quarterLength <= 0:
                continue
            for sub in (n.notes if n.isChord else [n]):
                items.append((float(n.offset), float(n.quarterLength), sub.pitch.midi, sub.tie.type if sub.tie else None))
        items.sort(key=lambda x: x[0])
        tied = {}  # (midi, where the tie ends) -> the event it continues
        for on, ln, m, tt in items:
            ev = tied.pop((m, round(on, 3)), None) if tt in ("stop", "continue") else None
            if ev:
                ev[1] = on + ln - ev[0]
            else:
                ev = [on, ln, m, hand]
                events.append(ev)
            if tt in ("start", "continue"):
                tied[(m, round(on + ln, 3))] = ev
    events = sorted([round(e[0], 4), round(e[1], 4), e[2], e[3]] for e in events)
    marks = sc.flatten().getElementsByClass(tempo.MetronomeMark)
    bpm = float(marks[0].getQuarterBPM()) if marks else 80.0  # playback default when the score gives no tempo
    ts = sc.flatten().getElementsByClass(meter.TimeSignature)
    beat = float(ts[0].beatDuration.quarterLength) if ts else 1.0
    beats = int(ts[0].beatCount) if ts else 4
    bars = [round(float(m.offset), 4) for m in sc.parts[0].getElementsByClass("Measure")]
    return {"bpm": bpm, "beat": beat, "beatsPerBar": beats, "bars": bars, "end": round(float(sc.highestTime), 4), "events": events}


def gz64(text):
    return base64.b64encode(gzip.compress(text.encode("utf-8"), 9, mtime=0)).decode("ascii")


def score_view(xml_path):
    """The score drawn by Verovio (gzipped SVG pages, plus one long line for the sheet-music game) and each note's
    start, end (in quarter notes), hand (0 right, 1 left), MIDI pitch and a skip flag, for highlighting and checking."""
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
    timemap = tk.renderToTimemap({})
    for e in timemap:
        for nid in e.get("on", []):
            notes.setdefault(nid, [e["qstamp"], None, hand.get(nid, 0)])
        for nid in e.get("off", []):
            if nid in notes:
                notes[nid][1] = e["qstamp"]
    for nid, n in notes.items():
        n.append(tk.getMIDIValuesForElement(nid).get("pitch"))
        n.append(0)
    # A 5th value of 1 means "drawn and highlighted, but not checked": the second note of a tie (it is held, not
    # played again) and grace notes (the player leaves them out). The first note of a tie is held to the tie's end.
    mei = tk.getMEI()
    ties = dict(re.findall(r'<tie\b[^>]*?startid="#([^"]+)"[^>]*?endid="#([^"]+)"', mei))
    grace = set(re.findall(r'<note\b[^>]*?xml:id="([^"]+)"[^>]*?grace=', mei))
    for chord in re.findall(r'<chord\b[^>]*?grace=.*?</chord>', mei, re.S):
        grace.update(re.findall(r'<note\b[^>]*?xml:id="([^"]+)"', chord))
    for nid in grace:
        if nid in notes:
            notes[nid][4] = 1
    for start in sorted(ties, key=lambda k: notes[k][0] if k in notes else 0):
        end = ties[start]
        if start in notes and end in notes and notes[start][3] == notes[end][3]:
            notes[end][4] = 1
            first = start
            while any(v == first for v in ties.values()):  # walk back to the first note of a chain of ties
                first = next(k for k, v in ties.items() if v == first)
            if first in notes and notes[end][1] is not None:
                notes[first][1] = max(notes[first][1] or 0, notes[end][1])
    tk.setOptions({"breaks": "none", "adjustPageWidth": True, "pageWidth": 100000})
    tk.redoLayout()
    line = re.sub(r">\s+<", "><", tk.renderToSVG(1))
    return {"svg": gz64("\u0000".join(pages)), "line": gz64(line), "notes": notes}


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
    ap.add_argument("--pieces-url", default=PIECES_URL, help="web folder holding app/pieces/ (ends with /)")
    ap.add_argument("--no-candidates", action="store_true", help="leave out the pieces still under review")
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
    if not args.no_candidates:
        pieces_dir = ROOT / "app" / "pieces"
        pieces_dir.mkdir(exist_ok=True)
        known = {a["asset_id"] for a in assets}
        with open(ROOT / "licenses" / "candidates.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if r["asset_id"] in known:
                continue  # already approved and listed in assets.csv
            why = candidate_reason(r)
            if why:
                print(f"  left out {r['asset_id']}: {why}")
                continue
            typeset = re.search(r"typeset by (.+?) from", r.get("edition_source", ""))
            credit = ("Typeset by " + typeset.group(1) + " for the Mutopia Project" if typeset else "Mutopia Project edition") + " (public domain)"
            opus = (r.get("opus") or "").strip().rstrip(".")
            if re.fullmatch(r"Op\.?\s*0", opus):
                opus = ""  # Mutopia's placeholder for "no opus number"
            title = r["title"] + (", " + opus if opus and opus not in r["title"] else "")
            assets.append({"asset_id": r["asset_id"], "title": title, "composer": r["composer"], "url": r["mutopia_url"],
                           "attribution_text": credit, "review": True, "scoreSrc": r["asset_id"] + ".js",
                           "play": piece_file(r, pieces_dir)})
        print(f"  {sum(1 for a in assets if a.get('review'))} pieces under review; piece files in {pieces_dir}")
    content = {
        "levels": levels, "paths": paths, "assets": assets, "piano": piano_samples(), "piecesUrl": args.pieces_url,
        "placement": {"quiz": placement("reader-quiz-template.md"),
                      "checklist": placement("prereader-observation-checklist.md"),
                      "rules": json.loads((ROOT / "content" / "placement" / "placement-rules.json").read_text(encoding="utf-8"))},
    }
    blob = json.dumps(content, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

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
