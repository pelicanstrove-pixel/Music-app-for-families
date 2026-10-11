# Built-in MIDI player: options (2026-10-11)

Question from the owner: can Family Piano play music itself (a "MIDI player"), and what are the options?
Short answer: **yes**. The best fit is a small player written for this app on the browser's own sound
engine (Web Audio). It plays note data made at build time from our own simplified scores, and it can
optionally send the notes to the family's digital piano over USB (Web MIDI).

## Decisions and what is built (2026-10-11)

- **Copyright:** "don't get us sued". The build only lets the player play a piece when the composition is
  public domain, the edition is CC0 / public domain / plain CC-BY (with credit), `derivatives_allowed` is
  `yes`, and our simplified score is approved and unchanged. Share-alike, NC and ND are refused. See
  `licenses/SOURCING.md`. No recordings are used.
- **Sound:** MIT piano samples (option B), made from MuseScore's MIT-licensed FluidR3Mono, not the CC-BY
  MIDI.js renders (see `app/vendor/piano/README.md`). Adds about 0.5 MB to the app.
- **Where:** everywhere, with a switch (Family → Sound): Pieces (full player), drill sheets (a Play button
  on note-naming, interval and rhythm items, never printed), kid modes (a short chime when a step or tile
  is marked done). Ear-training items get sound once educators add notes to exercises.
- **Digital piano:** Web MIDI output as a setting (Family → Sound → Play through), and MIDI input for wait-for-me.
- **Keyboard size** (Family → Your keyboard and listening): 1–7 octaves or 88 keys, plus the keyboard's octave
  buttons. Pieces are moved by octaves to fit (or single notes folded in when a piece is wider than the keyboard);
  the on-screen keys and the game show only the family's keys. Optional: count the right note in any octave.
- **Listening and checking:** the app hears the child through a digital piano (MIDI), the **microphone** (chords too: on each
  attack the app checks the notes it is waiting for against the new sound, by harmonic matching after Klapuri;
  nothing is recorded or sent) or the on-screen keys. *Check my
  playing* grades every note in time (green right, red wrong, grey missed) while the app plays the other hand;
  *Wait for me* marks right-first-time notes and gives a summary.
- **Compose** (side menu → Compose; "Make a song" in Beginner reader mode): records the digital piano (with exact
  note lengths from key releases and loudness), the on-screen keys, or the microphone (single notes reliable; chords
  are a best guess, since nothing is expected). Count-in and metronome at a chosen tempo; plays back *as played*
  (the child's own timing) or *as written*. The app snaps the performance to the beat (quarter, eighth or sixteenth
  notes), splits right hand / left hand at middle C, writes rests and ties across barlines, spells accidentals for
  the chosen key, and draws a grand staff with VexFlow. Print it (black and white), or download MusicXML (for
  MuseScore and other programs) and MIDI. Songs are saved per child and included in backups.
- **Game** (Pieces → Game): falling notes onto a keyboard (rhythm-game style) or the sheet music scrolling past a
  line; *Play in time* (perfect/good/miss timing, combo, score, 1–3 stars) or *Wait for me*; hands, speed, note
  names. Best score and stars are saved per child and piece. Works for every piece the license gate lets the
  player play, now and in future.
- Player options built: Play / Pause / Stop, progress, speed 40–120%, hands (both / right / left),
  bars from–to, loop, count-in, metronome, volume.
- Also built: the score is shown with the sounding notes highlighted (tap a note to start there), and
  **wait for me** mode: the next note or chord is marked and the app waits until the child plays it on a digital
  piano (Web MIDI input: Chrome, Edge, Firefox) or the on-screen keys; with one hand chosen, the other hand can play along.

The research below is kept for reference. Correction to the table: the FluidR3 GM files from MIDI.js are
labeled CC-BY 3.0 by that project; the original Fluid R3 and MuseScore's FluidR3Mono are MIT.

## What it would play

