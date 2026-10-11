#!/usr/bin/env python3
"""Turn a Mutopia Project LilyPond score into MusicXML for scores/source/.

How: copy the piece's folder, update its syntax (convert-ly, plus a few repairs it does not do), and
compile it with LilyPond. scores/tools/event-performer.ly logs every note LilyPond performs: its exact
start and length (fractions, no rounding), how it is written (letter + sharp/flat), its staff, voice,
ties and grace notes, plus key and time signatures. music21 then writes MusicXML from those events.
Repeats come out written out (as performed). A file with several movements gives one MusicXML each.

Checks (a movement is refused, and no file written, if either fails):
  1. the logged notes are exactly the notes in LilyPond's own MIDI file (pitch and start, graces aside);
  2. the MusicXML read back has exactly those notes again (pitch and start), ties joined.

It does not decide anything about licenses: check the piece with licenses/SOURCING.md first.

Usage: pip install lilypond music21
       python3 scores/tools/mutopia_to_musicxml.py path/to/piece.ly out.musicxml
"""
import collections, pathlib, re, shutil, subprocess, sys, tempfile
from fractions import Fraction as F

from music21 import chord, clef, converter, duration, key, meter, midi as m21midi, note, stream

HERE = pathlib.Path(__file__).resolve().parent
PERFORMER = HERE / "event-performer.ly"
LETTERS = "CDEFGAB"

# Old syntax that current LilyPond rejects and convert-ly does not fix. Applied to the temporary copy only.
REPAIRS = [
    (re.compile(r"#:text\b"), "#:normal-text"),                                   # markup command renamed
    (re.compile(r"(?<![\\a-zA-Z])([a-g](?:isis|eses|is|es)?)(\d+\.*)('+|,+)"), r"\1\3\2"),   # f8' -> f'8
    (re.compile(r"(?<=[A-Za-z0-9',.>)~!?\[\]()])-\|"), "-!"),                             # old staccatissimo shorthand
]


def repair(folder):
    for f in list(folder.glob("*.ly")) + list(folder.glob("*.ily")) + list(folder.glob("*.lyi")):
        text = f.read_text(encoding="utf-8", errors="replace")
        new = text
        for pat, rep in REPAIRS:
            new = pat.sub(rep, new)
        if new != text:
            f.write_text(new, encoding="utf-8")


def lilypond_bin(name):
    import lilypond  # pip install lilypond
    return str(pathlib.Path(lilypond.executable()).parent / name)


def read_events(path):
    """Split the log into movements: {"notes": [...], "ties": set, "keys": [...]} each."""
    movements = []
    for line in path.read_text().splitlines():
        f = line.split("\t")
        if f[0] == "S":
            movements.append({"notes": [], "ties": set(), "keys": []})
        elif f[0] == "N":
            alter = float(f[8])
            movements[-1]["notes"].append({
                "staff": f[1], "voice": f[2], "on": F(f[3]), "dur": F(f[4]), "grace": f[5] == "1",
                "midi": int(f[6]), "name": LETTERS[int(f[7])] + {-1.0: "--", -0.5: "-", 0.0: "", 0.5: "#", 1.0: "##"}[alter],
                "octave": int(f[9]) + 4, "ts": f[10], "mpos": F(f[11]), "clef": f[12] if len(f) > 12 else "?"})
        elif f[0] == "T":
            movements[-1]["ties"].add((f[1], F(f[2])))
        elif f[0] == "K":
            movements[-1]["keys"].append((F(f[1]), int(f[2])))
    return [m for m in movements if m["notes"]]


def midi_onsets(path):
    """MIDI note-ons as a Counter of (tick, pitch), plus ticks per whole note."""
    mf = m21midi.MidiFile()
    mf.open(str(path)); mf.read(); mf.close()
    on = collections.Counter()
    for t in mf.tracks:
        tick = 0
        for e in t.events:
            if e.isDeltaTime():
                tick += e.time
            elif e.type == m21midi.ChannelVoiceMessages.NOTE_ON and e.velocity > 0:
                on[(tick, e.pitch)] += 1
    return on, mf.ticksPerQuarterNote * 4


def take_onset(ons, tick, pitch):
    """Use up the MIDI note-on for this note (LilyPond rounds tuplets to whole ticks: allow one tick)."""
    for t in (tick, tick - 1, tick + 1):
        if ons[(t, pitch)] > 0:
            ons[(t, pitch)] -= 1
            return True
    return False


