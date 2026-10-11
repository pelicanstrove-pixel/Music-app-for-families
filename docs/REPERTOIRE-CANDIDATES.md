# Pieces to ship: research (2026-10-11)

**Bottom line.** All 76 license-cleared candidates (78 files: Clementi's sonatina gives one per movement) are
converted into draft MusicXML, ready for a person to check and approve. They come from the **Mutopia Project**, whose
volunteer typesetters placed these editions in the **public domain**, made from old public-domain editions
(Bach-Gesellschaft, Peters, Litolff and similar). The compositions are all public domain in the US: every composer died
before 1926 and every piece was published long before 1929. Nothing here is shipped yet: each piece still needs the
human steps below.

Files: drafts in `scores/candidates/` (compressed MusicXML, `.mxl`), one row per file with the license evidence in
`licenses/candidates.csv`, converter in `scores/tools/mutopia_to_musicxml.py` (with `scores/tools/event-performer.ly`).

## Where pieces can come from

| Source | License picture | Format | Verdict |
|---|---|---|---|
| **Mutopia Project** (mutopiaproject.org; all files also on GitHub: MutopiaProject/MutopiaProject) | Each piece says its license in the file: *Public Domain*, CC-BY, or CC-BY-SA | LilyPond (+ PDF, MIDI on the website) | **Main source.** Use the *Public Domain* and plain CC-BY ones. Our build refuses CC-BY-SA |
| OpenScore (openscore.cc) | Everything CC0 | MuseScore / MusicXML | Clean license, but it is mostly songs (Lieder) and string quartets, little beginner piano. Worth a look for melodies |
| IMSLP | Old scans are public domain in the US; typeset files have mixed licenses | Mostly PDF | Good for **checking** and for an educator to type new editions from. Not a direct source of MusicXML |
| MuseScore.com user uploads | Mixed, often unclear; site terms apply | MuseScore | **Avoid** |
| Typing our own editions | Notes of a public-domain piece cannot be owned; our own typesetting can be CC0 | MusicXML | **Best for the very easiest songs** (see Gaps) |

Most important rule from `licenses/SOURCING.md`: a public-domain composition does not make every edition public
domain. Each candidate here records **which edition** it was typeset from and its **typesetter's license**.

## Converted and ready to check (78 files)

How the converter works: LilyPond compiles the Mutopia file, and a small listener inside LilyPond's MIDI pass logs every
note it plays with its exact start and length (fractions, no rounding), its written spelling, staff, voice, ties and
grace notes, plus key, time signature, pickup and clef. music21 writes MusicXML from that. Two checks must pass or no
file is written: the logged notes are exactly the notes in LilyPond's own MIDI file (pitch and start, within one MIDI
tick for tuplets), and the MusicXML read back has exactly those notes again. All 78 files pass both.

Known quirks for the proofreader: repeats are written out (as performed); a pickup bar is written as a full first bar
that starts with a rest; music for two voices on one staff is written as voices; old LilyPond syntax was repaired
automatically in a temporary copy (`-|` staccatissimo, `f8'` octave marks, `#:text` markup).

