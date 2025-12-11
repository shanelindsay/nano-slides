# Agent Guide: Rendering Slides with nano-slides

This fork renders full slide images from YAML outlines using Gemini 3 Pro Image Preview. The goal: keep humans in control of structure/style, let the model render cohesive scenes.

## Files & Inputs
- `slides.yaml` (or any `--yaml`): multiple YAML docs (`---` separated), each a slide.
  - `slide`: number (for sanity)
  - `type`: title | section | content | image_only | transition
  - `layout`: title_slide | title_and_content | two_content | comparison | picture_with_caption | section_header | blank (hints only)
  - `style`: style pack name with optional variant (e.g., `glass_garden:default`)
  - `generate`: true/false (skip placeholders)
  - `title`, `subtitle`
  - `text`: either `bullets: [...]` or `columns: [{heading, bullets}, ...]`
  - `visual`: art direction paragraph
  - `assets`: list of image paths to inject
  - `style_ref`: optional reference images to enforce consistency
  - `notes`: speaker notes
  - `image_only`: boolean to minimize rendered text
- `styles/`: style packs (`glass_garden.md` default). No `visual_guideline.md`.
- `prompts/outline_generator.md`: prompt to ask an LLM to emit YAML outlines in this schema.

## Commands
- Draft (1K): `python tools/generate_slides.py --yaml slides.yaml --style glass_garden`
- Upscale to 4K: `python tools/generate_slides.py --enlarge`
- Select slides: `--slides 2 4`
- Outputs land in `generated_slides/<yaml-stem>/<timestamp>/` with `slide_XX_0.jpg`, `slides.pdf`, and a per-run `index.html`.

## Quick startup checklist
- Style pack present? (`styles/<name>.md`). If not, create one (copy/edit `glass_garden.md`).
- Outline ready? (`slides.yaml` or `--yaml <file>`). Ensure `generate: true` on slides you want.
- Assets in place? Paths in `assets/style_ref` resolve relative to repo root.
- Optional style anchor: keep a style reference image (e.g., `imgs/style_anchor_glass_garden_0.jpg`) and list it in `assets`/`style_ref` to harden consistency.

## Prompt Composition (what the model sees)
- Global style text from the chosen style pack.
- Role hint from `type`.
- Layout hint mapped from `layout` to natural language (e.g., “Two content columns side by side…”).
- Title/subtitle.
- Text structure description (single bullets or per-column headings/bullets).
- Visual description.
- Style refs + assets sent as image parts; referenced explicitly in the prompt.

## Agent Playbook
1) Outline
   - Use the YAML schema above; prefer `layout` names that mirror PowerPoint masters.
   - For two sets of bullets, use `text.columns` with headings.
   - For image-heavy slides, set `type: image_only` or `image_only: true` and keep `text` empty.
   - Add `style_ref` if you want to lock in an existing look; list reference images.
2) Style
   - Choose a style pack (`styles/<name>.md`); variants via `style: name:variant`.
   - Add more packs by dropping Markdown files into `styles/`.
3) Assets
   - Place images relative to repo root; list them under `assets`.
   - The model integrates them; no hard placement—describe intent in `visual`.
4) Generate
   - Run draft generation; review `generated_slides/slide_XX_0.jpg`.
   - Upscale approved slides with `--enlarge` (produces `_4k` variants).
5) If results drift
   - Strengthen `visual` and layout hints.
   - Add/update `style_ref`.
   - Simplify text if the model hallucinates text; consider `image_only` then overlay text externally.
   - Reuse a consistent anchor image (style reference) in `style_ref`.

## Troubleshooting
- Missing style file: ensure `styles/<base>.md` exists or pass `--style` pointing to a file.
- Assets not found: check paths in YAML; they are resolved relative to repo root unless absolute.
- Inconsistent style: add a good `style_ref` and mention it; keep style pack concise and directive.
- Text garbling: reduce embedded text expectations; use `image_only` and overlay later if needed.
