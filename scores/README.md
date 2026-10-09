# Score pipeline (Phase 1.5, Part A)

Turns a public-domain or CC MusicXML score into a simplified, annotated version with fixed rules.
**No AI.** Every rule is in [`RULES.md`](RULES.md). Every output starts as a **draft**.

```
scores/
  RULES.md            ← every rule in plain English
  requirements.txt    ← Python packages
  source/             ← put input MusicXML here, named <asset_id>.musicxml
  recipes/            ← one .yaml recipe per piece (copy the sample)
  derived/<asset_id>/ ← outputs: .musicxml, .pdf, -large-print.pdf, meta.json
  pipeline/           ← the code (process.py, approve.py, selftest.py, ...)
```

## One-time setup

1. Install Python 3.10 or newer from python.org (Windows: tick "Add Python to PATH").
2. Open a terminal in this repository folder and run:

```
pip install -r scores/requirements.txt
python scores/pipeline/selftest.py
```

PDFs need one of these:
- **Mac (Verovio, default):** if you see "Cairo is not installed", install Homebrew (brew.sh), then run `brew install cairo`. If it still says so, run `export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` in the same terminal and try again.
- **Windows (easiest):** install MuseScore 4 from musescore.org, then set `engine: musescore` in the recipe.

## Make one piece

```
python scores/pipeline/process.py --check
python scores/pipeline/process.py scores/recipes/twinkle-test-fixture.yaml
```

## Approve (after a person has checked the PDF)

```
python scores/pipeline/approve.py twinkle-test-fixture "Your Name"
```

## Add a new piece

1. Check the license with `licenses/SOURCING.md`. Add a row to `licenses/assets.csv`, filling in `derivatives_allowed` (`yes`, `no`, or `share-alike`) and `source_format` (`musicxml`).
2. Save the file as `scores/source/<asset_id>.musicxml`.
3. Copy `scores/recipes/twinkle-test-fixture.yaml` to `scores/recipes/<asset_id>.yaml`, change `asset_id` and the settings.
4. Run `process.py` with the new recipe.
