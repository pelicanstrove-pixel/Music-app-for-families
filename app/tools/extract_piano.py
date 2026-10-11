#!/usr/bin/env python3
"""Make the app's piano sounds from FluidR3Mono_GM.sf3 (MIT license).

Source: MuseScore 3.6.2, share/sound/FluidR3Mono_GM.sf3
  https://raw.githubusercontent.com/musescore/MuseScore/v3.6.2/share/sound/FluidR3Mono_GM.sf3
License: MIT (Frank Wen; mono version Michael Cowgill), see app/vendor/piano/LICENSE.md.

Reads General MIDI program 0 (Acoustic Grand Piano, bank 0), takes the sample used at a medium-loud
velocity for each key range, trims it, fades it out and saves small mono MP3s plus piano.json
(which file to use for which key and how to re-pitch it).

Usage: pip install soundfile numpy
       python3 app/tools/extract_piano.py path/to/FluidR3Mono_GM.sf3
"""
import hashlib, io, json, pathlib, struct, sys

import numpy as np
import soundfile as sf

OUT = pathlib.Path(__file__).resolve().parent.parent / "vendor" / "piano"
KEEP_SECONDS = 2.6      # long enough for practice tempos; the app fades longer notes
FADE_SECONDS = 0.4
RATE = 22050
VELOCITY = 90           # pick the layer a medium-loud key press would use
LOW, HIGH = 24, 96      # C1..C7: covers beginner music; the top octave is stretch-tuned and rarely used


def chunks(data, start, end):
    i = start
    while i < end:
        cid, size = data[i:i + 4].decode("latin-1"), struct.unpack("<I", data[i + 4:i + 8])[0]
        yield cid, i + 8, size
        i += 8 + size + (size & 1)


def records(buf, fmt):
    n = struct.calcsize(fmt)
    return [struct.unpack(fmt, buf[i:i + n]) for i in range(0, len(buf) - n + 1, n)]


def parse(path):
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"sfbk", "not a SoundFont"
    lists = {}
    for cid, off, size in chunks(data, 12, len(data)):
        if cid == "LIST":
            lists[data[off:off + 4].decode()] = {c: data[o:o + s] for c, o, s in chunks(data, off + 4, off + size)}
    p = lists["pdta"]
    return data, {
        "smpl": lists["sdta"]["smpl"],
        "phdr": records(p["phdr"], "<20sHHHIII"), "pbag": records(p["pbag"], "<HH"), "pgen": records(p["pgen"], "<HH"),
        "inst": records(p["inst"], "<20sH"), "ibag": records(p["ibag"], "<HH"), "igen": records(p["igen"], "<HH"),
        "shdr": records(p["shdr"], "<20sIIIIIBbHH"),
    }


def zones(bags, gens, first, last):
    out = []
    for b in range(first, last):
        g0, g1 = bags[b][0], bags[b + 1][0]
        z = {}
        for op, amount in gens[g0:g1]:
            if op in (43, 44):  # keyRange, velRange: lo/hi bytes
                z[op] = (amount & 0xFF, amount >> 8)
            else:
                z[op] = struct.unpack("<h", struct.pack("<H", amount))[0]
        out.append(z)
    return out


def main(src):
    src = pathlib.Path(src)
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    data, sfd = parse(src)
    preset = next(i for i, r in enumerate(sfd["phdr"][:-1]) if r[1] == 0 and r[2] == 0)  # program 0, bank 0
    name = sfd["phdr"][preset][0].split(b"\0")[0].decode()
    pzones = zones(sfd["pbag"], sfd["pgen"], sfd["phdr"][preset][3], sfd["phdr"][preset + 1][3])
    inst_ids = sorted({z[41] for z in pzones if 41 in z})
    picks = {}
    for ii in inst_ids:
        for z in zones(sfd["ibag"], sfd["igen"], sfd["inst"][ii][1], sfd["inst"][ii + 1][1]):
            if 53 not in z:
                continue  # global zone
            lo, hi = z.get(43, (0, 127))
            vlo, vhi = z.get(44, (0, 127))
            if not (vlo <= VELOCITY <= vhi):
                continue
            for key in range(max(lo, LOW), min(hi, HIGH) + 1):
                picks.setdefault(key, z)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.mp3"):
        old.unlink()
    samples, keymap = {}, {}
    for key in range(LOW, HIGH + 1):
        z = picks[key]
        sid = z[53]
        sname, start, end, _ls, _le, rate, root, corr, _link, stype = sfd["shdr"][sid]
        if sid not in samples:
            raw = sfd["smpl"][start:end] if stype & 0x10 else None  # SF3: Ogg Vorbis bytes
            if raw is None:
                pcm = np.frombuffer(sfd["smpl"][start * 2:end * 2], dtype="<i2").astype(np.float32) / 32768
            else:
                pcm, rate = sf.read(io.BytesIO(raw), dtype="float32")
                if pcm.ndim > 1:
                    pcm = pcm.mean(axis=1)
            # resample to RATE (linear is fine for short piano notes at this quality)
            n_out = int(len(pcm) * RATE / rate)
            pcm = np.interp(np.linspace(0, len(pcm) - 1, n_out), np.arange(len(pcm)), pcm)
            pcm = pcm[: int(KEEP_SECONDS * RATE)]
            fade = int(FADE_SECONDS * RATE)
            if len(pcm) > fade:
                pcm[-fade:] *= np.linspace(1, 0, fade)
            peak = float(np.max(np.abs(pcm))) or 1.0
            pcm = pcm / peak * 0.9
            fname = f"s{len(samples):02d}.mp3"
            sf.write(OUT / fname, pcm.astype(np.float32), RATE, format="MP3", bitrate_mode="VARIABLE", compression_level=0.5)
            root_key = z.get(58, root)  # overridingRootKey wins over the sample header
            cents = z.get(51, 0) * 100 + z.get(52, 0) + corr
            samples[sid] = {"file": fname, "root": root_key, "cents": cents, "name": sname.split(b"\0")[0].decode()}
        keymap[key] = sid
    info = {
        "source": "FluidR3Mono_GM.sf3 (MuseScore 3.6.2), preset: " + name,
        "source_sha256": digest, "license": "MIT, see LICENSE.md", "rate": RATE,
        "samples": [{"file": s["file"], "root": s["root"], "cents": s["cents"]} for s in samples.values()],
        "keys": {str(k): list(samples).index(sid) for k, sid in keymap.items()},
    }
    (OUT / "piano.json").write_text(json.dumps(info, indent=1) + "\n")
    total = sum(f.stat().st_size for f in OUT.glob("*.mp3"))
    print(f"preset '{name}', {len(samples)} samples for keys {LOW}-{HIGH}, {total:,} bytes of MP3")
    print("source sha256:", digest)


if __name__ == "__main__":
    main(sys.argv[1])
