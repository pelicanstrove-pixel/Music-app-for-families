# Fonts

`nunito-latin-wght-normal.woff2`: Nunito (variable weight 200–1000, Latin subset), from the
`@fontsource-variable/nunito` 5.3.0 npm package. SIL Open Font License 1.1, see `OFL.txt`.

`app/build.py` embeds this file inside `app/family-piano.html` (as base64), so the app never
contacts Google Fonts or any other font server. Inside the app it is named "FP Nunito" so it
cannot clash with fonts on the host page.
