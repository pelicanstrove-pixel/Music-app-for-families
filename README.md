# Piano & Music Theory Printables (Phase 1: content skeleton)

A homeschool family project: piano and music theory printables for kids ages 4–10+.
**Phase 1 is only the structure.** There is no app yet. Nothing in here is finished teaching content. Everything is a placeholder for humans to write.

## Ground rules

- **No AI-written teaching content.** Explanations, exercises, answers, and parent notes are written by people.
- Every outline item says **"DRAFT – needs educator review"** until an educator approves it.
- Sheet music and audio: human-made, public domain or CC-licensed only. Linked, never copied in. See `licenses/SOURCING.md`.
- US English. US Letter paper. Black and white printing. Large-print option. Parent answer keys.

## Folder map

```
README.md                         ← you are here
content/
  levels.json                     ← the 5 levels (Pre-reader, Levels 1–4), ages, prerequisites, goals per strand
  paths/
    pre-reader.json               ← 12-week plan skeleton for each level
    level-1.json … level-4.json
  exercise-bank/
    exercise.schema.json          ← the rules every exercise must follow (don't edit unless needed)
    example.json                  ← one empty example exercise to copy
  parametric-templates.md         ← worksheet types the generator will make, and the limits per level
  placement/
    reader-quiz-template.md       ← placement quiz for children who read
    prereader-observation-checklist.md  ← checklist a parent fills in by watching a young child
    placement-rules.json          ← how placement results turn into a suggested level (educator fills in the blanks)
licenses/
  THIRD-PARTY.md                  ← fonts, libraries and sounds inside the app, and their licenses
  candidates.csv                  ← pieces checked for license but not yet verified by a person (in the app, labeled "Under review")
  assets.csv                      ← one row per score/recording (now also: derivatives_allowed, source_format)
  SOURCING.md                     ← checklist for checking a license before adding a row
scores/                           ← Phase 1.5 Part A: rule-based score simplifier (see scores/README.md)
  candidates/                     ← draft MusicXML of candidate pieces (in the app as "Under review", see docs/REPERTOIRE-CANDIDATES.md)
  tools/mutopia_to_musicxml.py    ← converts a Mutopia LilyPond score to MusicXML (with a note check)
  RULES.md                        ← every simplification rule in plain English
app/                              ← Phase 1.5 Part B + main app
  drills.html                     ← drill sheet generator; paste into a Squarespace Code block
  DRILL-RULES.md                  ← every drill rule in plain English
  family-piano.html               ← main app (built file); paste into a Squarespace Code block
  src/family-piano.template.html  ← main app source; edit this, then run `python3 app/build.py`
  build.py                        ← inlines content, drills, font, VexFlow, piano sound and player notes into family-piano.html
  pieces/                         ← built: one drawn score per piece under review, loaded when the piece is opened (host it, see below)
  fonts/                          ← Nunito (SIL Open Font License), embedded so no font server is used
  vendor/                         ← VexFlow 4.2.2 + Bravura (draws drill sheets), embedded so the app needs no outside files
    piano/                        ← MIT piano sound for the built-in player (made by tools/extract_piano.py)
  tools/extract_piano.py          ← makes the piano sound from FluidR3Mono_GM.sf3
docs/
  UI-CONTEXT.md, UI-SPEC.md       ← UI design context and the approved UI spec
  UI-SPEC-REVIEW.md               ← where the two differ (owner decisions needed) + progress/backup format
  MIDI-PLAYER-OPTIONS.md          ← research: built-in player options and owner decisions
  REPERTOIRE-CANDIDATES.md        ← research: public-domain pieces to ship, license evidence, steps to ship one
```

**assets.csv new columns:** `derivatives_allowed` = `yes`, `no`, or `share-alike` (may we make a simplified version?). `source_format` = `musicxml`, `mxl`, or `xml` for files in `scores/source/` (use `n/a` for linked-only items).

