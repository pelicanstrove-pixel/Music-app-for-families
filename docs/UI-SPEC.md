# UI-SPEC (draft v1) – Family Piano

Source: approved mockup #2 (side menu) on the "Family Piano App Mockups" canvas. Supplements UI-CONTEXT.md; if they conflict, ask the owner.

## Shell

- Left sidebar, 220 px, navy #1d3b5c. Content area on #f2f7fb.
- Sidebar order: logo, child chip (name, level, week), nav, backup note + "Help & placement" link.
- Nav (Standard mode): This week, All 12 weeks, Print, Pieces, Family.
- Font: Nunito (400/700/800). Touch targets >= 44 px. Real buttons, links, inputs with labels.
- Colors: navy #1d3b5c, blue #1b6a8c, yellow #ffc83d, text #1d2b3a. Strand tints: blue #cfe8f5, amber #ffe3a3, green #d9f0dd, pink #f3d6ee.
- Every screen with unreviewed content shows a "Draft content" chip. Educator-owned text stays as `[... – educator to write]` placeholders until approved.

## Modes (per child, switch in sidebar)

- **Standard:** 4 strand cards (Technique, Theory, Repertoire, Ear training), 12-week dot tracker, Print / Practice chart / Week done.
- **Beginner reader:** 4 numbered steps, large text (26 px), icon + short line, Done checkbox, "Read to me", star row.
- **Toddler:** 2x2 big picture tiles, no reading, tap to mark done, "Grown-up" button, parent cue banner.
- Kid modes show a reduced nav (Reader: Today, Songs, My stars; Toddler: Play).

## Screens

- **This week (Sidebar):** per mode above.
- **All 12 weeks:** 4x3 grid; states Done, This week, Coming up (not clickable).
- **Print:** pick one sheet (radio), options (Large print, Answer key, Name/date line), live paper preview, Print, Save as PDF. Output is black and white, letter paper, regardless of screen colors.
- **Pieces:** filter chips, rows with Learned checkbox, title/composer, license credit, week chip, Open score link.
- **Family:** backup banner (shows days since last backup), one card per child (age, level, mode, week, progress), Add a child, Backup & restore, Start over.
- **Help & placement:** mode guide per child type, FAQ accordion (print, where progress is saved, other device, change mode).

## Rules

- Progress is stored in the browser only; backup file is the only way to move or recover it. Keep the backup reminder visible.
- No accounts, no tracking, no ads. Family data stays on the device.
- Open items for the owner: placement descriptions, week focus text, pieces and license credits, final mode names.
