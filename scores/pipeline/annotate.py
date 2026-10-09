"""Annotate rules A1-A6. See scores/RULES.md.

Text placed ABOVE the staff: note names (A1), chord symbols (A4), suggested fingering (A6).
Text placed BELOW the top staff: counting (A2, lyric line 1), solfege (A3, lyric line 2).
Roman numerals (A5) go under the lowest staff.
"""
from music21 import articulations, chord, expressions, harmony, note, roman, stream

def _letter(p):
    acc = {"#": "#", "##": "x", "-": "b", "--": "bb"}.get(p.accidental.modifier if p.accidental else "", "")
    return p.step + acc


def add_note_names(score):
    """A1: write the letter name above every note, on every staff
    (chords: top to bottom, joined by '/'). Sharps are written '#', flats 'b'.
    No octave numbers."""
    count = 0
    for part in score.parts:
        for m in part.getElementsByClass(stream.Measure):
            for n in list(m.recurse().notes):
                if n.duration.isGrace:
                    continue
                ps = sorted(n.pitches, key=lambda p: -p.ps)
                te = expressions.TextExpression("/".join(_letter(p) for p in ps))
                te.placement = "above"
                te.style.fontStyle = "normal"
                m.insert(n.getOffsetInHierarchy(m), te)
                count += 1
    return [f"named {count} notes"]


def _count_label(beat_pos):
    """Name a position inside a beat: 0 -> beat number, 1/2 -> '&', 1/4 -> 'e', 3/4 -> 'a',
    1/3 -> 'la', 2/3 -> 'li' (triplets). Anything else -> '+'."""
    whole = int(beat_pos + 1e-9)
    frac = beat_pos - whole
    for f, name in ((0, None), (0.5, "&"), (0.25, "e"), (0.75, "a"), (1 / 3, "la"), (2 / 3, "li")):
        if abs(frac - f) < 1e-6:
            return whole, name
    return whole, "+"


def add_counting(score):
    """A2: write counts under every note and rest of the top staff.
    Beat unit: the time signature's bottom number (in 6/8, 9/8, 12/8 we count every eighth).
    A note on a beat gets that beat number; held beats are added with dashes ('1-2-3').
    Rests get their count in parentheses."""
    count = 0
    ts = next(iter(score.recurse().getElementsByClass("TimeSignature")), None)
    for part in score.parts[:1]:
        for m in part.getElementsByClass(stream.Measure):
            ts = m.timeSignature or ts
            if ts is None:
                continue
            unit = 4.0 / ts.denominator
            beats_in_bar = ts.numerator
            pad = m.paddingLeft
            for n in m.recurse().notesAndRests:
                if n.duration.isGrace:
                    continue
                off = n.getOffsetInHierarchy(m) + pad
                pos = off / unit
                whole, sub = _count_label(pos)
                if sub is None:
                    held_end = (off + n.quarterLength) / unit
                    beats = [str(b + 1) for b in range(whole, min(int(held_end - 1e-9) + 1, beats_in_bar))]
                    text = "-".join(beats) if beats else str(whole + 1)
                else:
                    text = sub
                if n.isRest:
                    text = f"({text})"
                n.lyrics.append(note.Lyric(text, number=len(n.lyrics) + 1, identifier="counting"))
                count += 1
    return [f"counted {count} notes and rests"]


SOLFEGE = ["do", "re", "mi", "fa", "sol", "la", "ti"]
SHARP_SYL = {"do": "di", "re": "ri", "fa": "fi", "sol": "si", "la": "li"}
FLAT_SYL = {"re": "ra", "mi": "me", "sol": "se", "la": "le", "ti": "te"}
MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]


def solfege_syllable(p, do_pitch):
    """Movable-do syllable for pitch p when 'do' is do_pitch.
    Raised notes: di ri fi si li. Lowered notes: ra me se le te.
    Any other alteration is written as the plain syllable plus #/b."""
    steps = (p.diatonicNoteNum - do_pitch.diatonicNoteNum) % 7
    base = SOLFEGE[steps]
    semis = (p.pitchClass - do_pitch.pitchClass) % 12
    alt = (semis - MAJOR_STEPS[steps] + 6) % 12 - 6
    if alt == 0:
        return base
    if alt == 1 and base in SHARP_SYL:
        return SHARP_SYL[base]
    if alt == -1 and base in FLAT_SYL:
        return FLAT_SYL[base]
    return base + ("#" * alt if alt > 0 else "b" * -alt)


def add_solfege(score, k):
    """A3: movable-do solfege under each note of the top staff. Major keys: tonic = do.
    Minor keys: tonic = la (do is the relative major tonic). Chords: top note only."""
    do = k.tonic if k.mode == "major" else k.relative.tonic
    count = 0
    for n in score.parts[0].recurse().notes:
        if n.duration.isGrace:
            continue
        top = max(n.pitches, key=lambda p: p.ps)
        n.lyrics.append(note.Lyric(solfege_syllable(top, do), number=len(n.lyrics) + 1, identifier="solfege"))
        count += 1
    return [f"key {k.tonic.name} {k.mode}: do = {do.name}; {count} syllables"]


