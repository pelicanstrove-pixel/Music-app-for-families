# Built-in MIDI player: options (2026-10-11)

Question from the owner: can Family Piano play music itself (a "MIDI player"), and what are the options?
Short answer: **yes**. The best fit is a small player written for this app on the browser's own sound
engine (Web Audio). It plays note data made at build time from our own simplified scores, and it can
optionally send the notes to the family's digital piano over USB (Web MIDI). Nothing below is built yet.

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