def prepare(mv, ons, tpw):
    """Merge doubled notes, join ties the way LilyPond plays them, order staves top to bottom.
    A logged note LilyPond did not strike (no MIDI note-on) is the continuation of a tie: it is joined to the
    same pitch on the same staff that ends exactly where it starts. Returns (staves, notes LilyPond struck
    that no logged note explains, grace count)."""
    ons = collections.Counter(ons)
    notes = sorted(mv["notes"], key=lambda n: (n["on"], n["staff"], n["midi"]))
    # Grace notes at the very start make LilyPond's MIDI begin earlier: find that shift from the first notes.
    diffs = collections.Counter()
    for n in [n for n in notes if not n["grace"]][:24]:
        for (t, p) in ons:
            if p == n["midi"] and abs(t - round(n["on"] * tpw)) <= tpw:
                diffs[t - round(n["on"] * tpw)] += 1
    shift = diffs.most_common(1)[0][0] if diffs else 0
    last = {}      # (staff, midi) -> the note it would continue
    out, unexplained = [], 0
    for n in notes:
        if n["grace"]:
            out.append(n); continue
        k = (n["staff"], n["midi"])
        prev = last.get(k)
        if prev is not None and prev["on"] == n["on"]:
            prev["dur"] = max(prev["dur"], n["dur"]); continue      # same note written in two voices
        if take_onset(ons, round(n["on"] * tpw) + shift, n["midi"]):
            last[k] = n; out.append(n); continue
        if prev is not None and prev["on"] + prev["dur"] == n["on"]:
            prev["dur"] += n["dur"]; continue                      # held over by a tie
        unexplained += 1; out.append(n)
    graces = sum(1 for n in out if n["grace"])
    staves = collections.defaultdict(list)
    for n in out:
        staves[n["staff"]].append(n)
    for notes_ in staves.values():   # a held note stops where the same key is struck again (as in the MIDI)
        nxt = {}
        for n in sorted((n for n in notes_ if not n["grace"]), key=lambda n: -n["on"]):
            later = nxt.get(n["midi"])
            if later is not None and n["on"] + n["dur"] > later:
                n["dur"] = later - n["on"]
            nxt[n["midi"]] = n["on"]
    order = sorted(staves, key=lambda s: -sum(n["midi"] for n in staves[s]) / len(staves[s]))
    left = sum(ons.values())   # MIDI note-ons not matched to any logged note (grace notes are played early)
    return [staves[s] for s in order], unexplained, left - graces


def build_score(staves, mv):
    first = min((n for s in staves for n in s if not n["grace"]), key=lambda n: n["on"])
    pad = F(0)                                                                # pickup bar
    if first["on"] == 0 and first["mpos"] != 0:
        num, den = first["ts"].split("/")
        pad = first["mpos"] if first["mpos"] > 0 else F(int(num), int(den)) + first["mpos"]
    sc = stream.Score()
    for i, notes in enumerate(staves):
        part = stream.Part()
        part.partName = ["Right hand", "Left hand"][i] if i < 2 else f"Part {i + 1}"
        avg = sum(n["midi"] for n in notes) / len(notes)
        def clef_for(glyph):
            if glyph.startswith("clefs.F"): return clef.BassClef()
            if glyph.startswith("clefs.G"): return clef.TrebleClef()
            return clef.TrebleClef() if avg >= 57 else clef.BassClef()
        seen_clef = None
        for n in sorted((n for n in notes if not n["grace"]), key=lambda n: n["on"]):   # LilyPond's own clefs and clef changes
            if n["clef"] != seen_clef:
                part.insert(float((n["on"] + pad) * 4) if seen_clef is not None else 0.0, clef_for(n["clef"])); seen_clef = n["clef"]
        seen_ts = None
        for n in sorted(notes, key=lambda n: n["on"]):
            if not n["grace"] and n["ts"] != seen_ts:
                num, den = n["ts"].split("/")
                at = 0.0 if seen_ts is None else float((n["on"] + pad) * 4)
                part.insert(at, meter.TimeSignature(f"{num}/{den}")); seen_ts = n["ts"]
        last_key = None
        for on, k in sorted(mv["keys"]):
            if k != last_key:
                part.insert(float((on + pad) * 4), key.KeySignature(k)); last_key = k
        groups = collections.defaultdict(list)
        for n in notes:   # notes that start and end together make one chord, whichever voice wrote them
            groups[(n["on"], n["dur"], n["grace"])].append(n)
        for (on, dur, grace), ns in sorted(groups.items(), key=lambda kv: (kv[0][0], not kv[0][2])):
            pitches = [x["name"] + str(x["octave"]) for x in ns]
            el = note.Note(pitches[0]) if len(pitches) == 1 else chord.Chord(pitches)
            if grace:
                el = el.getGrace()
            else:
                el.duration = duration.Duration(float(dur * 4))
            part.insert(float((on + pad) * 4), el)
        if part.flatten().notes.stream().getOverlaps():
            part.makeVoices(inPlace=True, fillGaps=False)      # two voices on one staff with different rhythms
        sc.insert(0, part)
    return sc, pad


