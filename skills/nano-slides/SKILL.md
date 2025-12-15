---
name: nano-slides
description: Generate slide decks as images (plus PDF/HTML viewer, optional PPTX) using the local nano-slides repo (Gemini 3 Pro Image). Use when the user wants to turn a YAML slide outline into a styled deck, upscale slides to 4K, export image-only PPTX, or scaffold a new style pack.
---

# Nano Slides

Generate presentation decks as rendered slide images using the `nano-slides` project in `/home/sl/github/nano-slides`.

## Quick Start

Generate draft slides (1K):
```bash
python ~/.codex/skills/nano-slides/scripts/nano_slides.py generate --yaml slides.yaml --style modern_academic --mode balanced
```

Upscale the latest run to 4K:
```bash
python ~/.codex/skills/nano-slides/scripts/nano_slides.py enlarge --latest
```

Show the most recent run directory:
```bash
python ~/.codex/skills/nano-slides/scripts/nano_slides.py latest
```

Export the latest run to PPTX (image-only):
```bash
python ~/.codex/skills/nano-slides/scripts/nano_slides.py export-pptx --latest --yaml slides.yaml --use-4k
```

## Inputs

- `--yaml`: Path to your multi-document YAML outline (slides separated by `---`).
- `--style`: Style pack name under `styles/` (e.g. `modern_academic`, `chalkboard`) or a path to a style `.md`.
- `--mode`: `structured | balanced | expressive`.
- `--slides`: Optional list of slide numbers to render / upscale.

## Outputs

Generation writes into the repo under:

`/home/sl/github/nano-slides/generated_slides/<yaml-stem>/<timestamp>/`

Each run typically includes:
- `slide_XX_0.*` (draft images)
- `slides.pdf`
- `index.html` (simple viewer)

## API Key / Credentials

The underlying scripts load `/home/sl/github/nano-slides/.env` automatically. Ensure it contains `GOOGLE_API_KEY=...` (or set `GEMINI_API_KEY` / `GOOGLE_API_KEY` in your environment).

Do not edit `.env` via the agent; only you should change it.