### Bach: Notebook for Anna Magdalena Bach (12)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| Menuet (BWV Anh. 113) | 1 flat | 3/4 | 32 | [74](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=74) | `bach-bwv-anh-113-menuet.mxl` |
| Menuet (BWV Anh. 114) | 1 sharp | 3/4 | 32 | [75](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=75) | `bach-bwv-anh-114-menuet.mxl` |
| Menuet (BWV Anh. 115) | 2 flats | 3/4 | 32 | [76](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=76) | `bach-bwv-anh-115-menuet.mxl` |
| Menuet (BWV Anh. 116) | 1 sharp | 3/4 | 40 | [77](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=77) | `bach-bwv-anh-116-menuet.mxl` |
| Polonaise in F major (BWV Anh. 117b) | 1 flat | 3/4 | 16 | [1015](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1015) | `bach-bwv-anh-117b-polonaise-in-f-major.mxl` |
| Minuet in B-flat major (BWV Anh. 118) | 2 flats | 3/4 | 26 | [1014](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1014) | `bach-bwv-anh-118-minuet-in-b-flat-major.mxl` |
| Polonaise in G minor (BWV Anh. 119) | 2 flats | 3/4 | 16 | [1016](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1016) | `bach-bwv-anh-119-polonaise-in-g-minor.mxl` |
| Minuet in A minor (BWV Anh. 120) | none | 3/4 | 29 | [1612](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1612) | `bach-bwv-anh-120-minuet-in-a-minor.mxl` |
| Minuet in C minor (BWV Anh. 121) | 3 flats | 3/4 | 24 | [1613](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1613) | `bach-bwv-anh-121-minuet-in-c-minor.mxl` |
| Musette (BWV Anh. 126) | 2 sharps | 2/4 | 20 | [79](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=79) | `bach-bwv-anh-126-musette.mxl` |
| March in E-flat major (BWV Anh. 127) | 3 flats | 2/2 | 29 | [1614](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1614) | `bach-bwv-anh-127-march-in-e-flat-major.mxl` |
| Polonaise in D minor (BWV Anh. 128) | 1 flat | 3/4 | 18 | [1615](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1615) | `bach-bwv-anh-128-polonaise-in-d-minor.mxl` |
### Mozart (written at age 5–6) (1)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| Menuett N°2 fûr das Pianoforte Kôch Verz N°2 (KV 2) | 1 flat | 3/4 | 24 | [1770](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1770) | `mozart-kv-2-menuett-n2-fur-das-pianoforte-koch-verz.mxl` |
### Czerny: exercises (Op. 821 and Op. 840) (29)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| 50 Melodische Übungsstücke, No. 1 | none | 4/4 | 33 | [2146](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2146) | `czerny-op-840-no-1-50-melodische-ubungsstucke-no-1.mxl` |
| 50 Melodische Übungsstücke, No. 10 | 1 sharp | 4/4 | 32 | [2177](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2177) | `czerny-op-840-no-10-50-melodische-ubungsstucke-no-10.mxl` |
| 50 Melodische Übungsstücke, No. 2 | 1 flat | 6/8 | 33 | [2147](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2147) | `czerny-op-840-no-2-50-melodische-ubungsstucke-no-2.mxl` |
| 50 Melodische Übungsstücke, No. 3 | 3 flats | 3/8 | 48 | [2148](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2148) | `czerny-op-840-no-3-50-melodische-ubungsstucke-no-3.mxl` |
| 50 Melodische Übungsstücke, No. 4 | 2 flats | 3/4 | 65 | [2149](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2149) | `czerny-op-840-no-4-50-melodische-ubungsstucke-no-4.mxl` |
| 50 Melodische Übungsstücke, No. 5 | none | 2/4 | 40 | [2150](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2150) | `czerny-op-840-no-5-50-melodische-ubungsstucke-no-5.mxl` |
| 50 Melodische Übungsstücke, No. 6 | none | 6/8 | 33 | [2151](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2151) | `czerny-op-840-no-6-50-melodische-ubungsstucke-no-6.mxl` |
| 50 Melodische Übungsstücke, No. 7 | none | 2/4 | 57 | [2152](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2152) | `czerny-op-840-no-7-50-melodische-ubungsstucke-no-7.mxl` |
| 50 Melodische Übungsstücke, No. 8 | none | 2/4 | 32 | [2153](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2153) | `czerny-op-840-no-8-50-melodische-ubungsstucke-no-8.mxl` |
| 50 Melodische Übungsstücke, No. 9 | 2 flats | 2/4 | 48 | [2154](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2154) | `czerny-op-840-no-9-50-melodische-ubungsstucke-no-9.mxl` |
| 160 Eight-Measure Exercises, No. 1 | none | 4/4 | 8 | [2060](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2060) | `czerny-op-821-no-1-160-eight-measure-exercises-no-1.mxl` |
| 160 Eight-Measure Exercises, No. 2 | none | 3/4 | 8 | [2061](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2061) | `czerny-op-821-no-2-160-eight-measure-exercises-no-2.mxl` |
| 160 Eight-Measure Exercises, No. 3 | none | 4/4 | 8 | [2062](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2062) | `czerny-op-821-no-3-160-eight-measure-exercises-no-3.mxl` |
| 160 Eight-Measure Exercises, No. 4 | none | 6/8 | 8 | [2063](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2063) | `czerny-op-821-no-4-160-eight-measure-exercises-no-4.mxl` |
| 160 Eight-Measure Exercises, No. 5 | 1 flat | 3/4 | 8 | [2066](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2066) | `czerny-op-821-no-5-160-eight-measure-exercises-no-5.mxl` |
| 160 Eight-Measure Exercises, No. 6 | 1 flat | 3/4 | 8 | [2067](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2067) | `czerny-op-821-no-6-160-eight-measure-exercises-no-6.mxl` |
| 160 Eight-Measure Exercises, No. 7 | 1 flat | 4/4 | 8 | [2068](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2068) | `czerny-op-821-no-7-160-eight-measure-exercises-no-7.mxl` |
| 160 Eight-Measure Exercises, No. 8 | 1 flat | 4/4 | 8 | [2069](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2069) | `czerny-op-821-no-8-160-eight-measure-exercises-no-8.mxl` |
| 160 Eight-Measure Exercises, No. 9 | 1 flat | 6/8 | 8 | [2072](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2072) | `czerny-op-821-no-9-160-eight-measure-exercises-no-9.mxl` |
| 160 Eight-Measure Exercises, No. 10 | 1 flat | 2/4 | 8 | [2073](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2073) | `czerny-op-821-no-10-160-eight-measure-exercises-no-10.mxl` |
| 160 Eight-Measure Exercises, No. 11 | 2 flats | 4/4 | 8 | [2076](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2076) | `czerny-op-821-no-11-160-eight-measure-exercises-no-11.mxl` |
| 160 Eight-Measure Exercises, No. 12 | 2 flats | 4/4 | 8 | [2077](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2077) | `czerny-op-821-no-12-160-eight-measure-exercises-no-12.mxl` |
| 160 Eight-Measure Exercises, No. 13 | 2 flats | 4/4 | 8 | [2078](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2078) | `czerny-op-821-no-13-160-eight-measure-exercises-no-13.mxl` |
| 160 Eight-Measure Exercises, No. 14 | 2 flats | 3/8 | 16 | [2079](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2079) | `czerny-op-821-no-14-160-eight-measure-exercises-no-14.mxl` |
| 160 Eight-Measure Exercises, No. 15 | 1 sharp | 2/4 | 8 | [2081](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2081) | `czerny-op-821-no-15-160-eight-measure-exercises-no-15.mxl` |
| 160 Eight-Measure Exercises, No. 16 | 1 sharp | 2/4 | 8 | [2082](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2082) | `czerny-op-821-no-16-160-eight-measure-exercises-no-16.mxl` |
| 160 Eight-Measure Exercises, No. 17 | 1 sharp | 4/4 | 8 | [2083](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2083) | `czerny-op-821-no-17-160-eight-measure-exercises-no-17.mxl` |
| 160 Eight-Measure Exercises, No. 18 | 1 sharp | 3/8 | 8 | [2084](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2084) | `czerny-op-821-no-18-160-eight-measure-exercises-no-18.mxl` |
| 160 Eight-Measure Exercises, No. 19 | 2 sharps | 3/4 | 8 | [2085](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2085) | `czerny-op-821-no-19-160-eight-measure-exercises-no-19.mxl` |
### Tchaikovsky: Album for the Young, Op. 39 (3)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| Morning Prayer (Op. 39, No. 1) | 1 sharp | 3/4 | 24 | [2032](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2032) | `tchaikovsky-op-39-no-1-morning-prayer.mxl` |
| March of the Wooden Soldiers (Op. 39, No. 5) | 2 sharps | 2/4 | 48 | [1806](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1806) | `tchaikovsky-op-39-no-5-march-of-the-wooden-soldiers.mxl` |
| Old French Song (Op.0) | none | 2/4 | 33 | [2080](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2080) | `tchaikovsky-op-0-old-french-song.mxl` |
### Burgmüller: 25 Easy and Progressive Studies, Op. 100 (18)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| La Candeur | none | 4/4 | 23 | [202](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=202) | `burgmuller-opus-100-la-candeur.mxl` |
| l'Arabesque | none | 2/4 | 33 | [203](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=203) | `burgmuller-opus-100-l-arabesque.mxl` |
| La Pastorale | 1 sharp | 6/8 | 29 | [218](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=218) | `burgmuller-opus-100-la-pastorale.mxl` |
| La Petite Réunion | none | 4/4 | 30 | [219](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=219) | `burgmuller-opus-100-la-petite-reunion.mxl` |
| Innocence | 1 flat | 3/4 | 17 | [214](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=214) | `burgmuller-opus-100-innocence.mxl` |
| Progrès | none | 4/4 | 16 | [215](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=215) | `burgmuller-opus-100-progres.mxl` |
| Le Courant Limpide | 1 sharp | 4/4 | 16 | [216](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=216) | `burgmuller-opus-100-le-courant-limpide.mxl` |
| La Gracieuse | 1 flat | 3/4 | 16 | [217](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=217) | `burgmuller-opus-100-la-gracieuse.mxl` |
| La Chasse | none | 6/8 | 57 | [220](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=220) | `burgmuller-opus-100-la-chasse.mxl` |
| Tendre Fleur | 2 sharps | 4/4 | 24 | [221](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=221) | `burgmuller-opus-100-tendre-fleur.mxl` |
| La Bergeronnette | none | 2/4 | 30 | [222](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=222) | `burgmuller-opus-100-la-bergeronnette.mxl` |
| L'Adieu | none | 4/4 | 42 | [223](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=223) | `burgmuller-opus-100-l-adieu.mxl` |
| Consolation | none | 4/4 | 27 | [224](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=224) | `burgmuller-opus-100-consolation.mxl` |
| La Styrienne | 1 sharp | 3/4 | 37 | [225](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=225) | `burgmuller-opus-100-la-styrienne.mxl` |
| Ballade | 3 flats | 3/8 | 96 | [227](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=227) | `burgmuller-opus-100-ballade.mxl` |
| Douce Plainte | 2 flats | 4/4 | 18 | [228](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=228) | `burgmuller-opus-100-douce-plainte.mxl` |
| La Babillarde | 1 flat | 3/8 | 35 | [229](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=229) | `burgmuller-opus-100-la-babillarde.mxl` |
| Inquiétude | 1 sharp | 2/4 | 31 | [230](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=230) | `burgmuller-opus-100-inquietude.mxl` |
### Sonatinas and other pieces (15)