**Strands:** Pre-reader uses Kodály-style strands: `singing`, `rhythm`, `solfege`, `pre_staff`.
Levels 1–4 use: `technique`, `theory`, `repertoire`, `ear_training`.

## Hosting the piece files

`app/family-piano.html` (about 2 MB) holds everything except the drawn scores of the pieces under review. Each of those
is in its own file in `app/pieces/` (78 files, about 7 MB together) and is loaded the first time a family opens that piece.
Without them a piece still plays (player, wait-for-me, game, checking); only the sheet music on screen is missing.

The repository is private, so the files must be put somewhere public that serves `.js` files, for example:

1. **GitHub Pages:** make the repo public (or use a paid plan), then Settings → Pages → Deploy from branch `main`, folder `/`.
   The folder is then `https://pelicanstrove-pixel.github.io/Music-app-for-families/app/pieces/`.
2. **Any static host** (Netlify, Cloudflare Pages, your own web space): upload the `app/pieces/` folder.

Then build with that address and paste the new `app/family-piano.html` into Squarespace:

```
python3 app/build.py --pieces-url https://pelicanstrove-pixel.github.io/Music-app-for-families/app/pieces/
```

Without `--pieces-url` the app looks for a `pieces/` folder next to the page, which works when the app is opened
from its own folder (for example `app/family-piano.html` on your computer). `--no-candidates` leaves the pieces under review out.

## How to fill in content

You can edit these files right on GitHub: open a file, click the ✏️ pencil, edit, then "Commit changes".

**Editing JSON files safely** (`.json`):
- Only change text **between the quote marks** `"like this"`. Leave the `{ } [ ] , :` symbols alone.
- After editing, paste the whole file into a free checker such as jsonlint.com to make sure nothing broke.
- Never change an `id` once it exists. The app will use ids to save each child's progress.

**Workflow for every item:**
1. **Write.** The author fills in empty fields (`description`, `focus`, `topic`, `parent_notes`, `body`, `answer_key`…) and puts their name in `author` (exercises).
2. **Review.** An educator reads it, fixes it, and puts their name in `reviewed_by`.
3. **Approve.** Change `"status"` from `"DRAFT – needs educator review"` (or `"draft"` for exercises) to `"approved"`. Only approved items will appear in the app.

**Where things go:**
| I want to… | Edit this |
|---|---|
| Change a level's age range or goals | `content/levels.json` |
| Plan what happens in week 3 of Level 2 | `content/paths/level-2.json` → the week with `"week": 3` |
| Add a worksheet or exercise | Copy the exercise in `exercise-bank/example.json` into a new file such as `exercise-bank/level-1-theory.json`, give it a new `id`, fill it in |
| Change what the worksheet generator may produce | `content/parametric-templates.md` (the level tables) |
| Write the placement quiz or checklist | the two files in `content/placement/` |
| Set how placement results suggest a level | `content/placement/placement-rules.json` (then run `python3 app/build.py`) |
| Add a piece of music or recording | Check it with `licenses/SOURCING.md`, then add a row to `licenses/assets.csv` (open it in Google Sheets or Excel, save as CSV) |
| Use that piece in a week | Put its `asset_id` in that week's `repertoire_ids` list |

**Id patterns:** weeks are `level-1-w03`; strand items are `level-1-w03-theory-01`; exercises are like `l1-theory-0001`; assets are like `bach-minuet-g-mutopia`.

## Notes for later phases (already built into the shapes)

- The app will be one self-contained HTML/JS file in a Squarespace code block. It will read these JSON files bundled in at build time.
- No server. Progress is saved in the browser (localStorage), keyed by the stable ids above, with an export/import backup file.
- Scores and audio are referenced by `asset_id` → `url` in `assets.csv`. They are linked, never embedded.
- Printables: US Letter, black and white, `large_print_ok` on each exercise, `answer_key` for parents.
