# Nano Banana Pro Slide Deck Generator (Fork)

This fork is a controllable slide renderer:

- You write the outline as YAML slides.
- You pick a style pack from `styles/`.
- The tool composes prompts for Gemini 3 Pro Image Preview.
- Each slide is rendered as a full image that you can view, export to PDF, or 
wrap in PowerPoint.

Original write‑up for background and style inspiration:

- [中文版 (Chinese)](https://yage.ai/nano-banana-pro.html)  
- [English Version](https://yage.ai/nano-banana-pro-en.html)

---

## Approach in one paragraph

Instead of building slides inside PowerPoint, you describe the talk as data:

- **Outline**: `slides.yaml` holds the slide sequence and content.  
- **Style**: a style pack in `styles/` describes the visual language.  
- **Generator**: `tools/generate_slides.py` combines style text, style images 
and your outline into prompts, and calls Gemini 3 Pro Image Preview.  

The result is a folder of slide images, plus a PDF and a small HTML viewer.

---

## Pros and cons

### Advantages

- **Separation of concerns**  
  Structure, content and visual style are defined separately and combined at 
render time.

- **Consistent visual identity**  
  The model sees both the style description and an example style image so decks 
tend to look coherent end to end.

- **Style‑swappable decks**  
  The same `slides.yaml` can be rendered in different styles just by changing 
`--style`.

### Limitations

- **Images, not editable shapes**  
  Output is raster images. You cannot edit text inside PowerPoint; links are not 
clickable on the slide itself.

- **Layout is a hint**  
  `layout:` values are steering signals for the model, not strict layout 
constraints.

- **Model and cost dependent**  
  Renders depend on Gemini’s behaviour and pricing, so long decks and many 
iterations will consume API quota.

---

## What this fork adds

Compared to the original Nano Banana Pro repo, this fork:

- Uses **YAML slide blocks** (`slides.yaml` by default, or any file via 
`--yaml`) rather than ad‑hoc markdown formats.
- Provides multiple **style packs** in `styles/` (for example `modern_academic`, 
`chalkboard`, `clean_keynote`, `glass_garden`).
- Uses **style reference images** automatically when they are present for a 
style.
- Generates a **PDF** and a minimal **HTML viewer** for each run, in addition to 
the per‑slide images.
- Exposes standard flags for **draft generation**, **upscaling to 4K**, and 
**optional PowerPoint export** (image‑only slides).

---

## Styles and style reference images

Each style has:

1. A **style file** in `styles/`, for example:

   - `styles/modern_academic.md`
   - `styles/chalkboard.md`
   - `styles/notebook_paper.md`
   - `styles/glass_garden.md`

2. An optional **style reference image** that shows one example slide in that
look, for example:

   - `imgs/style_ref_modern_academic_0.jpg`
   - `imgs/style_ref_chalkboard_0.jpg`
   - `imgs/style_ref_notebook_paper_0.jpg`
   - `imgs/style_anchor_glass_garden_0.jpg`

When you run:

```bash
python tools/generate_slides.py --yaml slides.yaml --style modern_academic
```

the generator:

* Loads the text spec from `styles/modern_academic.md`.
* If an image with a matching name exists in `imgs/` (for example a file
starting `style_ref_modern_academic_`), uses it as a **global style anchor**.
* Also passes any per‑slide `assets:` listed in the YAML (intended for semantic
assets such as logos/QR codes).

This means the model is guided by both the written description and a concrete
visual example, which improves consistency across slides.

You can also steer the overall tone with `--mode`:

- `structured`: more literal, bullet-friendly layouts
- `balanced`: (default) mix structure with some expressive visuals
- `expressive`: more visual/metaphorical while preserving information

For research-heavy decks, use `prompts/outline_generator_research.md` to generate a style-neutral outline with strict factual constraints.

### Recommended workflow for a new style

You can scaffold a new style automatically:

```bash
python tools/make_style.py \
  --name minimal_grid \
  --description "Very clean research-talk style, thin grid, off-white background, mono accent colour."
```

This creates `styles/minimal_grid.md` and a matching `imgs/style_ref_minimal_grid_0.*` anchor.

1. **Create a style file**
   Copy an existing file, for example:

   ```bash
   cp styles/modern_academic.md styles/my_style.md
   ```

   Edit the colours, typography and layout guidance so it describes your new 
style.

2. **Generate an example slide image**
   Use `tools/gemini_generate_image.py` to render one example slide in that 
style and save it under `imgs/` with a matching name, for example:

   ```bash
   python tools/gemini_generate_image.py \
     --prompt "One example presentation slide in the 'My Style' visual language 
described in styles/my_style.md" \
     --output imgs/style_ref_my_style \
     --size 1K --aspect-ratio 16:9
   ```

3. **Use it in your outline**
   Keep the outline style‑neutral. Render with:

   ```bash
   python tools/generate_slides.py --yaml slides.yaml --style my_style
   ```

The generator will automatically pick up both the style text and the matching
style reference image if present.

---

## Basic usage

### 1. Write an outline

Default outline file is `slides.yaml` in the repo root.
You can also point at any YAML file with `--yaml`.

### 1a. Deck defaults (optional)

Set repo-wide defaults in `deck.yaml`:

```yaml
style_pack: modern_academic      # style name or path under styles/
mode: balanced                   # structured | balanced | expressive
yaml: slides.yaml                # default outline file
```

CLI flags override these values.

Outlines are **style neutral**. Choose the style with `--style`; per-slide
`style` is treated only as a variant (e.g. `title`, `visual`). YAML format is
`---` separated slide documents, for example:

```yaml
---
slide: 2                          # explicit number
type: content                     # title | section | content | image_only | 
transition
style: title                      # optional variant (e.g. title | visual)
layout: two_content               # title_slide | title_and_content |
two_content | comparison | picture_with_caption | section_header | blank
generate: true                    # optional; defaults to true

title: Background problem
subtitle: The old world

text:                             # optional; omit for image‑only
  columns:
    - heading: Old
      bullets:
        - Fragmented visuals
        - Manual layout
        - Time sink
    - heading: New
      bullets:
        - Cohesive visuals
        - Minimal manual layout
        - Faster iteration

visual: |
  Two‑column composition: left shows fragmented assets; right shows a cohesive
  rendered scene. Keep it style neutral; the style pack will define the medium.

assets:
  - imgs/logo.png                # optional per‑slide semantic asset (logo/QR)

notes: Optional speaker notes
image_only: false
---
```

### Demos

- `demo/chalkboard/`: example run of the neutral outline rendered with `--style chalkboard` (images, PDF, PPTX, index).
- `demo/notebook_paper/`: example run of the same outline rendered with `--style notebook_paper` (images, PDF, PPTX, index).

Then render with a style pack, for example:

```bash
# Chalkboard look
python tools/generate_slides.py --yaml slides.yaml --style chalkboard --mode balanced

# Notebook paper look
python tools/generate_slides.py --yaml slides.yaml --style notebook_paper --mode structured
```

If `slides.yaml` is missing, the tool falls back to 
`outlines/sample_slides.yaml`.

### 2. Generate draft slides

Create 1K draft images for quick iteration:

```bash
python tools/generate_slides.py --yaml slides.yaml --style glass_garden --mode balanced
```

This writes a new run under:

```text
generated_slides/<yaml-stem>/<timestamp>/
```

Each run directory contains:

* `slide_XX_0.<ext>` – draft slide images
* `slides.pdf` – combined PDF version
* `index.html` – simple viewer that shows all slides in order

You can limit to specific slides with:

```bash
python tools/generate_slides.py --yaml slides.yaml --style glass_garden --slides 
2 4 5
```

### 3. Upscale to 4K (optional)

Once you are happy with some drafts, upscale those images:

```bash
# Upscale all slides from the most recent run
python tools/generate_slides.py --enlarge

# Upscale specific slides from the most recent run
python tools/generate_slides.py --enlarge --slides 8 11

# Upscale slides from a specific run directory
python tools/generate_slides.py --enlarge --run-dir slides/20250101_120000
```

---

## Export to PowerPoint (image‑only)

If you have a script such as `tools/export_pptx.py`, you can wrap a run’s images 
into a PPTX where each image is a full‑screen slide and notes come from the 
YAML:

```bash
# 1) Generate slides as images
python tools/generate_slides.py --yaml slides.yaml --style modern_academic

# 2) Upscale if you want 4K (optional)
python tools/generate_slides.py --enlarge --run-dir slides/20250101_120000

# 3) Export to PPTX (image‑only slides)
python tools/export_pptx.py \
  --run-dir generated_slides/slides/20250101_120000 \
  --yaml slides.yaml \
  --use-4k \
  --output pptx/slides_modern_academic.pptx
```

If you do not need PowerPoint, you can present directly from the generated PDF 
or from the HTML viewer in the run directory.

---

## Setup

1. **Environment**

   ```bash
   uv venv  # any virtualenv tool is fine
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Credentials**

   Create a `.env` file with your API key:

   ```text
   GOOGLE_API_KEY=your_key_here
   ```

---

## Project layout

* `slides.yaml` – default outline file.
* `outlines/` – extra outline examples, for example 
`outlines/sample_talk_outline.md`.
* `styles/` – style packs (markdown descriptions).
* `imgs/` – style reference images and other assets.
* `prompts/outline_generator.md` – prompt for asking an LLM to generate YAML 
outlines.
* `AGENTS.md` – quick guide for agents using this repo.
* `speak_notes.md` – speaker notes for the demo talk.
* `tools/` – generation and upscaling scripts.
* `generated_slides/` – output from each run.
* `index.html` – Reveal.js talk about the project itself (not updated per run).
