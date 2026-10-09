# Drill sheet rules (`app/drills.html`)

> **DRAFT – needs educator review.** Every sheet prints "DRAFT – generator rules need educator review"
> until an educator approves these rules. To approve: in `drills.html` change `var RULES_STATUS = 'draft';`
> to `'approved'`.
>
> **No AI.** Sheets are made by the fixed rules below and a seeded random-number generator.
> The same seed + the same settings always give the same sheet and the same answer key.

## General rules

| ID | Rule |
|---|---|
| G1 | **Seed.** Every sheet uses one whole number (the seed). It is printed at the bottom of every page with the level, drill, option and number of items. Type the same values in again to get the identical sheet. "New" picks a new seed. |
| G2 | **Random numbers** come from a simple formula (mulberry32) started from the seed. Nothing else (time, name, print size) changes the items. |
| G3 | **Answer key** is drawn from the same list of items, so it always matches. It starts on a new page. |
| G4 | **Level limits** are copied from `content/parametric-templates.md` into the `LIMITS` section of `drills.html`. If you change one, change the other. |
| G5 | **No back-to-back repeats:** the same note, interval or key is not used twice in a row (up to 20 tries, then allowed). |
| G6 | **Wording:** every sentence on the sheet is in the `TEXT` section of `drills.html` (draft wording; an educator should rewrite it). |
| G7 | **Print:** US Letter, 0.5 in margins, black and white. Controls are hidden when printing. Items are spread over as many pages as needed. |
| G8 | **Large print:** same items, fewer per page, bigger music and text. |
| G9 | **Ink-saving:** black keys are striped instead of solid, pre-reader shapes are outlines, the header line is thin. |
| G10 | **Number of items:** 4 to 24. |

## Note naming (`note-naming`)

| Level | Rule |
|---|---|
| Pre-reader | Not offered. |
| Level 1 | Treble (C4–G4) or bass (C3–G3). At most 1 ledger line. No sharps or flats. |
| Level 2 | Treble, bass or grand staff. Notes C3–C5 that need at most 1 ledger line. No sharps or flats. |
| Level 3 | Notes A2–E5, at most 2 ledger lines. Each sheet uses only sharps **or** only flats (chosen by the seed); about 1 note in 3 gets one. |
| Level 4 | Notes F2–A5, at most 3 ledger lines. Sharps and flats mixed; about 1 note in 3 gets one. |

- Every note is a whole note. All allowed natural notes are equally likely.
- Grand staff: middle C and higher go on the treble staff, lower notes on the bass staff.
- E♯, B♯, C♭ and F♭ are never used.
- Answer: letter name with ♯ or ♭.

## Keyboard geography (`keyboard`)

Keyboards start on C and end on C.

| Level | Octaves | Tasks |
|---|---|---|
| Pre-reader | 1 | circle groups of 2 black keys, circle groups of 3 black keys, high/low (circle the higher or lower of two dotted keys at least 3 white keys apart) |
| Level 1 | 1–2 | name a dotted white key, put an X on every key with a given letter |
| Level 2 | 2 | adds: name a dotted black key (answer gives both names, e.g. C♯ / D♭) |
| Level 3 | 2–3 | adds: two dotted keys a half step or whole step apart; write H or W |
| Level 4 | 3 | all of the above except high/low |

"Mixed" picks a task for each item from the level's list; choosing one task uses only that task.

## Rhythm counting (`rhythm`)

Each item is 2 measures in one time signature on a one-line staff.

| Level | Time | Note and rest blocks |
|---|---|---|
| Pre-reader | 2/4, 4/4 | Stick notation, no staff: ta (one stick), ti-ti (two joined sticks), quarter rest (Z mark). Kodály syllables. |
| Level 1 | 2/4, 3/4, 4/4 | whole, dotted half, half, quarter, quarter rest, half rest |
| Level 2 | same | adds eighth pair and whole-measure rest; counts or Kodály syllables |
| Level 3 | adds 6/8 | adds dotted quarter + eighth, single eighth with eighth rest, ties |
| Level 4 | same | adds sixteenths (four 16ths, eighth + two 16ths, two 16ths + eighth) |

- **Filling a measure:** start at beat 1. Pick a block that fits the beats left (notes are 3× as likely as rests; a whole-measure rest is less likely). Half notes start on beat 1 or 3 in 4/4; dotted halves and wholes start on beat 1.
- **6/8:** counted 1–6 in eighths. Each half of the bar (3 eighths) is one block: dotted quarter, dotted-quarter rest, quarter + eighth, eighth + quarter, three eighths (Level 4 adds two 16ths + two eighths), or one dotted half for the whole bar. Kodály option skips 6/8.
- **Ties (Level 3–4):** if measure 1 ends with a quarter or half and measure 2 starts with a quarter, they are tied 4 times in 10.
- **Counts in the answer key:** the beat number on a beat; held beats joined with dashes (`3-4`); `&` half way; `e` and `a` for sixteenths. Parentheses mean "don't play a new sound here": rests and tied notes, e.g. `(2)`.
- **Kodály syllables:** ta, ta-a, ta-a-a, ta-a-a-a, ti ti, tam ti, ti-ka; rests are written (rest).

## Interval identification (`intervals`)

Notes use the same range and ledger limits as note naming at that level.

| Level | Rule |
|---|---|
| Pre-reader | Not offered (see the pre-reader step/skip set). |
| Level 1 | 2nds and 3rds, one after the other (melodic), going up, no sharps/flats. Answer: number only. |
| Level 2 | 2nds–5ths, melodic or together (harmonic), going up, no sharps/flats. Answer: number only. |
| Level 3 | 2nds–8ves, melodic or harmonic, going up. Major/minor 2nds and 3rds; perfect 4ths, 5ths, octaves (the top note gets a ♯ or ♭ if needed). 6ths and 7ths use white keys and are named by number only. |
| Level 4 | 2nds–8ves, up or down. Major/minor 2nds, 3rds, 6ths, 7ths; perfect 4ths, 5ths, octaves; augmented 4th; diminished 5th. |

- Pick a size, then a quality, then a bottom note (natural); work out the top note. If the top note would need a double sharp/flat, E♯/B♯/C♭/F♭, or leaves the range, try again.
- Answer: e.g. `3rd`, `M3` (major 3rd), `P5`, `A4`.

## Key signatures (`key-signatures`)

| Level | Keys |
|---|---|
| Pre-reader, Level 1 | Not offered. |
| Level 2 | C, G, F major. Treble or bass. |
| Level 3 | C, G, D, F, B♭ major. Treble or bass. |
| Level 4 | C, G, D, A, E, F, B♭, E♭, A♭ major and their relative minors (answer both). Treble, bass or grand staff. |

## Pre-reader set (`prereader`, Pre-reader level only)

No staff, no letters for the child. A grown-up reads the direction.

| Kind | Rule |
|---|---|
| High / low | Two copies of one shape, one near the top and one near the bottom of the box (left/right side chosen by the seed). "Circle the HIGH one" or "Circle the LOW one". |
| Long / short | Two bars after a shape, one long (230) and one short (55). "Circle the LONG sound" or "SHORT sound". |
| Step / skip | A 4-stair staircase with two shapes: on the next stair (step) or one stair apart (skip), going up or down. The child circles STEP or SKIP. |

Shapes: circle, star, heart, square, triangle. "Mixed" rotates high/low, long/short, step/skip in that order.
