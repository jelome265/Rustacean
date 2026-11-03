---
name: Rustacean site
description: Visual system for the Rustacean GitHub Pages site. Black and white ground with a rust scale as the one accent, and the official Rust logo.
colors:
  mill: "#eef0ec"
  mill-2: "#e2e6e1"
  ink: "#14171c"
  ink-2: "#252b33"
  paper: "#ffffff"
  rust-50: "#fdf1ec"
  rust-100: "#fbdcd0"
  rust-200: "#f8bba0"
  rust-300: "#f39267"
  rust-400: "#ef692f"
  rust-500: "#b7410e"
  rust-600: "#ab3d0d"
  rust-700: "#89310b"
  rust-800: "#682508"
  rust-900: "#471905"
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
    backgroundColor: "{colors.rust-500}"
    textColor: "{colors.paper}"
    typography: "{typography.body}"
    height: 52px
  button-secondary:
    backgroundColor: "{colors.mill-2}"
    textColor: "{colors.ink}"
  console:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  manifest:
    backgroundColor: "{colors.rust-700}"
    textColor: "{colors.paper}"
  rule-chip:
    backgroundColor: "{colors.rust-100}"
    textColor: "{colors.ink}"
---

# Rustacean site: design system

## Overview

The site describes Rust rules that can be checked. The system is black and white, with one accent: a rust scale. The official Rust logo is the brand mark. Nothing is decorative: there are no gradients, shadows, glass effects, eyebrow labels, or numbered section markers.

Mode: Persuade. This is a project landing page. Its job is to get a visitor to install the suite or read the source within seconds.

Physical scene: an engineer reads this at a desk in daylight, comparing it with a terminal open beside it. The light is bright and neutral, so the ground is light and the accent fields carry the contrast.

## Colours

- **Mill** (`#eef0ec`) and **paper** (`#ffffff`): page ground and text on dark fields.
- **Ink** (`#14171c`): text on mill (15.7:1), command blocks, footer.
- **Rust scale**: 50 to 900, derived from the base hue `#b7410e`. Each step is for one role:
  - `rust-500` (`#b7410e`): primary button. White text on it measures 5.6:1.
  - `rust-700` (`#89310b`): the manifest and install fields, with white text at 8.4:1. Running text needs 7:1, which `rust-500` cannot reach.
  - `rust-600` (`#ab3d0d`): the hero accent word on mill, 6.2:1 for large text.
  - `rust-700` on mill: small accent text (7.3:1).
  - `rust-100` and `rust-300`: light chips with ink text (14:1 and 7.8:1).
  - `rust-50`: muted text on rust fields (at least 5.0:1).

The base hue is a design choice. The Rust artwork repository does not define an official brand colour, so the site does not claim one.

Strategy: Restrained. Black and white carry the page. Rust carries the primary action, the two dark fields, and the accent word.

## Logo

- Header: `rust-logo-single-path.svg`, the official black logo, on the mill ground.
- Manifest and footer: `rust-logo-white-outline.svg`, the official white-outline logo, on rust and ink.
- The logos are not recoloured or altered. They are CC-BY 4.0 (© Rust Foundation). Credit, a licence link, and a non-endorsement notice are in the footer. Trademark terms are in `site/assets/brand/README.md`.

## Typography

Bricolage Grotesque is used for display and body, from a self-hosted variable file (weight 200 to 800, width 75% to 100%). JetBrains Mono is used only for literal code (commands, `--agent` IDs, inline code).

The desktop scale has six sizes: 14 (labels and small text), 17 (body), 20 (lead and list text), 34 (skill names), 88 (section and verify headings), and 112 (hero). Mobile reduces the display sizes with `min()` and `max()` so every headline stays within two lines at 390px.

Running text is capped at about 68 characters per line.

## Layout

- One pair of outer margins at every width, set by `--gutter` (20px on phones, 56px on wide screens) and a 1240px maximum content width.
- Sections are separated by generous space and by changes of ground. There are no rules between sections.
- Two-column splits (hero, install, verify) collapse to one column below 920px.
- The skills are a ledger: one row per skill, separated by space.

## Elevation and shape

No shadows. No gradients. No rounded corners. Depth comes only from ground changes.

## Components

- **Primary button**: rust-500 fill, white text, 52px high. Hover becomes rust-700.
- **Secondary button**: mill-2 fill, ink text.
- **Manifest**: rust-700 panel with the white-outline logo, listing the five skills. Each row has a rust-100 ID chip with ink text.
- **Console**: ink code panel with a rust-700 header and footer. Copy buttons are rust-500, 44px high.
- **Agent selector**: a select with 12 options. The values are the installer's real `--agent` IDs, checked against `tools/agent_skill_targets.json`. The commands below update when it changes.
- **Agents table**: zebra-striped. Evidence is a filled chip: rust-300 for official, ink for conflicting, mill-2 for third-party. Below 900px the table stacks into labelled blocks with no sideways scroll.
- **Caveat**: rust-100 panel stating what a successful install does not prove.

## Motion

Entrance: elements slide up 22px as they enter the viewport. Content is visible without JavaScript. Motion is removed under `prefers-reduced-motion`.

## Accessibility

- Touch targets: 44px minimum. Primary buttons are 52px.
- Focus: a 3px ink outline on light grounds, rust-50 inside the install section, and rust-300 in the footer. Non-text contrast is at least 3:1. This is a WCAG 1.4.11 judgement, since the Apple guidance covers native apps rather than web focus rings.
- `prefers-contrast: more`: secondary text becomes full ink, rust text lightens to white on rust fields, and buttons and chips gain a 2px border.
- Reduced motion: no transitions or entrance motion.
- Automated checks: axe-core reports zero violations at 1440px and 390px.

## Do

- Use rust as the one accent. Use it for the primary action and for the two fields.
- Use the official logo files unaltered.
- Keep headlines to two lines or fewer at every width.

## Don't

- Don't add a second accent colour, gradients, shadows, eyebrow labels, numbered section markers, or hairline dividers.
- Don't use monospace for labels or identifiers.
- Don't recolour or redraw the Rust logo.

## Known gaps

- **No photography or footage.** The build environment cannot reach open image or video collections. Honest candidates would be photographs of steel and forge work, Rust community events, or a short clip of the installer running. Do not draw or generate these and present them as real.
- The installer's dry-run and apply output is not captured for display. Only the commands are shown.