| Piece | Key signature | Meter | Bars (as played) | Mutopia | File |
|---|---|---|---|---|---|
| Ludwig van Beethoven: Für Elise (WoO 59) | none | 3/8 | 105 | [931](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=931) | `beethovenlv-woo-59-fur-elise.mxl` |
| Ludwig van Beethoven: Menuett Op. WoO 82 | none | 3/4 | 123 | [904](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=904) | `beethovenlv-woo-82-menuett-op-woo-82.mxl` |
| Frédéric Chopin: Prelude: Op. 28, No. 20 | 3 flats | 4/4 | 13 | [472](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=472) | `chopin-op-28-prelude-op-28-no-20.mxl` |
| Frédéric Chopin: Prelude: Op. 28, No. 4 ('Suffocation') | 1 sharp | 2/2 | 26 | [468](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=468) | `chopin-op-28-prelude-op-28-no-4-suffocation.mxl` |
| Muzio Clementi: Sonatina, movement 1 (O 36) | none | 2/2 | 38 | [804](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=804) | `clementi-o-36-sonatina-1.mxl` |
| Muzio Clementi: Sonatina, movement 2 (O 36) | 1 flat | 3/4 | 26 | [804](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=804) | `clementi-o-36-sonatina-2.mxl` |
| Muzio Clementi: Sonatina, movement 3 (O 36) | none | 3/8 | 70 | [804](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=804) | `clementi-o-36-sonatina-3.mxl` |
| Joseph Haydn: Sonate I, II - Menuetto (Hob. XVI:27) | 1 sharp | 3/4 | 66 | [186](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=186) | `haydn-hob-xvi-27-sonate-i-ii-menuetto.mxl` |
| Joseph Haydn: Sonate I, III - Presto (Hob. XVI:27) | none | 2/4 | 153 | [187](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=187) | `haydn-hob-xvi-27-sonate-i-iii-presto.mxl` |
| Friedrich Kuhlau: Sonatine I - Allegro (O 20, No. 1: 1) | none | 4/4 | 80 | [232](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=232) | `kuhlau-o-20-no-1-1-sonatine-i-allegro.mxl` |
| Friedrich Kuhlau: Sonatine I - Andante (O 20, No. 1: 2) | 1 flat | 6/8 | 17 | [233](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=233) | `kuhlau-o-20-no-1-2-sonatine-i-andante.mxl` |
| Friedrich Kuhlau: Sonatine I - Rondo (O 20, No. 1: 3) | none | 2/4 | 158 | [234](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=234) | `kuhlau-o-20-no-1-3-sonatine-i-rondo.mxl` |
| Ignaz Pleyel: Rondo | none | 3/4 | 32 | [191](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=191) | `pleyel-rondo.mxl` |
| Erik Satie: Gymnopédie No. 1 | 2 sharps | 3/4 | 47 | [37](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=37) | `satie-gymnopedie-no-1.mxl` |
| Johann Baptist Wanhal: Rondo (Opus 42, No. 1) | none | 2/4 | 56 | [192](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=192) | `wanhal-opus-42-no-1-rondo.mxl` |

