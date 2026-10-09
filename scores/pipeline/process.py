"""Score pipeline. Rules only, no AI. Plain-English rules: scores/RULES.md.

Usage (run from the repository folder):
  python scores/pipeline/process.py scores/recipes/<asset_id>.yaml   # make one piece
  python scores/pipeline/process.py --check                          # license check for every file in scores/source
"""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "scores" / "source"
DERIVED_DIR = ROOT / "scores" / "derived"
ASSETS_CSV = ROOT / "licenses" / "assets.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import annotate  # noqa: E402
import extract  # noqa: E402
import licenses  # noqa: E402
import render  # noqa: E402
import transform  # noqa: E402

RULE_NAMES = {
    "E1": "measure range", "E2": "right hand only", "E3": "left hand only", "E4": "top melody only",
    "T1": "ornaments/grace notes removed", "T2": "inner voices dropped", "T3": "dotted rhythms evened",
    "T4": "transposed", "T5": "range limited by octave moves",
    "A1": "note names", "A2": "counting", "A3": "solfege (movable do)", "A4": "chord symbols",
    "A5": "Roman numerals", "A6": "SUGGESTED fingering",
}

DEFAULT_RECIPE = {
    "extract": {"part": "both", "measures": None},
    "transform": {"remove_ornaments": True, "drop_inner_voices": False, "simplify_dotted_rhythms": False,
                  "transpose_to_key": None, "limit_range_semitones": None, "phrase_measures": 4},
    "annotate": {"note_names": False, "counting": False, "solfege": False, "chord_symbols": False,
                 "roman_numerals": False, "suggested_fingering": False, "fingering_every_note": False},
    "render": {"engine": "verovio", "large_print": True},
}


def load_recipe(path):
    with open(path, encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}
    recipe = copy.deepcopy(DEFAULT_RECIPE)
    for section, values in user.items():
        if isinstance(values, dict) and section in recipe:
            unknown = set(values) - set(recipe[section])
            if unknown:
                sys.exit(f"Recipe error: unknown setting(s) in '{section}': {', '.join(sorted(unknown))}")
            recipe[section].update(values)
        else:
            recipe[section] = values
    if not recipe.get("asset_id"):
        sys.exit("Recipe error: 'asset_id' is missing.")
    if recipe["extract"]["part"] not in ("both", "right_hand", "left_hand", "melody"):
        sys.exit("Recipe error: extract.part must be both, right_hand, left_hand, or melody.")
    return recipe


def license_gate(asset_id):
    """Run L1-L6 and stop with the reasons if anything fails."""
    rows = licenses.load_assets(ASSETS_CSV)
    row = rows.get(asset_id)
    ok, reasons = licenses.check_license(asset_id, row)
    src = licenses.find_source_file(SOURCE_DIR, asset_id)
    if src is None:
        ok = False
        reasons.append(f"No file named {asset_id}.musicxml, .mxl or .xml in scores/source/.")
    if not ok:
        print(f"REFUSED: {asset_id}")
        for r in reasons:
            print("  - " + r)
        sys.exit(2)
    return row, src


def check_all():
    rows = licenses.load_assets(ASSETS_CSV)
    files = sorted(p for p in SOURCE_DIR.iterdir() if p.suffix.lower() in (".musicxml", ".mxl", ".xml"))
    if not files:
        print("No MusicXML files in scores/source/.")
    for p in files:
        ok, reasons = licenses.check_license(p.stem, rows.get(p.stem))
        print(("OK       " if ok else "REFUSED  ") + p.name)
        for r in reasons:
            print("  - " + r)


def build_footer(row, applied, recipe):
    composer = row.get("composer") or "unknown composer"
    source = row.get("edition_source") or "unknown source"
    lic = row.get("edition_license") or "unknown license"
    attrib = (row.get("attribution_text") or "").strip()
    rules = "; ".join(f"{rid} {RULE_NAMES[rid]}" for rid in applied)
    text = f"Simplified from {composer}, {source} / {lic}."
    if attrib:
        text += f" {attrib}."
    if (row.get("derivatives_allowed") or "").strip().lower() == "share-alike":
        text += f" This arrangement is shared under the same license ({lic})."
    text += f" Rules: {rules}. Rules are explained in scores/RULES.md."
    if recipe["annotate"]["suggested_fingering"]:
        text += " Fingering is SUGGESTED by a simple rule; check it with a teacher."
    return text


