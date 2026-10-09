# Score simplification rules (plain English)

> **DRAFT – needs educator review.** These are the only things the pipeline does to a score.
> There is **no AI or machine learning** anywhere. Every step is a fixed rule written by a person,
> so the same file + the same recipe always gives exactly the same output.
> Each rule has an ID (like `T4`). The PDF footer and `meta.json` list the IDs that were used.

Code for each rule: `scores/pipeline/` (`licenses.py`, `extract.py`, `transform.py`, `annotate.py`, `render.py`).

## Order the rules run in

1. License gate (L1–L6). If any fails, stop.
2. E1 measure range
3. T1 remove ornaments → T4 transpose
4. Find the key and the chords (used by A3, A4, A5), using both hands and every chord note
5. T2 drop inner voices → T3 even dotted rhythms
6. E2 / E3 / E4 pick a hand or the melody
7. T5 limit range
8. A1 → A6 annotations
9. O1–O6 outputs

**Staff convention:** the first (top) staff is the right hand. The last (bottom) staff is the left hand.

---

## L. License gate (always on)

The source file must be `scores/source/<asset_id>.musicxml` (or `.mxl`, `.xml`) and have a row in `licenses/assets.csv` with the same `asset_id`.

| ID | Rule |
|---|---|
| L1 | Refuse if there is no row for the file in `assets.csv`. |
| L2 | Refuse if `composition_status` is empty or `unknown`. |
| L3 | Refuse if `derivatives_allowed` is not `yes` or `share-alike`. |
| L4 | Refuse if `edition_license` is a No-Derivatives license (contains `ND`, e.g. CC-BY-ND, CC-BY-NC-ND). This applies even if L3 says yes. |
| L5 | Refuse if `verified_by` is empty (a person must check the license first). |
| L6 | Refuse if `source_format` is not `musicxml`, `mxl` or `xml`. |

The reason is printed. Check every file at once with `python scores/pipeline/process.py --check`.

## E. Extract

| ID | Recipe setting | Rule |
|---|---|---|
| E1 | `extract.measures: [first, last]` | Keep only those measures (printed measure numbers, both ends included). |
| E2 | `extract.part: right_hand` | Keep only the top staff. |
| E3 | `extract.part: left_hand` | Keep only the bottom staff. |
| E4 | `extract.part: melody` | Keep only the top staff. In each measure keep only voice 1. In every chord keep only the highest note. |

`extract.part: both` keeps all staves (no E rule listed).

## T. Transform

| ID | Recipe setting | Rule |
|---|---|---|
| T1 | `remove_ornaments: true` (on by default) | Delete grace notes. Delete trill, mordent, turn and tremolo marks; the main note stays. Delete trill wavy lines. Fermatas, accents and dynamics stay. |
| T2 | `drop_inner_voices: true` | In each staff, if a measure has 2+ voices, keep one: the highest voice in the top staff, the lowest voice in other staves. In chords of 3 or more notes, keep only the top and bottom notes. |
| T3 | `simplify_dotted_rhythms: true` (**off by default**) | A dotted note followed by a note one third its length (dotted quarter + eighth, dotted eighth + sixteenth, dotted half + quarter) becomes two equal notes (quarter + quarter, etc.). Only inside one measure, only notes (not rests), only when neither note is tied. Everything else stays. |
| T4 | `transpose_to_key: G` | Find the key (see "Key finding" below). Move every note so the key note becomes the new one, keeping major/minor. Take the shorter way (up or down); if both are equal (6 semitones), go down. Key signatures move too. |
| T5 | `limit_range_semitones: 12`, `phrase_measures: 4` | Done for each staff separately. Cut the staff into "phrases" of 4 measures (or the number you set). The allowed window starts at the lowest note of the first phrase and goes up the number of semitones you set (12 = one octave). A phrase that sticks out of the window is moved by whole octaves until it fits; the smallest move is tried first, down before up (−1, +1, −2, +2, −3, +3 octaves). A phrase that is wider than the window by itself is left alone, and this is written in `meta.json`. |

