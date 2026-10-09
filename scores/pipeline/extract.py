"""Extract rules E1-E4. See scores/RULES.md.

Each function takes a music21 Score and returns a new Score.
Staff convention: the first staff is the right hand (upper),
the last staff is the left hand (lower).
"""
from music21 import chord, layout, note, stream


def _keep_parts(score, keep):
    """Return a copy of the score with only the given part indexes."""
    new = stream.Score()
    new.metadata = score.metadata
    for i, p in enumerate(score.parts):
        if i in keep:
            new.insert(0, p)
    return new


def extract_measure_range(score, first, last):
    """E1: keep measures first..last (inclusive, by printed measure number)."""
    return score.measures(first, last)


def extract_right_hand(score):
    """E2: keep only the first (upper) staff."""
    return _keep_parts(score, {0})


def extract_left_hand(score):
    """E3: keep only the last (lower) staff."""
    return _keep_parts(score, {len(score.parts) - 1})


def extract_top_melody(score):
    """E4: upper staff only; in each measure keep only voice 1;
    in every chord keep only the highest note."""
    s = _keep_parts(score, {0})
    part = s.parts[0]
    for m in part.getElementsByClass(stream.Measure):
        voices = list(m.voices)
        for v in voices[1:]:
            m.remove(v)
        if voices:
            m.flattenUnnecessaryVoices(force=True)
    for c in list(part.recurse().getElementsByClass(chord.Chord)):
        top = max(c.pitches, key=lambda p: p.ps)
        n = note.Note(top, duration=c.duration)
        n.tie = c.tie
        n.expressions = list(c.expressions)
        n.articulations = list(c.articulations)
        c.activeSite.replace(c, n)
    return s


def hands_of(score, extract_mode):
    """Which hand each output staff belongs to (used by fingering and range rules)."""
    n = len(score.parts)
    if extract_mode in ("right_hand", "melody"):
        return ["RH"]
    if extract_mode == "left_hand":
        return ["LH"]
    return ["RH"] + ["LH"] * (n - 1)


def drop_staff_groups(score):
    """Remove brace/bracket groups that point at removed staves."""
    for sg in list(score.getElementsByClass(layout.StaffGroup)):
        score.remove(sg)
    if len(score.parts) > 1:
        score.insert(0, layout.StaffGroup(list(score.parts), symbol="brace"))
    return score
