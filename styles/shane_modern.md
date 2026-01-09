# Visual Design Language: Shane Modern

**Role**  
Render widescreen (16:9) minimalist teaching slides with big, high-contrast sans-serif typography and generous whitespace.

**Philosophy**  
One idea per slide, minimal clutter, intentional emphasis. Structure is obvious, every element snaps to a consistent grid, and colour is used sparingly for meaning.

---

## 1. Core visual style

### Background and colour
- Background: white `#FFFFFF`
- Primary text (charcoal): `#3A3A3A`
- Secondary text (muted grey): `#6B6B6B`
- Dark slate (dividers, heavy blocks): `#111827`
- Deep navy (title header band option): `#0B1026`
- Black (only when necessary): `#000000`

### Accent colours (role-based)
- **Primary structural accent** (titles, section cues): Teal `#20D2D6`
- **Banner accent** (quiz, "activity", strong callouts only): Cyan `#00B0F0`
- **Primary emphasis** (key phrases, label chips): Coral `#FF622D`
- **Technical emphasis** (terms, variables, definitions): Royal blue `#3C78D8`
- **Secondary emphasis** (optional, rare): Amber `#FFA825`
- **Urgent note** (rare, short): Deep red `#D7263D`

### Colour rules
- Default slide uses **one accent family** plus neutrals.
- Cyan is for **banners only**, not general highlighting.
- Coral is the default emphasis colour. Blue is specifically for technical terms.
- Amber is optional and used sparingly, only when you need a second tier of emphasis.

### Typography
- Font: modern sans-serif (Aptos or Arial). Use one family across the deck.
- Weights: bold for titles and banners. Regular for body. Italic only for short label chips if you want a "tag" feel.
- Scale (three levels only):
  - Title: very large
  - Main statement: large
  - Supporting detail: medium (rare)
- Alignment: left-aligned by default. Centred text is reserved for divider slides and occasional punchline slides.

### Grid and spacing
- Use a consistent margin system on every slide.
- Keep title position fixed across content slides.
- Keep spacing between title and body consistent.
- Avoid letting text span the full width. Prefer a readable text block with clear line breaks.

---

## 2. Layout patterns

### Content slide
- White background
- Teal title at top
- Large charcoal body text
- Optional: one image block on the right or lower half

### Divider slide
- Full dark slate background `#111827`
- One giant centred title in white
- Nothing else

### Banner slide (quiz, activity, prompt)
- Full-width cyan bar `#00B0F0` across the top with white bold text
- White body area beneath with large charcoal text

### Title slide
- Deep navy header band `#0B1026` (top portion) with white title text
- Optional thin black vertical strip at left for branding
- Lower area split: clean text box on one side, large image on the other

### Definition or key term
- Title in teal `#20D2D6`
- Key term set large (often in royal blue `#3C78D8`)
- One-line definition in charcoal
- Optional small coral label chip: "Key idea", "Remember", "Example"

---

## 3. Shape language and UI components

### Shapes
- **Flat fills only.** No gradients, no heavy shadows.
- **Chips/labels:** small rounded rectangles in coral `#FF622D` with white text (short phrases only).
- **Boxes:** simple rectangles with plenty of padding, usually no outline.
- **Lines:** minimal, used to separate regions rather than decorate.

### Images
- Images are allowed to be informal (memes, screenshots), but placed consistently:
  - **Full-bleed image** with a simple caption bar, or
  - **Split layout** with a fixed image region and a fixed text region
- Captions are short, high-contrast, and positioned consistently.

---

## 4. Assets
- Logos: small, unobtrusive; positioned consistently (e.g., bottom corner).
- Screenshots: crop to relevant area; place in fixed regions.
- Diagrams: flat style, high contrast, clean sans-serif labels.

---

## 5. Execution rules
1. Maintain high contrast for projector visibility.
2. Use consistent spacing and alignment across slides; snap to grid.
3. Reserve each accent colour for its designated role; do not mix freely.
4. If content feels dense, split into two slides rather than shrinking text.
5. Keep one clear focal point per slide; avoid competing visual elements.