def check_against(events_counter, staves, pad, xml_path, what):
    back = converter.parse(str(xml_path))
    got = collections.Counter()
    graces = 0
    for p in back.parts:
        open_ties = {}   # midi -> end offset of a note whose tie continues (joined here, also across voices and bars)
        for n in sorted(p.flatten().notes, key=lambda n: n.getOffsetInHierarchy(p)):
            if n.duration.isGrace:
                graces += len(n.pitches); continue
            on = F(n.getOffsetInHierarchy(p)).limit_denominator(3840)
            end = on + F(n.quarterLength).limit_denominator(3840)
            for sub in (n.notes if n.isChord else [n]):
                pt, tie = sub.pitch, (sub.tie or n.tie)
                kind = tie.type if tie else None
                if kind in ("stop", "continue") and open_ties.get(pt.midi) == on:
                    if kind == "continue": open_ties[pt.midi] = end
                    else: open_ties.pop(pt.midi, None)
                    continue
                got[(on / 4, pt.midi)] += 1
                if kind in ("start", "continue"): open_ties[pt.midi] = end
    want = collections.Counter((n["on"], n["midi"]) for s in staves for n in s if not n["grace"])
    # compare positions relative to the first note, so a pickup bar may be written either way
    g0 = min(a for a, _ in got) if got else 0
    w0 = min(a for a, _ in want) if want else 0
    got = collections.Counter({(a - g0, b): c for (a, b), c in got.items()})
    want = collections.Counter({(a - w0, b): c for (a, b), c in want.items()})
    want_graces = sum(1 for s in staves for n in s if n["grace"])
    if got != want or graces != want_graces:
        diff = list((want - got).items())[:3] + list((got - want).items())[:3]
        return f"{what}: MusicXML differs from LilyPond's notes, e.g. {[(str(a), b) for (a, b), _ in diff]}"
    return None


def convert(ly_path, out_path):
    """Returns (ok, message, [written files])."""
    ly_path = pathlib.Path(ly_path).resolve()
    out_path = pathlib.Path(out_path)
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "piece"
        shutil.copytree(ly_path.parent, work, symlinks=True, ignore_dangling_symlinks=True)
        subprocess.run([lilypond_bin("convert-ly"), "-e", "-q"] + [str(p) for p in work.glob("*.ly*")],
                       capture_output=True, cwd=work)
        repair(work)
        r = subprocess.run([lilypond_bin("lilypond"), "-s", "-dno-print-pages", "-o", "out",
                            "-dinclude-settings=" + str(PERFORMER), ly_path.name],
                           capture_output=True, text=True, cwd=work, timeout=600)
        log = work / "out-events.txt"
        midis = [work / "out.midi"] + sorted(work.glob("out-*.midi"), key=lambda p: int(p.stem.split("-")[-1]))
        midis = [m for m in midis if m.exists()]
        if not log.exists() or not midis:
            err = [l for l in r.stderr.splitlines() if "error" in l.lower()] or r.stderr.strip().splitlines() or ["?"]
            return False, "LilyPond could not compile it: " + err[0][:160], []
        movements = read_events(log)
        if len(movements) != len(midis):
            return False, f"{len(movements)} scores logged but {len(midis)} MIDI files", []
        written, notes_total, msgs = [], 0, []
        for i, (mv, mid) in enumerate(zip(movements, midis)):
            what = f"movement {i + 1}" if len(movements) > 1 else "piece"
            ons, tpw = midi_onsets(mid)
            staves, extra, missing = prepare(mv, ons, tpw)
            if extra or missing > 0:
                return False, f"{what}: logged notes differ from LilyPond's MIDI ({extra} extra, {missing} missing)", written
            sc, pad = build_score(staves, mv)
            target = out_path if len(movements) == 1 else out_path.with_name(f"{out_path.stem}-{i + 1}{out_path.suffix}")
            sc.write("musicxml", fp=str(target))
            bad = check_against(None, staves, pad, target, what)
            if bad:
                target.unlink()
                return False, bad, written
            written.append(target)
            n_notes = sum(1 for s in staves for n in s)
            notes_total += n_notes
            msgs.append(f"{n_notes} notes, {len(staves)} staves, {len(converter.parse(str(target)).parts[0].getElementsByClass('Measure'))} bars")
    return True, "; ".join(msgs), written


if __name__ == "__main__":
    ok, msg, files = convert(sys.argv[1], sys.argv[2])
    print(("OK      " if ok else "FAILED  ") + msg + ("" if len(files) < 2 else " -> " + ", ".join(f.name for f in files)))
    sys.exit(0 if ok else 1)
