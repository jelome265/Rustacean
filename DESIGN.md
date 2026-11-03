---
name: Rustacean site
description: Visual system for the Rustacean GitHub Pages site. Steel tempering: a cool mill-sheet ground, tempering-blue fields, and straw used only to mark what has been checked.
colors:
  mill: "#eef0ec"
  mill-2: "#e2e6e1"
  ink: "#14171c"
  ink-2: "#252b33"
  temper: "#2c4a7b"
  temper-deep: "#213a63"
  temper-muted: "#e3ebf6"
  paper: "#eef2f5"
  straw: "#e0b14a"
  code: "#111a2b"
  code-text: "#e9eef7"
  code-muted: "#9fb0cc"
typography:
  display:
    fontFamily: "Bricolage Grotesque"
    fontWeight: 720
    fontStretch: 88%
    letterSpacing: -0.03em
    lineHeight: 0.94
  body:
    fontFamily: "Bricolage Grotesque"
    fontSize: 17px
    lineHeight: 1.55
  code:
    fontFamily: "JetBrains Mono"
    fontSize: 14px
    lineHeight: 1.6
rounded:
  none: 0px
spacing:
  gutter: "clamp(20px, 4.2vw, 56px)"
  maxWidth: 1240px
  sectionPadding: "clamp(88px, 11vw, 144px)"
components:
  button-primary:
    backgroundColor: "{colors.straw}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    height: 52px
  button-secondary:
    backgroundColor: "{colors.mill-2}"
    textColor: "{colors.ink}"
  console:
    backgroundColor: "{colors.code}"
    textColor: "{colors.code-text}"
  manifest:
    backgroundColor: "{colors.temper}"
    textColor: "{colors.paper}"
  verified-chip:
    backgroundColor: "{colors.straw}"
    textColor: "{colors.ink}"
---

# Rustacean site: design system

## Overview

The site describes Rust rules that can be checked. The visual idea comes from steel tempering: heat-treated steel shows a sequence of oxide colours (straw, purple, blue) that tell a metalworker the part has reached a set state. The system uses that idea in three ways. The ground is a cool mill-sheet grey. The large fields are tempering blue. Straw is reserved for the one signal that means "checked": the primary action, the rule IDs, and the caveat. Nothing is decorative.

Mode: Persuade. This is a project landing page, so it has a point of view, and its job is to get a visitor to install or read the source within seconds.

Physical scene: an engineer reads this at a desk in daylight, comparing it with a terminal open beside it. The light is bright and neutral, which is why the ground is light and the blue fields provide contrast.

## Colours

- **Mill** (`#eef0ec`): page ground. Carries the majority of the page.
- **Mill-2** (`#e2e6e1`): header and secondary surfaces.
- **Temper** (`#2c4a7b`): large fields (hero manifest, install section). Paper text on temper measures 7.4:1 at its lightest muted tint.
- **Straw** (`#e0b14a`): fills only. Primary buttons, RS-ID chips, the verification caveat. Straw is never used as small text on temper (it measures 4.45:1 there, below the 4.5:1 minimum).
- **Ink** (`#14171c`): text on mill (15.7:1) and the footer ground.
- **Code** (`#111a2b`): command blocks. Code text measures 15:1.

Strategy: Committed. Temper carries roughly a third of the page through two fields.

## Typography

Bricolage Grotesque is used for display and body, from a self-hosted variable file (weight 200 to 800, width 75% to 100%). JetBrains Mono is used only for literal code (commands, `--agent` IDs, inline code).

The desktop scale has six sizes: 14 (labels and small text), 17 (body), 20 (lead and list text), 34 (skill names), 88 (section and verify headings), and 112 (hero). Mobile reduces the display sizes with `min()` and `max()` so every headline stays within two lines at 390px.

Headlines use negative tracking (-0.025em to -0.03em) at weight 720 and width 88%. Body copy is set in full ink (15:1 on mill) and not in grey.

## Layout

- One pair of outer margins at every width, set by `--gutter` (20px on phones, 56px on wide screens) and a 1240px maximum content width.
- Sections are separated by generous space (88px to 144px). There are no rules between sections. Change of ground does the separating.
- Two-column splits (hero, install, verify) collapse to one column below 920px.
- The skills are a ledger: one row per skill, with identifier, name, description, and use-for columns. Rows are separated by space, not by lines.

## Elevation and shape

No shadows. No gradients. No rounded corners (radius 0). Depth comes only from ground changes between sections.

## Components

- **Primary button**: straw fill, ink text, 52px high. Hover inverts to ink with straw text.
- **Secondary button**: mill-2 fill, ink text.
- **Manifest**: temper panel listing the five skills. Each row has a straw-filled ID chip with ink text.
- **Console**: code-coloured panel. Commands are literal code. Copy buttons are straw-filled, 44px high.
- **Agent selector**: a select with 12 options. Its values are the installer's real `--agent` IDs. The two commands below update when it changes.
- **Agents table**: zebra-striped. Evidence is shown as a filled chip: straw for official, ink for conflicting, mill-2 for third-party. Below 900px the table stacks into labelled blocks, with no sideways scroll.
- **Caveat**: straw panel stating what a successful install does not prove.

## Motion

Entrance: elements rise 22px and settle as they enter the viewport. The motion runs only when JavaScript is running, and content is visible without it. It is removed entirely under `prefers-reduced-motion`.

## Accessibility

- Touch targets: buttons and links are at least 44px high. Primary buttons are 52px.
- Focus: a 3px ink outline on light grounds, and a 3px straw outline inside the temper and footer sections. Non-text contrast is at least 3:1 in both cases. This is a judgement under WCAG 1.4.11, since the Apple HIG references do not cover web focus rings.
- Increased contrast: under `prefers-contrast: more`, secondary text becomes full ink, muted text on temper becomes white, and buttons and chips gain a 2px border.
- Reduced motion: no transitions or entrance motion.
- Automated checks: axe-core reports zero violations at 1440px and 390px.

## Do

- Use straw only to mark something checked or to carry the primary action.
- Use the installer's real IDs for every value that is a command or a target.
- Keep headlines to two lines or fewer at every width.

## Don't

- Don't add eyebrow labels, numbered section markers, gradients, shadows, glass blur, or hairline dividers.
- Don't use monospace for labels or identifiers. Use it only for literal code.
- Don't add a second accent colour.

## Known gaps

- **No photography or footage.** The site has no real pictures or video. The build environment could not reach any open image or footage collection, so none were added. Honest candidates would be photographs of steel tempering colours, the Rust foundation or open-source community events, or a short clip of the installer running. None of these should be drawn or generated and presented as real.
- The installer's dry-run and apply output has not been captured for display. Only the commands are shown.