| Source | Where the notes come from | Notes |
|---|---|---|
| **Pieces** (simplified scores) | `scores/derived/<asset_id>/*.musicxml`, already made by the score pipeline. `app/build.py` would turn each **approved** score into a small list of notes (pitch, start, length, hand) with music21, which the pipeline already uses | Only scores whose `meta.json` is approved and whose `derivatives_allowed` is `yes` or `share-alike` |
| **Drill sheets** | The drill maker already knows every item's notes (intervals, rhythms, note names) | e.g. a "Listen" button on the answer key, or for ear-training practice |
| **Ear training / week items** | Exercise-bank items could carry notes once educators write them | Educator-written only (no generated teaching content) |

## Ways to make the sound

| Option | Size added | Sound | Outside requests | License | Verdict |
|---|---|---|---|---|---|
| **A. Own Web Audio synth** (oscillators shaped like a soft piano) | ~10–15 KB of code | Clean, "electronic piano"; fine for melodies and intervals | None | ours | **Recommended to start** |
| **B. Own player + embedded piano samples** (FluidR3 GM piano, one sample every 3 semitones, re-pitched in between) | ~0.3–0.6 MB (estimate) | Real piano | None (samples inside the file) | FluidR3 GM: MIT | **Recommended upgrade** if A sounds too thin |
| **C. Web MIDI output** (send notes to a digital piano plugged in by USB / Bluetooth MIDI) | ~2 KB on top of A/B | The family's own piano | None | browser API | **Recommended as an option**. Works in Chrome, Edge, Firefox (asks permission) and Android; **not** in Safari, so not on iPhone/iPad |
| html-midi-player (Magenta.js) | large (Magenta + TensorFlow parts) | Good | Loads sounds from Google's servers by default | BSD-2 / Apache-2.0 | Not recommended: size and Google requests |
| soundfont-player / smplr | 100 KB–1 MB code | Good | Load samples from GitHub Pages by default (could be self-hosted) | MIT; samples vary (MusyngKite is CC-BY-SA) | Not needed if we do B ourselves |
| Tone.js + @tonejs/midi | several hundred KB | Good, many effects | None by itself | MIT | More than we need |
| spessasynth_lib / js-synthesizer (SoundFont engines) | 0.3 MB+ code **plus** a multi-MB SoundFont | Best, all General MIDI instruments | None if the SoundFont is embedded | Apache-2.0 / BSD-3 | Only if we ever need many instruments |
| WebAudioFont | large | Good | Optional | **GPL-3** | Avoid: GPL would apply to the whole app |

All sound in browsers must start from a tap or click (autoplay rule), which suits a Play button.
On iPhone/iPad, Safari plays Web Audio **silently when the ring/silent switch is on**. The help FAQ
should say so.

## Player options (features), in suggested build order

1. **Basic:** Play / Pause / Stop, a progress bar, volume.
2. **Practice:** tempo slider (e.g. 40–120% of the marked tempo), **hands**: right / left / both (the
   simplified scores keep hands as separate parts), **loop** a few measures (A–B), **count-in** clicks
   and an optional **metronome**.
3. **Follow along:** highlight the current note on the score. Verovio (already in the pipeline) can
   output the score as SVG plus a "timemap" of when each note sounds, so this can be made at build time.
4. **Digital piano (Web MIDI):** pick an output to play through the family's piano. With MIDI **input**,
   a "wait for me" mode can pause until the child plays the right key. Chrome, Edge and Firefox only.
5. **Kid modes:** one big Play button for Beginner reader ("Songs"); in Toddler mode, tapping a picture
   tile could play a short sound (only from educator-chosen notes).

## Owner decisions needed

1. **Policy.** `licenses/SOURCING.md` says the app *links to scores and audio and never copies them into
   the app*. Playback needs the notes of our own simplified scores inside the app (no recordings).
   Is that allowed for approved scores whose license allows derivatives? (With CC-BY / CC-BY-SA sources
   the credit line must show next to the player.)
2. **Sound.** Start with the built-in synth (A), go straight to embedded piano samples (B, +~0.5 MB),
   or both with a switch?
3. **Where.** Pieces only, or also drill answer keys / ear training, and kid modes?
4. **Digital piano.** Include Web MIDI output (C)? Input / "wait for me" mode?

## Suggested first step

Build A + basic and practice options (1–2) for Pieces, with Web MIDI output as a setting. Notes would
be made by `app/build.py` from approved derived scores only. Today the only derived score is the
pipeline test fixture, so it could be used to test the player but would not be shown to families.
