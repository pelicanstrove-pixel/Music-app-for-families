# Parametric worksheet templates

> **Every rule below is DRAFT – needs educator review.** These are only proposed limits on what the generator may produce. They are not teaching content. Change any value you disagree with.

The app (in a later phase) will build worksheets from these templates. An exercise in the exercise bank with `"type": "parametric"` names one `template_id` below and fills in `params`.

**Print rules for all templates:** US Letter (8.5 × 11 in), black and white only (no gray fills), 0.5 in margins. There is a large-print option and a separate answer-key page for the parent.

**Shared parameters (all templates):**

| Parameter | Values | Notes |
|---|---|---|
| `count` | 4–24 | Number of questions per sheet |
| `large_print` | true / false | Larger staff, notes, and text; fewer items per page |
| `seed` | whole number | Lets you print the same sheet again |
| `answer_key` | true / false | Adds a parent answer page |

---

## 1. `note-naming`: name the note on the staff

| Parameter | Values |
|---|---|
| `clef` | treble, bass, grand |
| `note_range` | lowest–highest note, e.g. `C4–G4` |
| `ledger_lines_max` | 0–3 |
| `accidentals` | none, sharps, flats, both |
| `answer_format` | write letter, circle choice, match |

| Level | Valid values (DRAFT – needs educator review) |
|---|---|
| pre-reader | Not used. Pre-staff only: high/low icons, no clef |
| level-1 | clef: treble or bass. range: C4–G4 (treble), C3–G3 (bass). ledger 0–1 (middle C only). accidentals: none |
| level-2 | clef: any. range: C3–C5. ledger 0–1. accidentals: none |
| level-3 | clef: any. range: A2–E5. ledger 0–2. accidentals: sharps or flats |
| level-4 | clef: any. range: F2–A5. ledger 0–3. accidentals: both |

## 2. `rhythm-counting`: write the counts / clap the rhythm

| Parameter | Values |
|---|---|
| `time_signature` | 2/4, 3/4, 4/4, 6/8 |
| `note_values` | whole, half, dotted-half, quarter, eighth-pair, single eighth, dotted-quarter, sixteenth |
| `rests` | list of allowed rest values |
| `ties` | true / false |
| `measures` | 1–8 per line |
| `syllables` | kodaly (ta, ti-ti), numbers (1 & 2 &) |

| Level | Valid values (DRAFT – needs educator review) |
|---|---|
| pre-reader | Stick notation only (no staff). values: quarter, eighth-pair, quarter rest. time: 2/4 or 4/4. syllables: kodaly. measures 1–4 |
| level-1 | time: 2/4, 3/4, 4/4. values: whole, half, dotted-half, quarter. rests: quarter, half. ties: no |
| level-2 | adds eighth-pair and whole rest. syllables: either |
| level-3 | adds dotted-quarter, single eighth, eighth rest, ties. time: adds 6/8 |
| level-4 | adds sixteenths. all time signatures above |

## 3. `intervals`: identify or draw an interval

| Parameter | Values |
|---|---|
| `mode` | identify, draw |
| `direction` | up, down, both |
| `presentation` | melodic, harmonic, both |
| `sizes` | 2nd–8th (numbers only) |
| `qualities` | none (number only), major/minor, perfect, aug/dim |
| `clef`, `note_range` | as in note-naming |

| Level | Valid values (DRAFT – needs educator review) |
|---|---|
| pre-reader | Not used. (Ear only: same/different, step/skip on icons) |
| level-1 | sizes: 2nd, 3rd. melodic only. qualities: none. mode: identify |
| level-2 | sizes: 2nd–5th. melodic or harmonic. qualities: none |
| level-3 | sizes: 2nd–8th. qualities: major/minor 2nd–3rd, perfect 4th/5th/8th. mode: identify or draw |
| level-4 | sizes: 2nd–8th. all qualities incl. aug/dim. direction: both |

## 4. `key-signatures`: name or write a key signature

| Parameter | Values |
|---|---|
| `mode` | identify, write |
| `keys` | list of keys, e.g. `C, G, F` |
| `include_minor` | true / false |
| `clef` | treble, bass, grand |

| Level | Valid values (DRAFT – needs educator review) |
|---|---|
| pre-reader | Not used |
| level-1 | Not used |
| level-2 | keys: C, G, F (major only). mode: identify |
| level-3 | keys: up to 2 sharps / 2 flats, major. mode: identify or write |
| level-4 | keys: up to 4 sharps / 4 flats. include_minor: yes (relative minors) |

## 5. `keyboard-geography`: find and label keys on a printed keyboard

| Parameter | Values |
|---|---|
| `octaves_shown` | 1–3 |
| `task` | find groups of 2/3 black keys, label white keys, label black keys, mark a note, mark half/whole steps |
| `labels` | letters, solfege, none |
| `start_note` | letter + octave, e.g. `C4` |

| Level | Valid values (DRAFT – needs educator review) |
|---|---|
| pre-reader | octaves 1. task: black-key groups, high/low side. labels: none or solfege |
| level-1 | octaves 1–2. task: label white keys, mark a note |
| level-2 | octaves 2. adds label black keys (sharp/flat names) |
| level-3 | octaves 2–3. adds half/whole steps |
| level-4 | octaves 3. all tasks |

---

## Adding a new template

1. Add a section above with a new `template_id`, its parameters, and a level table.
2. Mark the level table "DRAFT – needs educator review" until an educator signs off.
