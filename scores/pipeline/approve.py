"""Mark a derived score as approved after a person has checked it (rule O6).

Usage:
  python scores/pipeline/approve.py <asset_id> "Reviewer Name"

It checks the MusicXML has not changed since it was made, sets status to
"approved", records the reviewer and date, and re-draws the PDFs without
the DRAFT stamp. Running process.py again resets everything to draft.
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    asset_id, reviewer = sys.argv[1], sys.argv[2].strip()
    if not reviewer:
        sys.exit("Please give the reviewer's name.")
    out_dir = ROOT / "scores" / "derived" / asset_id
    meta_path = out_dir / "meta.json"
    if not meta_path.exists():
        sys.exit(f"No meta.json in scores/derived/{asset_id}/. Run process.py first.")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    xml = (out_dir / meta["outputs"]["musicxml"]).read_text(encoding="utf-8")
    if hashlib.sha256(xml.encode("utf-8")).hexdigest() != meta["musicxml_sha256"]:
        sys.exit("The MusicXML changed after it was made. Run process.py again, then review again.")
    engine = meta["tools"]["engine"]
    render.render_pdf(xml, out_dir / meta["outputs"]["pdf"], meta["footer"], "approved", "normal", engine)
    if "pdf_large_print" in meta["outputs"]:
        render.render_pdf(xml, out_dir / meta["outputs"]["pdf_large_print"], meta["footer"], "approved", "large", engine)
    meta["status"] = "approved"
    meta["reviewed_by"] = reviewer
    meta["reviewed_date"] = datetime.date.today().isoformat()
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Approved {asset_id} (reviewed by {reviewer}). DRAFT stamp removed from the PDFs.")


if __name__ == "__main__":
    main()