def run(recipe_path):
    recipe = load_recipe(recipe_path)
    asset_id = recipe["asset_id"]
    row, src = license_gate(asset_id)

    from music21 import converter, metadata
    import music21
    import verovio

    score = converter.parse(str(src))
    ex, tr, an = recipe["extract"], recipe["transform"], recipe["annotate"]
    applied, log = [], {}

    def step(rule_id, notes):
        applied.append(rule_id)
        log[rule_id] = notes if isinstance(notes, list) else [notes]

    # 1. Measure range (before everything else)
    if ex["measures"]:
        first, last = ex["measures"]
        score = extract.extract_measure_range(score, first, last)
        step("E1", f"measures {first}-{last}")

    # 2. Transforms on the full score (ornaments out, then transpose, so harmony is analyzed in the new key)
    if tr["remove_ornaments"]:
        step("T1", transform.remove_ornaments(score))
    if tr["transpose_to_key"]:
        step("T4", transform.transpose_to_key(score, str(tr["transpose_to_key"])))

    # 3. Key and harmony analysis use both hands with every chord note, before anything is removed
    k = transform.detect_key(score)
    harmonies = annotate.analyze_harmony(score, k) if (an["chord_symbols"] or an["roman_numerals"]) else []

    if tr["drop_inner_voices"]:
        step("T2", transform.drop_inner_voices(score))
    if tr["simplify_dotted_rhythms"]:
        step("T3", transform.simplify_dotted_rhythms(score))

    # 4. Extract a hand or the melody
    part_mode = ex["part"]
    if part_mode == "right_hand":
        score = extract.extract_right_hand(score)
        step("E2", "kept the upper staff")
    elif part_mode == "left_hand":
        score = extract.extract_left_hand(score)
        step("E3", "kept the lower staff")
    elif part_mode == "melody":
        score = extract.extract_top_melody(score)
        step("E4", "kept voice 1 of the upper staff, top note of each chord")
    extract.drop_staff_groups(score)
    hands = extract.hands_of(score, part_mode)

    # 5. Range limit (per staff, after extraction)
    if tr["limit_range_semitones"]:
        step("T5", transform.limit_range(score, int(tr["limit_range_semitones"]), int(tr["phrase_measures"])))

    # 6. Annotations
    if an["note_names"]:
        step("A1", annotate.add_note_names(score))
    if an["counting"]:
        step("A2", annotate.add_counting(score))
    if an["solfege"]:
        step("A3", annotate.add_solfege(score, k))
    if an["chord_symbols"]:
        step("A4", annotate.add_chord_symbols(score, harmonies))
    if an["roman_numerals"]:
        step("A5", annotate.add_roman_numerals(score, harmonies, k))
    if an["suggested_fingering"]:
        step("A6", annotate.add_suggested_fingering(score, hands, an["fingering_every_note"]))

    # 7. Write outputs
    title = row.get("title") or asset_id
    score.metadata = metadata.Metadata(title=f"{title} (simplified)", composer=row.get("composer") or "")
    out_dir = DERIVED_DIR / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_xml = out_dir / ".tmp.musicxml"
    score.write("musicxml", fp=str(tmp_xml))
    xml = render.tidy_musicxml(tmp_xml.read_text(encoding="utf-8"))
    tmp_xml.unlink()
    xml_path = out_dir / f"{asset_id}.musicxml"
    xml_path.write_text(xml, encoding="utf-8")

    footer = build_footer(row, applied, recipe)
    engine = recipe["render"]["engine"]
    outputs = {"musicxml": xml_path.name, "pdf": f"{asset_id}.pdf"}
    render.render_pdf(xml, out_dir / outputs["pdf"], footer, "draft", "normal", engine)
    if recipe["render"]["large_print"]:
        outputs["pdf_large_print"] = f"{asset_id}-large-print.pdf"
        render.render_pdf(xml, out_dir / outputs["pdf_large_print"], footer, "draft", "large", engine)

    meta = {
        "asset_id": asset_id,
        "title": title,
        "composer": row.get("composer"),
        "source_file": src.name,
        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "license": {k2: row.get(k2) for k2 in ("composition_status", "edition_source", "edition_license",
                                               "attribution_text", "derivatives_allowed")},
        "recipe_file": Path(recipe_path).name,
        "recipe": recipe,
        "rules_applied": [{"id": r, "name": RULE_NAMES[r], "details": log[r]} for r in applied],
        "key_detected": f"{k.tonic.name} {k.mode}",
        "footer": footer,
        "outputs": outputs,
        "musicxml_sha256": hashlib.sha256(xml.encode("utf-8")).hexdigest(),
        "tools": {"music21": music21.__version__, "verovio": verovio.toolkit().getVersion(), "engine": engine},
        "generated_by": "deterministic rules only (no AI / ML)",
        "status": "draft",
        "reviewed_by": None,
        "reviewed_date": None,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Done: scores/derived/{asset_id}/")
    for r in meta["rules_applied"]:
        print(f"  {r['id']} {r['name']}: " + "; ".join(r["details"]))
    print("Status: draft. A person must review it, then run approve.py.")


def main():
    ap = argparse.ArgumentParser(description="Simplify a public-domain score with fixed rules.")
    ap.add_argument("recipe", nargs="?", help="path to a recipe .yaml file")
    ap.add_argument("--check", action="store_true", help="only check licenses of every file in scores/source/")
    args = ap.parse_args()
    if args.check:
        check_all()
    elif args.recipe:
        run(args.recipe)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