def analyze_harmony(full_score, k):
    """Shared by A4 and A5. Chordify the full (both-hands) score. For every beat,
    collect all pitches sounding in that beat. If there are 3+ different pitch
    names, label it; skip a label that repeats the previous one.
    Roman numerals keep only the usual inversion figures (6, 64, 7, 65, 43, 42);
    any other added-note figure is dropped, leaving the plain numeral."""
    results = []
    last = None
    chordified = full_score.chordify()
    ts = next(iter(full_score.recurse().getElementsByClass("TimeSignature")), None)
    for m in chordified.getElementsByClass(stream.Measure):
        ts = m.timeSignature or ts
        unit = 4.0 / ts.denominator * (3 if ts.numerator in (6, 9, 12) and ts.denominator == 8 else 1)
        start = -m.paddingLeft
        b = 0.0
        while b < m.barDuration.quarterLength - 1e-9:
            lo, hi = b + start, b + start + unit
            ps = []
            for c in m.recurse().getElementsByClass(chord.Chord):
                o = c.getOffsetInHierarchy(m)
                if o < hi - 1e-9 and o + c.quarterLength > lo + 1e-9:
                    ps.extend(c.pitches)
            names = {p.name for p in ps}
            if len(names) >= 3:
                c = chord.Chord(sorted(ps, key=lambda p: p.ps))
                c.removeRedundantPitchNames(inPlace=True)
                cs = harmony.chordSymbolFromChord(c)
                rn = roman.romanNumeralFromChord(c, k)
                rn_text = rn.figure
                if rn_text[len(rn.romanNumeral):] not in ("", "6", "64", "7", "65", "43", "42"):
                    rn_text = rn.romanNumeral
                fig = cs.figure if cs.figure and "Cannot" not in cs.figure else None
                label = fig
                if label != last and fig:
                    results.append({"measure": m.number, "offset": max(lo, 0.0), "symbol": fig, "roman": rn_text})
                    last = label
            b += unit
    return results


def _measure(part, number):
    for m in part.getElementsByClass(stream.Measure):
        if m.number == number:
            return m
    return None


def add_chord_symbols(score, harmonies):
    """A4: chord symbols above the top staff, from analyze_harmony."""
    top = score.parts[0]
    for h in harmonies:
        m = _measure(top, h["measure"])
        if m is not None:
            m.insert(h["offset"], harmony.ChordSymbol(h["symbol"]))
    return [f"{len(harmonies)} chord symbols"]


def add_roman_numerals(score, harmonies, k):
    """A5: Roman numerals below the bottom staff, from analyze_harmony.
    The key is printed once at the start (e.g. 'C:')."""
    bottom = score.parts[-1]
    for i, h in enumerate(harmonies):
        m = _measure(bottom, h["measure"])
        if m is None:
            continue
        text = (f"{k.tonic.name}{'' if k.mode == 'major' else 'm'}: " if i == 0 else "") + h["roman"]
        te = expressions.TextExpression(text)
        te.placement = "below"
        m.insert(h["offset"], te)
    return [f"{len(harmonies)} Roman numerals in {k.tonic.name} {k.mode}"]


def add_suggested_fingering(score, hands, every_note=False):
    """A6 (off by default, always labeled SUGGESTED): five-finger-position rule.
    Walk the single notes of a staff in order. A 'position' is the longest run of
    notes that fits inside 5 letter-names (a fifth). Right hand: lowest note of the
    position = finger 1, next letter = 2 ... Left hand: lowest = 5 ... highest letter
    of the five = 1. A chord or rest ends the position. Fingers are printed only on the
    first note of each new position (or every note if every_note is true)."""
    marked = 0
    for part, hand in zip(score.parts, hands):
        runs, run = [], []
        for n in part.recurse().notesAndRests:
            if isinstance(n, harmony.Harmony):
                continue
            if isinstance(n, note.Note) and not n.duration.isGrace:
                cand = run + [n]
                nums = [x.pitch.diatonicNoteNum for x in cand]
                if max(nums) - min(nums) <= 4:
                    run = cand
                    continue
                runs.append(run)
                run = [n]
            else:
                if run:
                    runs.append(run)
                run = []
        if run:
            runs.append(run)
        for r in runs:
            low = min(x.pitch.diatonicNoteNum for x in r)
            for i, n in enumerate(r):
                if i > 0 and not every_note:
                    continue
                step = n.pitch.diatonicNoteNum - low
                finger = 1 + step if hand == "RH" else 5 - step
                n.articulations.append(articulations.Fingering(finger))
                marked += 1
        first = next((n for n in part.recurse().notes if not isinstance(n, harmony.Harmony)), None)
        if first is not None:
            m = first.getContextByClass(stream.Measure)
            te = expressions.TextExpression("Suggested fingering (rule-based, not checked)")
            te.placement = "above"
            m.insert(0, te)
    return [f"{marked} SUGGESTED finger numbers"]
