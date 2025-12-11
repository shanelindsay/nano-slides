# Nano Banana Pro Slide Deck Generator (Fork)

This fork is a controllable slide renderer:
- You write the outline in Markdown.
- You pick a style pack from `styles/`.
- You can add per-slide style/layout hints.
- Gemini 3 Pro Image Preview renders the slides.

Original write-up for reference:
*   [中文版 (Chinese)](https://yage.ai/nano-banana-pro.html)
*   [English Version](https://yage.ai/nano-banana-pro-en.html)

## What’s different in this fork
- Styles live in `styles/` (clean_keynote, modern_academic, chalkboard, whiteboard_workshop, data_conference, editorial_magazine, glass_garden); choose with `--style` or point to a custom file.
- Outlines are YAML files (`slides.yaml` by default, or pass `--yaml`), with per-slide `type`, PowerPoint-like `layout`, `generate`, `title/subtitle`, `text` (bullets or columns), `visual`, `assets`, `style_ref`, `notes`, `image_only`. See `outlines/sample_talk_outline.md` or `slides.yaml`.
- Prompts are composed from the style pack + layout/type hints + your outline text. No automatic summarization or planning.


## Workflow (current fork)

### 1. Define the Context
Edit an outline (default: `slides.yaml` in the repo root, or pass `--yaml outlines/sample_talk_outline.md`). Preferred format is YAML documents separated by `---`:

```
---
slide: 2                          # explicit number
type: content                     # title | section | content | image_only | transition
style: glass_garden:default       # base style + optional variant
layout: two_content               # title_slide | title_and_content | two_content | comparison | picture_with_caption | section_header | blank
generate: true                    # optional; defaults to true

title: Background problem         # on-slide title
subtitle: The old world           # optional

text:                             # optional; omit for image-only
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
  Two-column composition: left shows fragmented assets; right shows a cohesive rendered scene.
  Emphasize contrast: chaos -> order.

assets:
  - imgs/style_anchor_glass_garden_0.jpg    # optional style anchor image

style_ref:
  - generated_slides/slide_01_0.jpg   # optional: reference images to enforce style consistency

notes: Optional speaker notes
image_only: false                    # optional; set true to minimize rendered text
---
```

### 2. Generate (Draft Mode)
Run the generator to create 1K previews. This is fast and cheap for iteration.
```bash
python tools/generate_slides.py --yaml slides.yaml --style glass_garden
```
This parses the outline, calls the Gemini 3 Pro Image Preview API, and saves images to `generated_slides/`.

By default it looks for `slides.yaml` in the repo root. If that does not exist, it falls back to `outlines/sample_slides.yaml`. You can point `--yaml` at any file. Each run writes to `generated_slides/<yaml-stem>/<timestamp>/` with:
- `slide_XX_0.<ext>` (1K drafts)
- `slides.pdf`
- `index.html` (simple viewer for that run)

Add your assets (e.g., `imgs/style_anchor_glass_garden_0.jpg` or `imgs/style_matrix_modern_academic_0.jpg`) if you want style anchoring; missing assets are skipped with a warning.

## Style preview

See `imgs/style_grid_reference_v3_0.jpg` for a 2x4 grid illustrating styles 
(Cinematic Darkroom, Research Notebook, Playful Infographic, Minimal Grid, 
Minimal Monochrome, Dark Terminal, Research Poster, Sticky Note Workshop).

Sample reference slides (usable as style anchors):
- Modern Academic: `imgs/style_ref_modern_academic_0.jpg`
- Dark Terminal: `imgs/style_ref_dark_terminal_0.jpg`

### 3. Refine & Upscale (Production Mode)
Once specific slides are approved, upscale them to 4K resolution using the generative upscaler.
```bash
# Upscale every slide from the most recent run
python tools/generate_slides.py --enlarge

# Upscale specific slides from the most recent run
python tools/generate_slides.py --enlarge --slides 8 11

# Upscale slides from a specific run directory under generated_slides/
python tools/generate_slides.py --enlarge --run-dir slides/20250101_120000
```

### 4. Present
To review a generated deck, open the `index.html` inside the run directory, for example:

`generated_slides/slides/20250101_120000/index.html`

This is a simple viewer that lists each slide image in order.

The root `index.html` in this repo is a Reveal.js talk about the project itself; it is not automatically updated for each generation run.

## Export to PowerPoint (image-only)
Wrap a run’s images into a PPTX (each image is a full-screen slide; notes come from your YAML).
```bash
# 1) Generate slides as images
python tools/generate_slides.py --yaml slides.yaml --style modern_academic

# 2) Upscale if you want 4K (optional)
python tools/generate_slides.py --enlarge --run-dir slides/20250101_120000

# 3) Export to PPTX (uses run images; attaches notes from YAML if provided)
python tools/export_pptx.py \
  --run-dir generated_slides/slides/20250101_120000 \
  --yaml slides.yaml \
  --use-4k \
  --output pptx/slides_modern_academic.pptx
```

## Setup

1.  **Environment**:
    ```bash
    uv venv  # using uv is recommended
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Credentials**:
    Create a `.env` file with your API key:
    ```
    GOOGLE_API_KEY=your_key_here
    ```

## Project Structure

*   `outlines/`: Outline files (sample: `outlines/sample_talk_outline.md`).
*   `styles/`: Style packs (clean_keynote, modern_academic, chalkboard, whiteboard_workshop, data_conference, editorial_magazine, glass_garden, minimal_monochrome, dark_terminal, research_poster, notebook_paper, sticky_note_workshop, systems_blueprint, cinematic_darkroom, research_notebook, playful_infographic, minimal_grid).
*   `prompts/outline_generator.md`: Prompt for an LLM to emit outlines in the YAML format.
*   `AGENTS.md`: Quick guide for agents using this repo.
*   `speak_notes.md`: The script for the presentation.
*   `tools/`: Python scripts for generation and upscaling.
    *   `generate_slides.py`: Main orchestrator.
    *   `gemini_generate_image.py`: API wrapper for generation.
    *   `gemini_enlarge_image.py`: API wrapper for upscaling.
*   `generated_slides/`: The render targets.
*   `index.html`: The viewer.