**Extra check needed** (also in the `note` column):
- Rondo (Ignaz Pleyel): source edition not named; compare with an old edition on IMSLP.
- Gymnopédie No. 1 (Erik Satie): typeset from a Dover reprint; confirm it reprints an old edition without new editorial material.
- Rondo (Johann Baptist Wanhal): source edition not named; compare with an old edition on IMSLP.

## Good beginner pieces we can only link to (CC-BY-SA on Mutopia)

- **Schumann, Album for the Young, Op. 68** (Melody, Soldiers' March, The Happy Farmer, Wild Rider…): every Mutopia
  edition is CC-BY-SA, so our build will not play them. They can be listed with a link and credit. A new CC0
  edition typed from a public-domain scan would remove the restriction.
- **Diabelli, Melodious Exercises Op. 149 and Op. 163** (piano duets): CC-BY-SA.

## Gaps

- **Pre-reader and Level 1 need very easy songs** (Hot Cross Buns, Mary Had a Little Lamb, Twinkle, Ode to Joy,
  Lightly Row, Au clair de la lune, Frère Jacques). Mutopia has few of these as piano music under a usable license.
  Two routes, both legally clean: (1) the educator types each tune into MuseScore and releases it as CC0 (the melodies
  are public domain); (2) take the tune from public-domain vocal arrangements on Mutopia (*Ode to Joy* SATB,
  *Stille Nacht*, *The First Noel* and *Greensleeves* hymn tunes, *Oats and Beans*) with the pipeline's extract step.
- Popular beginner books not on Mutopia under usable licenses: Türk *Handstücke*, Gurlitt, Beyer *Op. 101*, Köhler,
  Streabbog. All are public domain as compositions; scans of old editions on IMSLP could be typed as new CC0 editions.

## How a candidate becomes a shipped piece

1. **License check by a person:** open the piece's Mutopia page, confirm the license and source edition, fill the
   row in `licenses/candidates.csv` (`verified_by`, `verified_date`), following `licenses/SOURCING.md`.
2. **Proofread the conversion** against Mutopia's PDF and fix it in MuseScore if needed (`proofread_by`). See the known
   quirks above (written-out repeats, pickup bars, voices).
3. Copy the file to `scores/source/<asset_id>.mxl` and add the row to `licenses/assets.csv`
   (`derivatives_allowed` = `yes`, `source_format` = `mxl`).
4. Write a recipe in `scores/recipes/`, run the score pipeline, check the simplified score, run `approve.py`.
5. Put the `asset_id` in a week's `repertoire_ids` and run `python3 app/build.py`. The player, highlighting and
   wait-for-me mode switch on by themselves for approved pieces that pass the license gate.

Sources: [Mutopia Project (Wikipedia)](https://en.wikipedia.org/wiki/Mutopia_Project),
[Mutopia Project (Creative Commons wiki)](https://wiki.creativecommons.org/Mutopia_Project),
[Introducing OpenScore](https://openscore.cc/blog/introducing-openscore),
[OpenScore's plans to liberate sheet music (Creative Commons)](https://creativecommons.org/2017/06/30/openscores-plans-liberate-sheet-music/),
and the license headers of each `.ly` file in the MutopiaProject/MutopiaProject GitHub repository (read 2026-10-11).
