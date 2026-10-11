# Piano sound for the built-in player

34 short mono MP3 samples (C1–C7, re-pitched in between; `piano.json` says which sample plays which key).

- **Source:** `FluidR3Mono_GM.sf3` from MuseScore 3.6.2
  (https://raw.githubusercontent.com/musescore/MuseScore/v3.6.2/share/sound/FluidR3Mono_GM.sf3),
  preset "Grand Piano" (bank 0, program 0). SHA-256 of the file used:
  `2aacd036d7058d40a371846ef2f5dc5f130d648ab3837fe2626591ba49a71254`.
- **License: MIT.** Fluid R3 by Frank Wen (2000–2002, 2008), mono version by Michael Cowgill (2014–17).
  Full notice in `LICENSE.md` (from the same MuseScore folder, converted to UTF-8; text unchanged).
  `app/build.py` copies it, in full, into the top of `app/family-piano.html`.
- **Why not the ready-made MIDI.js files?** The popular pre-rendered "FluidR3_GM" MP3s
  (gleitz/midi-js-soundfonts) are labeled CC-BY 3.0 by that project. Making our own from the MIT original
  keeps this sound under one simple license.
- **How it was made:** `python3 app/tools/extract_piano.py FluidR3Mono_GM.sf3` (trims each sample to 2.6 s,
  fades it out, 22.05 kHz mono VBR MP3). Re-running it gives the same files.
