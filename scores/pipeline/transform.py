"""Transform rules T1-T5. See scores/RULES.md.

Each function changes the score in place and returns a list of
plain-English notes about what it did (for meta.json).
"""
from music21 import chord, duration, expressions, interval, key, note, pitch, spanner, stream


def remove_ornaments(score):
    """T1: delete grace notes; delete trill, mordent, turn and tremolo marks
    (the main note stays); delete trill wavy lines."""
    removed_marks = 0
    for n in score.recurse().notes:
        keep = [e for e in n.expressions
                if not isinstance(e, (expressions.Ornament, expressions.Tremolo))]
        removed_marks += len(n.expressions) - len(keep)
        n.expressions = keep
    graces = [n for n in score.recurse().notes if n.duration.isGrace]
    for g in graces:
        for sp in g.getSpannerSites():
            if len(sp.getSpannedElements()) <= 2:
                _remove_spanner(score, sp)
            else:
                sp.spannerStorage.remove(g)
        g.activeSite.remove(g)
    lines = [sp for sp in score.recurse().getElementsByClass(spanner.Spanner)
             if isinstance(sp, (expressions.TrillExtension, expressions.TremoloSpanner))]
    for sp in lines:
        _remove_spanner(score, sp)
    return [f"removed {len(graces)} grace notes, {removed_marks} ornament marks, {len(lines)} trill lines"]


def _remove_spanner(score, sp):
    site = sp.activeSite
    if site is not None:
        site.remove(sp)
    else:
        score.remove(sp, recurse=True)


def _staff_voices_outer(part, upper):
    """Keep the outer voice in each measure: highest for the upper staff,
    lowest for lower staves."""
    dropped = 0
    for m in part.getElementsByClass(stream.Measure):
        voices = list(m.voices)
        if len(voices) < 2:
            continue

        def avg(v):
            ps = [p.ps for n in v.notes for p in n.pitches]
            return sum(ps) / len(ps) if ps else (-1 if upper else 999)

        keep = max(voices, key=avg) if upper else min(voices, key=avg)
        for v in voices:
            if v is not keep:
                m.remove(v)
                dropped += 1
        m.flattenUnnecessaryVoices(force=True)
    return dropped


def drop_inner_voices(score):
    """T2: in each staff keep only the outer voice, and in chords of 3+ notes
    keep only the top and bottom notes."""
    dropped_voices = 0
    thinned = 0
    for i, part in enumerate(score.parts):
        dropped_voices += _staff_voices_outer(part, upper=(i == 0))
        for c in part.recurse().getElementsByClass(chord.Chord):
            if len(c.pitches) >= 3:
                ps = sorted(c.pitches, key=lambda p: p.ps)
                for p in ps[1:-1]:
                    c.remove(p)
                thinned += 1
    return [f"dropped {dropped_voices} extra voices, thinned {thinned} chords to top+bottom notes"]


def simplify_dotted_rhythms(score):
    """T3 (off by default): a dotted note followed by a note one third of its
    length (e.g. dotted quarter + eighth) becomes two equal notes (quarter + quarter).
    Only inside one measure, only for notes (not rests), only if neither is tied."""
    changed = 0
    containers = [s for s in score.recurse(streamsOnly=True)
                  if isinstance(s, (stream.Measure, stream.Voice))]
    for s in containers:
        items = list(s.getElementsByClass(note.GeneralNote))
        for a, b in zip(items, items[1:]):
            if a.isRest or b.isRest or a.duration.isGrace or b.duration.isGrace:
                continue
            if a.duration.dots != 1 or a.duration.tuplets or b.duration.tuplets:
                continue
            if a.tie is not None or b.tie is not None:
                continue
            qa, qb = a.quarterLength, b.quarterLength
            if abs(qb * 3 - qa) > 1e-9 or abs(s.elementOffset(b) - (s.elementOffset(a) + qa)) > 1e-9:
                continue
            base = qa * 2 / 3
            a.duration = duration.Duration(base)
            b.duration = duration.Duration(base)
            s.setElementOffset(b, s.elementOffset(a) + base)
            changed += 1
    return [f"evened {changed} dotted-rhythm pairs"]


def detect_key(score):
    """Key used by T4, A3 and A5: music21's Krumhansl-Schmuckler key analysis."""
    return score.analyze("key")


def transpose_to_key(score, target_tonic):
    """T4: move the whole piece so its tonic becomes target_tonic (same mode).
    Takes the shorter way (up or down); a tritone goes down."""
    src = detect_key(score)
    start = pitch.Pitch(src.tonic.name + "4")
    end_up = pitch.Pitch(pitch.Pitch(target_tonic).name + "4")
    if end_up.ps < start.ps:
        end_up.octave += 1
    end_down = pitch.Pitch(end_up.nameWithOctave)
    end_down.octave -= 1
    up = interval.Interval(start, end_up)
    down = interval.Interval(start, end_down)
    if up.semitones % 12 == 0:
        return [f"already in {target_tonic}; not moved"]
    iv = up if up.semitones < abs(down.semitones) else down
    score.transpose(iv, inPlace=True)
    for ks in score.recurse().getElementsByClass(key.KeySignature):
        if ks.sharps > 6 or ks.sharps < -6:
            ks.sharps = ks.sharps - 12 if ks.sharps > 0 else ks.sharps + 12
    return [f"{src.tonic.name} {src.mode} -> {pitch.Pitch(target_tonic).name} {src.mode} ({iv.directedName}, {iv.semitones:+d} semitones)"]


def limit_range(score, max_semitones, phrase_measures=4):
    """T5: split each staff into phrases of phrase_measures measures. The window
    is [lowest note of the first phrase, + max_semitones]. A phrase that sticks
    out is moved by whole octaves (smallest move first, down before up) until it
    fits. A phrase too wide to ever fit is left alone and reported."""
    notes_out = []
    for pi, part in enumerate(score.parts):
        measures = list(part.getElementsByClass(stream.Measure))
        phrases = [measures[i:i + phrase_measures] for i in range(0, len(measures), phrase_measures)]
        window_low = None
        for ph in phrases:
            ps = [p for m in ph for n in m.recurse().notes for p in n.pitches if not n.duration.isGrace]
            if not ps:
                continue
            lo, hi = min(p.ps for p in ps), max(p.ps for p in ps)
            if window_low is None:
                window_low = lo
            window_high = window_low + max_semitones
            label = f"staff {pi + 1}, measures {ph[0].number}-{ph[-1].number}"
            if hi - lo > max_semitones:
                notes_out.append(f"{label}: spans {int(hi - lo)} semitones, wider than {max_semitones}; left unchanged")
                continue
            if lo >= window_low and hi <= window_high:
                continue
            for k in (-1, 1, -2, 2, -3, 3):
                if lo + 12 * k >= window_low and hi + 12 * k <= window_high:
                    for p in ps:
                        p.octave += k
                    notes_out.append(f"{label}: moved {abs(k)} octave(s) {'down' if k < 0 else 'up'}")
                    break
            else:
                notes_out.append(f"{label}: could not fit in window by octave moves; left unchanged")
    return notes_out or ["all phrases already inside the range"]