## A. Annotate

| ID | Recipe setting | Rule |
|---|---|---|
| A1 | `note_names: true` | Write the letter name **above** every note, on every staff. Sharps as `#`, flats as `b`. Chords: names from top to bottom joined with `/` (e.g. `G/E/C`). No octave numbers. |
| A2 | `counting: true` | Write counts **under** every note and rest of the top staff. The beat is the time signature's bottom number (in 6/8, 9/8, 12/8 every eighth note is counted). On a beat: the beat number. Held notes add the beats they hold with dashes: a half note on beat 3 is `3-4`. Between beats: `&` (half way), `e` and `a` (quarter and three-quarter way), `la` and `li` (triplets), anything else `+`. Rests: the count in parentheses, e.g. `(3)`. |
| A3 | `solfege: true` | Movable-do solfege **under** the top staff (second line, below the counts). Major: the key note is `do`. Minor: the key note is `la` (do = the relative major). Raised notes: di, ri, fi, si, li. Lowered notes: ra, me, se, le, te. Any other change: the plain syllable + `#` or `b`. Chords: top note only. |
| A4 | `chord_symbols: true` | For every beat, gather all notes sounding in that beat in both hands. If they contain 3 or more different note names, music21 names the chord (e.g. `G`, `D/F#`). The symbol is printed **above** the top staff, only when it changes. If music21 cannot name the chord, nothing is printed. |
| A5 | `roman_numerals: true` | Same beats as A4. music21 gives the Roman numeral in the found key. Printed **under** the bottom staff; the first one shows the key (e.g. `G: I`). Only the usual inversion figures are kept (6, 64, 7, 65, 43, 42); any other added-note figure is dropped. |
| A6 | `suggested_fingering: true` (**off by default**) | Labeled **"Suggested fingering (rule-based, not checked)"** on the music and in the footer. Five-finger-position rule: walk the single notes of a staff in order; a "position" is the longest run of notes that fits inside five letter names. Right hand: the lowest letter of the position is finger 1, the next 2, up to 5. Left hand: the lowest letter is 5, up to 1. A chord or rest ends a position. Chords get no fingers. Fingers are printed only on the first note of each new position (`fingering_every_note: true` prints every note). Known limits: it does not avoid the thumb on black keys and does not plan finger crossings. |

**Key finding (used by T4, A3, A5):** music21's standard key analysis (Krumhansl–Schmuckler key profiles). It is a fixed formula, not machine learning. The key found is written in `meta.json` as `key_detected`. If it is wrong, do not use T4/A3/A5 for that piece.

## O. Outputs

| ID | Rule |
|---|---|
| O1 | Everything goes to `scores/derived/<asset_id>/`: `<asset_id>.musicxml`, `<asset_id>.pdf`, `<asset_id>-large-print.pdf`, `meta.json`. |
| O2 | Every output starts as `"status": "draft"`, `"reviewed_by": null`. Every PDF page says **DRAFT – needs review** at the top. Running `process.py` again always resets to draft. |
| O3 | PDFs are US Letter (8.5 × 11 in), black and white. Drawn by Verovio (default) or MuseScore 4 (`render.engine: musescore`). |
| O4 | Large print: the same music, about 1.4× bigger, with a larger footer. Turn off with `render.large_print: false`. |
| O5 | Footer on every page: "Simplified from [composer], [source] / [license]. [attribution]. Rules: [IDs and names]." For share-alike licenses it adds that the arrangement keeps the same license. |
| O6 | `approve.py` sets `"status": "approved"`, the reviewer's name and the date, and redraws the PDFs without the DRAFT stamp. It refuses if the MusicXML changed after it was made. |
| O7 | Repeatable output: the MusicXML has no date and fixed part ids, and PDFs have fixed metadata, so the same input gives the same files. |
