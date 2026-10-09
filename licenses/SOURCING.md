# Sourcing checklist for sheet music and audio

Use this checklist before adding any row to `assets.csv`. This is a rule of thumb, not legal advice.

## ⚠️ The most important rule: three separate licenses

A piece of music has **three layers**, and each one has its own copyright:

| Layer | Example | Column in assets.csv |
|---|---|---|
| **Composition** (the notes the composer wrote) | Bach's Minuet in G | `composition_status` |
| **Edition / score** (a specific engraved or edited version) | A 1990s edition with fingerings added | `edition_source`, `edition_license` |
| **Recording** (a specific performance) | A pianist's 2015 recording | `recording_source`, `recording_performer`, `recording_license` |

**A public-domain composition does NOT mean a public-domain edition or recording.** Bach is PD, but a modern edited score or a modern recording of Bach is usually still under copyright. Check every layer.

## US public-domain rule of thumb (as of 2026)

- **Compositions and printed editions:** works **published in the US before January 1, 1931** are public domain. Each January 1, one more year enters (in 2027 the cutoff becomes 1932). Short version: published more than 95 years ago.
- **Unpublished works:** generally protected until 70 years after the composer's death.
- **Sound recordings:** recordings **published before January 1, 1926** are public domain (Music Modernization Act). Newer recordings are protected for a long time, so use only recordings that carry a CC0/CC-BY/PD license from the performer or publisher.
- **New editorial work** (added fingerings, dynamics, realized ornaments, new typesetting by someone today) can carry its own copyright. Use the license the editor or typesetter gave.
- **When unsure, do not use it.** Pick another source.

## Preferred licenses (best first)

1. **Public Domain / CC0**: no attribution needed (we still record the source).
2. **CC-BY**: OK; must show `attribution_text`.
3. **CC-BY-SA**: OK for linking; record it. Any adapted version must keep the same license.
4. **CC-BY-NC / CC-BY-ND**: avoid if possible. Note it in `notes`.
5. **"All rights reserved", no license, or unclear**: **do not use.**

Our app links to scores and audio. It never copies them into the app. We still track licenses so we only point families to properly licensed material, and so we can show correct credits.

---

## Checklist by source

### Mutopia Project (mutopiaproject.org)
- [ ] Open the piece's own page (not the site's general page).
- [ ] Read the license shown for **that piece**. Mutopia uses Public Domain, CC-BY, and CC-BY-SA. They differ per piece.
- [ ] Copy the license into `edition_license`. Record the "typeset by" / maintainer name in `attribution_text` if CC-BY or CC-BY-SA.
- [ ] Confirm the composition itself is PD (see the rule of thumb above).
- [ ] Link to the piece's page or PDF in `url`.

### IMSLP (imslp.org)
- [ ] Open the **specific file** you want, not just the work page. Each file has its own copyright tag.
- [ ] Check the file is marked **Public Domain in the US** (IMSLP is based in Canada. Watch for "Non-PD US" warnings).
- [ ] For scans of old printed editions: check the **publication year** of that edition (before 1931 for US PD as of 2026).
- [ ] For new typeset files uploaded by users: check the license tag (often CC-BY or CC-BY-SA). Record the uploader/typesetter in `attribution_text`.
- [ ] Recordings on IMSLP: check each recording's own license tag separately.
- [ ] Put the edition publisher + year in `edition_source`.

### Musopen (musopen.org)
- [ ] Open the specific recording or score page.
- [ ] Read its license. Musopen items are **not all the same**: some are PD/CC0, some CC-BY, some have other terms.
- [ ] Use only PD, CC0, or CC-BY items. Record the performer in `recording_performer`.
- [ ] Check the score separately if you also use Musopen sheet music.

### My own recordings (family or educator)
- [ ] Composition is PD (or you have the composer's permission). Record in `composition_status`.
- [ ] The **edition you played from** is PD or CC-licensed. Record it in `edition_source` / `edition_license`.
- [ ] Every performer agrees to the license you choose (recommended: CC0 or CC-BY). For children, a parent agrees.
- [ ] Set `recording_source` to "Own recording" and `recording_license` to the chosen license.
- [ ] Upload the file somewhere public that you control (not embedded in the app), then put the link in `url`.

---

## Before you add the row

- [ ] All three layers checked and filled in (use `n/a` if a layer is not used, e.g. no recording).
- [ ] `attribution_text` written if any layer is CC-BY or CC-BY-SA.
- [ ] `verified_by` = your name. `verified_date` = today (YYYY-MM-DD).
- [ ] Save a screenshot of the license page somewhere safe (optional but helpful). Note where in `notes`.
- [ ] `asset_id` is unique, lowercase, with dashes, e.g. `bach-minuet-g-mutopia`.

**Allowed values for `composition_status`:** `public-domain-us`, `cc0`, `cc-by`, `cc-by-sa`, `permission`, `unknown` (do not use `unknown` assets).
