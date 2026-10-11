# UI-SPEC v1 vs UI-CONTEXT: check (2026-10-11)

UI-SPEC says: if it conflicts with UI-CONTEXT, ask the owner. These are the places where they differ.
The app follows **UI-SPEC** for now; each item says what the app does today.

## Needs an owner decision

| # | Topic | UI-CONTEXT says | UI-SPEC says | App today |
|---|---|---|---|---|
| 1 | Draft content | "Only `approved` content is shown"; drafts clearly labeled *if shown at all* | Show unreviewed content with a "Draft content" chip and `[… – educator to write]` placeholders | Shows drafts with the chip (nothing is approved yet, so hiding drafts would leave every screen empty) |
| 2 | Outside font vs. "no tracking" | One self-contained file; must sit inside an unknown Squarespace page | Nunito font; "no tracking" | Loads Nunito from Google Fonts, which sees the visitor's IP address. Falls back to the system font if blocked. Option: self-host the font or drop it |
| 3 | Placement | A full flow: choose quiz or checklist → print → enter results → suggested level (parent can override) | Only "Help & placement": mode guide per child type, FAQ | Placement sheets can be printed (Print screen); the parent picks the level by hand when adding a child. No results entry or suggestion |
| 4 | First-run welcome | Its own screen (what this is, data stays in this browser, add first child) | Not listed | Family screen shows a welcome line and the Add-a-child form |
| 5 | Printables list | Drills, exercise-bank worksheets, simplified scores, placement sheets | "pick one sheet" (no list) | Week plan, practice chart, 12-week overview, drill sheet, placement quiz, pre-reader checklist. Exercise-bank worksheets and simplified-score PDFs are not in the list yet |
| 6 | Level overview | Goals per strand on the 12-week screen | All 12 weeks: 4x3 grid only | Grid only; level goals are printed on the "12-week overview" answer-key page |
| 7 | After week 12 | "Move up a level?" | Not covered | "All 12 weeks done!" screen with a "Start Level N" button |
| 8 | Parent help glossary | Glossary (strands, solfege, …) | FAQ only | FAQ only |
| 9 | Look of the drill sheets | House style: plain Helvetica, black on white | Nunito + color palette on screen; print stays B&W | Drill **controls** restyled to match the app; drill **pages** unchanged |
| 10 | Mode names | n/a | "final mode names" are an open item | Standard / Beginner reader / Toddler |

## Not conflicts, but missing from both

- **Score links.** `licenses/assets.csv` stores repo paths (`scores/...`). These do not work from a Squarespace page. The build turns them into GitHub links (`SCORE_BASE_URL` in `app/build.py`). If the repo is private, families can't open them: host the PDFs somewhere public and change `SCORE_BASE_URL`.
- **Progress format.** UI-CONTEXT asked the spec to define it; the spec doesn't. Defined below.

## Progress format (as built)

`localStorage["familyPiano.v1"]`:

```json
{
  "version": 1,
  "activeId": "c…",
  "lastBackup": "2026-10-11T12:00:00.000Z",
  "children": [{
    "id": "c…", "name": "Ada", "age": 8,
    "level": "level-1", "mode": "standard",
    "week": 3, "complete": false,
    "done":    { "level-1-w01-theory-01": true },
    "learned": { "<asset_id>": true }
  }]
}
```

`mode` is `standard`, `reader` or `toddler`. `done` is keyed by strand-item ids from `content/paths/*.json`; `learned` by `asset_id` from `licenses/assets.csv`.

Backup file (`family-piano-backup-YYYY-MM-DD.json`): `{ "app": "family-piano", "format": 1, "exported": "<ISO time>", "state": <the object above> }`.
