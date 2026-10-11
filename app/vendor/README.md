# Vendored libraries

`vexflow-bravura-4.2.2.js`: VexFlow 4.2.2 (music notation drawing), the "bravura" build from the
`vexflow@4.2.2` npm package (`build/cjs/vexflow-bravura.js`): VexFlow core plus the Bravura music font.
- VexFlow: MIT license, see `VEXFLOW-LICENSE.txt`.
- Bravura music font (Steinberg): SIL Open Font License 1.1, see `../fonts/OFL.txt`.

`app/build.py` embeds this file in `app/family-piano.html` in place of the jsDelivr `<script src>`,
so drill sheets work with no outside requests. Checked before switching: all 61 level / drill /
option combinations draw byte-identical sheets with this build and with the full `vexflow.js`
that `app/drills.html` loads on its own.

`app/drills.html` (the stand-alone drill page) still loads VexFlow from jsDelivr.
