# UI design context: Piano & Music Theory app for families

> Paste or upload this file into a Claude chat to work out the user interface.
> When the design is settled, bring the result (screen list, wireframes, decisions) back to Claude Code to build.
> Snapshot of the repo as of 2026-10-09 (Phase 1 + Phase 1.5 done; the main app is not built yet).

---

## 1. What the product is

A homeschool family project: **piano and music theory for kids ages 4–10+**, run by a parent.
Mostly **printables** (worksheets, drill sheets, practice charts, simplified sheet music) plus a light
on-screen "plan" that tells the parent what to do each week.

**Who uses it**
- **Parent / teacher (primary user).** Picks a level, follows a 12-week plan, prints sheets, marks progress, reads answer keys and parent notes. Often not a musician.
- **Child (secondary).** Mostly works on paper. Pre-readers (4–6) can't read; a grown-up reads directions aloud.
- **Educator / reviewer (behind the scenes).** Writes and approves content by editing files on GitHub, not through the app.
- Families may have **more than one child**, at different levels.

---

## 2. Hard constraints (the UI must live within these)

| Constraint | What it means for design |
|---|---|
| **One self-contained HTML/JS file pasted into a Squarespace Code block** | No routing server, no build-time framework assumptions in the page. Must look fine embedded inside someone else's Squarespace page (unknown fonts/colors around it). All CSS scoped under one root id (current pattern: `#pd-drills`, class prefix `pd-`). |
| **No server, no accounts** | Progress saved in the browser (`localStorage`) keyed by stable content ids. Needs an **Export / Import backup file** flow, because clearing the browser loses everything. |
| **Content is bundled JSON** | The app reads `levels.json`, the 12-week `paths/*.json`, and exercise-bank files baked in at build time. |
| **Only `"approved"` content is shown** | Today everything is `"DRAFT – needs educator review"`. The UI needs a sensible "nothing approved yet / draft" state, and drafts must be clearly labeled if shown at all. |
| **No AI-written teaching content** | The UI must not generate explanations or feedback text. Wording comes from content files or a fixed `TEXT` table an educator can rewrite. |
| **Print** | US Letter, 0.5 in margins, **black and white only (no gray fills)**, large-print option, separate parent **answer-key page**. On-screen controls hidden when printing. |
| **Scores & audio are linked, never embedded** | Repertoire shows a link + license credit (`attribution_text`) from `licenses/assets.csv`. |
| **US English**, plain simple wording | Parents of varied skill; keep labels short and friendly. |
| Accessibility | Large text option, high contrast, works on a phone/tablet (parent at the piano) and desktop (printing). |

---

## 3. Content model (what the screens display)

### Levels (`content/levels.json`)
| id | name | ages | pedagogy | strands |
|---|---|---|---|---|
| `pre-reader` | Pre-reader | 4–6 | Kodály | singing, rhythm, solfege, pre_staff |
| `level-1` | Level 1 | 6–10 | graded | technique, theory, repertoire, ear_training |
| `level-2` | Level 2 | 7–11 | graded | same |
| `level-3` | Level 3 | 8–12 | graded | same |
| `level-4` | Level 4 | 9–14 | graded | same |

Each level has `prerequisites`, `goals` per strand (each goal: `id`, `topic`, `description`, `status`), and `parent_notes`.
Example goal topics: Level 1 theory → "Keyboard geography", "Staff and clefs", "Note values". Pre-reader solfege → "Sol-mi", "La", "Hand signs".

### 12-week path (`content/paths/<level>.json`) — one per level
Each **week** (`id` like `level-1-w03`):
```json
{
  "id": "level-1-w03", "week": 3, "focus": "", "status": "DRAFT – needs educator review",
  "strand_items": {            // one or more items per strand
    "theory": [{ "id": "level-1-w03-theory-01", "topic": "", "goal_ref": "", "status": "..." }]
    // ...technique, repertoire, ear_training (or the 4 Kodály strands)
  },
  "parent_notes": "",
  "practice_chart": { "minutes_per_day": null, "days_per_week": null, "items": [] },
  "repertoire_ids": [],        // -> asset_id rows in licenses/assets.csv
  "worksheet_topics": [],
  "exercise_ids": []           // -> exercise bank
}
```

### Exercise bank (`content/exercise-bank/*.json`)
Each exercise: `id`, `level`, `strand`, `topic`, `age_min/max`, `type` (`fixed` | `parametric`),
`template_id` + `params` (parametric only), `author`, `reviewed_by`, `status` (`draft`|`approved`),
`body` (student-facing), `answer_key` (parent-facing), `large_print_ok`, optional `asset_ids`.

