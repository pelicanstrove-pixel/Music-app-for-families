#!/usr/bin/env python3
"""Turn a Mutopia Project LilyPond score into MusicXML for scores/source/.

How: copy the piece's folder, update its syntax with convert-ly, compile it with LilyPond to MIDI
(exact notes and rhythms as the typesetter entered them) while scores/tools/spelling-listener.ly logs
how every note is written (letter + sharp/flat), then build MusicXML with music21 from the MIDI and give
each note the typesetter's spelling. Repeats come out written out (as performed).

Check: the number of notes in the MusicXML (ties joined) must equal the number of notes LilyPond
played in the MIDI, or the piece is reported as FAILED and no file is written.

It does not decide anything about licenses: check the piece with licenses/SOURCING.md first.

Usage: pip install lilypond music21
       python3 scores/tools/mutopia_to_musicxml.py path/to/piece.ly out.musicxml
"""
import collections, pathlib, shutil, subprocess, sys, tempfile

from music21 import converter, midi as m21midi, pitch

HERE = pathlib.Path(__file__).resolve().parent
LISTENER = HERE / "spelling-listener.ly"
LETTERS = "CDEFGAB"


def lilypond_bin(name):
    import lilypond  # pip install lilypond
    return str(pathlib.Path(lilypond.executable()).parent / name)


def spelling_table(path):
    """MIDI number -> the spelling the typesetter used most often for it, e.g. 66 -> 'F#4'."""
    votes = collections.defaultdict(collections.Counter)
    for line in path.read_text().splitlines():
        m, step, alter, octave = line.split("\t")
        acc = {-1.0: "--", -0.5: "-", 0.0: "", 0.5: "#", 1.0: "##"}[float(alter)]
        name = LETTERS[int(step)] + acc
        votes[int(m)][(name, int(octave) + 4)] += 1
    return {m: c.most_common(1)[0][0] for m, c in votes.items()}


def midi_note_ons(path):
    mf = m21midi.MidiFile()
    mf.open(str(path)); mf.read(); mf.close()
    return sum(1 for t in mf.tracks for e in t.events
               if e.type == m21midi.ChannelVoiceMessages.NOTE_ON and e.velocity > 0)


def convert(ly_path, out_path):
    ly_path = pathlib.Path(ly_path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "piece"
        shutil.copytree(ly_path.parent, work)
        subprocess.run([lilypond_bin("convert-ly"), "-e", "-q"] + [str(p) for p in work.glob("*.ly*")],
                       capture_output=True, cwd=work)
        r = subprocess.run([lilypond_bin("lilypond"), "-s", "-dno-print-pages", "-o", "out",
                            "-dinclude-settings=" + str(LISTENER), ly_path.name],
                           capture_output=True, text=True, cwd=work, timeout=300)
        midis = sorted(work.glob("out*.mid*"))
        spell = work / "out-spelling.txt"
        if r.returncode != 0 or not midis or not spell.exists():
            return False, "LilyPond could not compile it: " + (r.stderr.strip().splitlines() or ["?"])[-1][:160]
        if len(midis) > 1:
            return False, f"{len(midis)} MIDI files (several scores in one file); convert by hand"
        table = spelling_table(spell)
        played = midi_note_ons(midis[0])
        score = converter.parse(str(midis[0]), quantizePost=True, quarterLengthDivisors=(4, 3))
        for n in score.recurse().notes:
            for p in n.pitches:
                if p.midi in table:
                    name, octave = table[p.midi]
                    q = pitch.Pitch(name); q.octave = octave
                    if q.midi == p.midi:
                        p.name, p.octave = q.name, q.octave
        for i, part in enumerate(score.parts):
            part.partName = ["Right hand", "Left hand"][i] if i < 2 else f"Part {i + 1}"
        score.metadata = None
        score.write("musicxml", fp=str(out_path))
    back = converter.parse(str(out_path)).stripTies()
    written = sum(len(n.pitches) for p in back.parts for n in p.flatten().notes)
    if written != played:
        pathlib.Path(out_path).unlink()
        return False, f"note check failed: MusicXML has {written} notes, LilyPond played {played}"
    return True, f"{written} notes, {len(back.parts)} staves, {len(back.parts[0].getElementsByClass('Measure'))} bars"


if __name__ == "__main__":
    ok, msg = convert(sys.argv[1], sys.argv[2])
    print(("OK      " if ok else "FAILED  ") + msg)
    sys.exit(0 if ok else 1)
