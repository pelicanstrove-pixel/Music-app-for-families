# Third-party parts inside the app

`app/build.py` puts the full license text of each of these at the top of `app/family-piano.html`,
and Help & placement → Credits names them.

| Part | Used for | License | Files |
|---|---|---|---|
| VexFlow 4.2.2 | drawing music on drill sheets | MIT | `app/vendor/vexflow-bravura-4.2.2.js`, `app/vendor/VEXFLOW-LICENSE.txt` |
| Bravura music font (Steinberg), inside VexFlow | music symbols | SIL OFL 1.1 | (inside the VexFlow file) |
| Nunito font | on-screen text | SIL OFL 1.1 | `app/fonts/` |
| Fluid R3 piano (FluidR3Mono_GM) | built-in player sound | MIT | `app/vendor/piano/` |

Nothing here is a recording or anyone else's score. Scores the player may play are our own simplified
editions, and only when they pass the license gate described in `licenses/SOURCING.md`.