### Worksheet templates (`content/parametric-templates.md`)
`note-naming`, `rhythm-counting`, `intervals`, `key-signatures`, `keyboard-geography`.
Shared params: `count` 4–24, `large_print`, `seed`, `answer_key`. Each level restricts what's allowed (e.g. Level 1 note naming = treble C4–G4 or bass C3–G3, no sharps/flats).

### Placement (`content/placement/`)
- **Reader quiz** (sections A–E: keyboard, note reading, rhythm, intervals & keys, playing check at the piano) → suggested starting level.
- **Pre-reader observation checklist**: parent marks Not yet / Sometimes / Usually across Singing, Rhythm, Solfege, Pre-staff, Attention → suggests pre-reader week 1, later week, or try the reader quiz.
- Both are printable today; the questions themselves are still placeholders.

### Repertoire / assets (`licenses/assets.csv`)
Columns used by the UI: `asset_id`, `title`, `composer`, `url`, `attribution_text`, license columns.
Simplified scores produced by the score pipeline (`scores/derived/<asset_id>/`): a `.pdf`, a `-large-print.pdf`, and `meta.json` (with approval status).

---

## 4. What already exists: the drill sheet generator (`app/drills.html`)

The only built UI so far. Its look is the current house style; the main app should feel like the same family.

**Controls (a card above the printed pages, CSS grid of fields):**
Child's name (optional) · Level · Drill type · Option · Number of items (4–24) · Seed + "New" button ·
☐ Large print · ☐ Ink-saving black & white · ☑ Include answer key · **[Make sheet]** (primary, black) · [Print]

**Drill types:** Name the Notes · Keyboard Map · Count the Rhythm · Name the Intervals · Key Signatures · Listen and Look (pre-reader only: high/low, long/short, step/skip with simple shapes).

**Output:** on-screen US Letter "paper" pages (drop shadow) with header (Name / Date line, title, instruction), a numbered grid of items drawn with VexFlow (SVG), footer with seed + settings + "DRAFT" notice. Answer key starts on a new page with an "ANSWER KEY (for the parent)" banner.

**Style:** Helvetica/Arial, black on white, 1px #999 card border, 4–6px radius, #fafafa control panel, black primary button. Very plain, print-first. All wording in a `TEXT` table so an educator can rewrite it.

**Same seed + same settings = identical sheet** (seeded random, no AI). Seed is printed so a parent can re-print.

---

## 5. Screens / flows to design (proposal — open for discussion)

1. **Welcome / first run** — what this is, the "nothing is lost but this browser holds your data" message, add first child.
2. **Children** — add/edit/switch child (name, age, current level, current week). Multi-child families.
3. **Placement** — choose reader quiz vs. pre-reader checklist → print → enter results → suggested level (parent can override).
4. **Home / This week** (the main screen) — for the selected child: level + week N of 12, week `focus`, strand items as a checklist, parent notes, practice chart, this week's pieces (links + credits), worksheets/drills to print, "mark week done → next week".
5. **Level overview** — the 12 weeks at a glance, goals per strand, progress per week.
6. **Practice chart** — printable weekly chart (minutes/day, days/week, items) and/or on-screen tick boxes.
7. **Printables** — drill generator (existing), exercise-bank worksheets, simplified scores, placement sheets; each with large-print + answer-key options.
8. **Repertoire library** — approved pieces by level, link out, show license/credit.
9. **Backup** — Export progress file / Import progress file / reset.
10. **Parent help** — how to use the plan, glossary (strands, solfege, etc.).

**States to cover:** content not yet approved (draft), no children yet, finished week 12 (move up a level?), missing/blocked links, phone vs. desktop, print preview.

---

## 6. Questions to settle in the design chat

- Navigation inside a single Squarespace block: tabs? a left menu? a single scrolling page with sections?
- How much should the child interact on screen vs. everything on paper?
- One child at a time with a switcher, or a family dashboard?
- What "progress" means: per strand item ticked, per week completed, per exercise done? (Saved by content id.)
- Should drafts ever be visible (e.g. a "preview drafts" toggle for the family/educator)?
- How prominent is the backup/export, and should the app remind the parent?
- Visual tone: keep the stark print-first black & white, or add a friendlier on-screen color palette (prints stay B&W)?
- Pre-reader mode: bigger icons, read-aloud cues, fewer words?

---

## 7. What to bring back to Claude Code

When the chat is done, ask it to produce a short spec with:
1. Final screen list and navigation.
2. A wireframe or description per screen (fields, buttons, states).
3. The `localStorage` progress shape (keyed by the content ids above) and the export file format.
4. Visual rules (fonts, colors on screen, spacing, print rules).
5. Any new wording, marked as **draft wording for educator review** (no AI-written teaching content).

Then paste that spec into Claude Code in this repo to build it.
