---
name: VoidCorp Terminal
colors:
  surface: '#2a002b'
  surface-dim: '#2a002b'
  surface-bright: '#69006d'
  surface-container-lowest: '#210022'
  surface-container-low: '#37003a'
  surface-container: '#3e0040'
  surface-container-high: '#500052'
  surface-container-highest: '#620065'
  on-surface: '#ffd6f7'
  on-surface-variant: '#d5c1d0'
  inverse-surface: '#ffd6f7'
  inverse-on-surface: '#5a005d'
  outline: '#9d8b99'
  outline-variant: '#51424e'
  surface-tint: '#ffa9fb'
  primary: '#ffa9fb'
  on-primary: '#590060'
  primary-container: '#ee82ee'
  on-primary-container: '#700478'
  inverse-primary: '#96339b'
  secondary: '#edffe1'
  on-secondary: '#013a00'
  secondary-container: '#28ff1d'
  on-secondary-container: '#027100'
  tertiary: '#ffb3ad'
  on-tertiary: '#680009'
  tertiary-container: '#ff8880'
  on-tertiary-container: '#84000f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffd6f9'
  primary-fixed-dim: '#ffa9fb'
  on-primary-fixed: '#37003b'
  on-primary-fixed-variant: '#7a1481'
  secondary-fixed: '#77ff61'
  secondary-fixed-dim: '#02e600'
  on-secondary-fixed: '#002200'
  on-secondary-fixed-variant: '#015300'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930012'
  background: '#2a002b'
  on-background: '#ffd6f7'
  surface-variant: '#620065'
typography:
  headline-lg:
    fontFamily: JetBrains Mono
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: JetBrains Mono
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
  headline-md:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  body-lg:
    fontFamily: JetBrains Mono
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  code-inline:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
  label-caps:
    fontFamily: Space Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.1em
spacing:
  cell: 8px
  gutter: 24px
  container-max: 1200px
  panel-padding: 1.5rem
---

## Brand & Style
The design system embodies a retro-futuristic, high-contrast CLI aesthetic inspired by modern Python terminal libraries. It is built for a developer-centric audience that appreciates technical precision and the nostalgic grit of low-level computing environments.

The style is **Cyber-Brutalist Minimalism**. It prioritizes information density and structural clarity through text-based UI patterns. The UI should evoke the feeling of a high-stakes mainframe interface—raw, intentional, and authoritative. Visual interest is generated through ASCII-inspired layouts, double-line borders, and rhythmic monospaced typography rather than traditional imagery or gradients.

## Colors
The palette is rooted in a deep-space black to maximize contrast and mimic a CRT monitor. 

- **Primary (#EE82EE):** Used for active commands, headers, and the blinking cursor.
- **Success (#00FF00):** Reserved for "OK" status codes, completed processes, and safe execution paths.
- **Error (#FF4444):** Used sparingly for critical system alerts and failed validations.
- **Borders (#DA70D6):** A slightly desaturated magenta used for structural framing and panel boxing.
- **Background (#0D0D0D):** The absolute base layer, providing a true-black canvas for vibrant terminal text.

## Typography
All text must be monospaced to maintain the terminal grid. **JetBrains Mono** is the primary typeface for its exceptional legibility and developer-centric glyphs. **Space Mono** is utilized for metadata, labels, and status indicators to provide a subtle geometric shift.

Large headlines should be treated as "Banner Art." Use bold weights for primary information and regular weights for standard log output. All text-based UI elements must align to a strict vertical rhythm to preserve the "grid-cell" nature of a CLI.

## Layout & Spacing
The layout follows a **Rigid Grid** philosophy. All margins and paddings must be multiples of the `cell` (8px) unit, mimicking character-cell spacing in a terminal emulator.

- **Container:** Content is centered with a fixed maximum width for readability, but individual panels within the container can behave like tiled windows.
- **Panels:** Use "Rich library" style framing. Elements are grouped in boxes with double-line or single-line borders.
- **Breakpoints:** On mobile, multi-column "tiled" layouts stack vertically. The border logic remains intact, ensuring each section looks like a separate terminal output block.

## Elevation & Depth
Depth is created through **Tonal Layering** and **Framing**, not shadows. 

- **Level 0 (Background):** Deep black (#0D0D0D).
- **Level 1 (Panels):** Defined by #DA70D6 borders. No change in background color.
- **Level 2 (Modals/Pop-overs):** Defined by a thicker border or a "shadow" effect created by offset solid-color blocks (e.g., a 4px offset magenta block behind a panel) to simulate retro layering.
- **Focus:** Active elements are indicated by a blinking underscore cursor or a solid block-invert (Primary color background with Black text).

## Shapes
This design system uses a `Sharp` (0px) roundedness policy. Every element—buttons, input fields, panels, and tags—must have 90-degree corners. This reinforces the technical, non-organic nature of a command-line interface. 

Borders are the primary decorative element. Use character-based symbols (┌, ┐, └, ┘, ─, │) or CSS `border-style: double` to create the "Rich" library box effect.

## Components
- **Buttons:** Styled as command blocks. Default state is a primary-colored border with primary-colored text. Hover/Active state is a solid primary-colored fill with black text (inverted).
- **Inputs:** Displayed as a command prompt. Use a `>` or `$` prefix. The cursor must be a blinking solid block (`_` or `█`).
- **Cards/Panels:** Defined by a title centered within the top border line (e.g., `──┤ System Logs ├──`).
- **Chips/Status:** Small text blocks wrapped in brackets, e.g., `[ SUCCESS ]` in green or `[ ERROR ]` in red.
- **Lists:** Use hyphens `-` or asterisks `*` as bullet points. Tables should use ASCII pipe `|` separators.
- **Progress Bars:** Represented by block characters `█` for filled segments and `░` for empty segments, contained within square brackets.
- **ASCII Art:** Use for the main brand mark/logo at the top of the page to establish the "Terminal" identity immediately.