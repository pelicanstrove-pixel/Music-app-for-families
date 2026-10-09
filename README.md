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
licenses/
  assets.csv                      ← one row per score/recording (now also: derivatives_allowed, source_format)
  SOURCING.md                     ← checklist for checking a license before adding a row
scores/                           ← Phase 1.5 Part A: rule-based score simplifier (see scores/README.md)
  RULES.md                        ← every simplification rule in plain English
app/                              ← Phase 1.5 Part B
  drills.html                     ← drill sheet generator; paste into a Squarespace Code block
  DRILL-RULES.md                  ← every drill rule in plain English
```

**assets.csv new columns:** `derivatives_allowed` = `yes`, `no`, or `share-alike` (may we make a simplified version?). `source_format` = `musicxml`, `mxl`, or `xml` for files in `scores/source/` (use `n/a` for linked-only items).

**Strands:** Pre-reader uses Kodály-style strands: `singing`, `rhythm`, `solfege`, `pre_staff`.
Levels 1–4 use: `technique`, `theory`, `repertoire`, `ear_training`.

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
| Add a piece of music or recording | Check it with `licenses/SOURCING.md`, then add a row to `licenses/assets.csv` (open it in Google Sheets or Excel, save as CSV) |
| Use that piece in a week | Put its `asset_id` in that week's `repertoire_ids` list |

**Id patterns:** weeks are `level-1-w03`; strand items are `level-1-w03-theory-01`; exercises are like `l1-theory-0001`; assets are like `bach-minuet-g-mutopia`.

## Notes for later phases (already built into the shapes)

- The app will be one self-contained HTML/JS file in a Squarespace code block. It will read these JSON files bundled in at build time.
- No server. Progress is saved in the browser (localStorage), keyed by the stable ids above, with an export/import backup file.
- Scores and audio are referenced by `asset_id` → `url` in `assets.csv`. They are linked, never embedded.
- Printables: US Letter, black and white, `large_print_ok` on each exercise, `answer_key` for parents.
