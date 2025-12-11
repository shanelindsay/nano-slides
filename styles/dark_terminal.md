# Visual Design Language: Dark Terminal

**Role**  
Render slide images that look like a developer console or dark‑mode IDE. Ideal for live coding, tooling demos, and technical deep dives.

**Philosophy**  
Feel like a dark coding environment: high contrast on a dark background, clear code/output, minimal ornament.

---

## 1. Core visual style

### Background
- Deep near‑black: `#0b0c10`, `#111217`, or `#121212`.
- Very subtle noise/vignette acceptable, kept low.

### Colour
- Main text: light grey (`#e0e0e0`), not pure white.
- Syntax‑style accents:
  - Strings: soft yellow/orange.
  - Keywords: cyan/teal.
  - Comments: muted grey‑green.
- Use accents consistently across slides.

### Typography
- Monospaced for most content: JetBrains Mono, Fira Code, Cascadia Code, Consolas.
- Titles can be mono or clean sans.
- Code blocks look like real code with proper indentation.

---

## 2. Layout patterns

### Title slide
- Large mono/sans title, aligned like a command line.
- Optional prompt prefix (`$`, `>`).
- Subtitle/name on smaller lines below.

### Code slide
- Small title (or comment) at top left.
- Large central code block framed like a terminal/editor pane.
- Faint borders/rules to mimic windows.

### Terminal output
- Command near top; output below, same mono style.
- Important lines highlighted with colour or subtle shading.

### Diagram slide
- Architecture/network diagrams on dark background.
- Lines light grey; labels light grey; key nodes in accent colours.

---

## 3. Assets
- Screenshots of terminals/editors: blend themes to match dark palette.
- Logos: simplified/reversed light‑on‑dark versions.

---

## 4. Execution rules
1. Text large enough and high contrast for dark rooms.  
2. One code snippet or concept per slide.  
3. Avoid bright white blocks.  
4. Align code as in a real editor; spacing looks intentional.  
5. Keep dark palette and syntax colours consistent throughout.***
