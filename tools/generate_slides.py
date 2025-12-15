import argparse
import sys
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import yaml
from PIL import Image

# Import gemini_generate_image from the same directory
import gemini_generate_image


def load_style(style_name: str, project_root: Path) -> str:
    """
    Load a style pack by name or path.
    - If style_name points to an existing file, use it.
    - Otherwise look under styles/<style_name>.md.
    """
    styles_dir = project_root / "styles"

    candidate_path = Path(style_name)
    if candidate_path.exists():
        return candidate_path.read_text(encoding="utf-8")

    named_style = styles_dir / f"{style_name}.md"
    if named_style.exists():
        return named_style.read_text(encoding="utf-8")

    raise FileNotFoundError(f"Style '{style_name}' not found at {named_style}")

def find_style_reference(base_style: str, project_root: Path):
    """
    Find a default style reference image for the given base style.
    Looks for imgs/style_ref_<base_style>*.{jpg,png,jpeg,webp} or style_anchor/style_matrix variants for glass_garden.
    Returns a Path or None.
    """
    imgs_dir = project_root / "imgs"
    exts = ["jpg", "jpeg", "png", "webp"]
    candidates = []
    for ext in exts:
        candidates.append(imgs_dir / f"style_ref_{base_style}_0.{ext}")
        candidates.append(imgs_dir / f"style_ref_{base_style}.{ext}")
    if base_style == "glass_garden":
        for name in ["style_anchor_glass_garden_0", "style_matrix_glass_garden_0", "style_matrix_glass_garden"]:
            for ext in exts:
                candidates.append(imgs_dir / f"{name}.{ext}")
    if base_style == "modern_academic":
        for name in ["style_matrix_modern_academic_0", "style_matrix_modern_academic"]:
            for ext in exts:
                candidates.append(imgs_dir / f"{name}.{ext}")
    for path in candidates:
        if path.exists():
            return path
    return None

def _format_text_block(text_field, mode: str = "balanced") -> str:
    """
    Normalize text content from YAML to a simple string block.
    Supports dict with heading/subtitle/body/bullets or plain string. Also supports columns.
    The wording changes slightly depending on mode: in non-structured modes we talk about "ideas" rather than "bullets".
    """
    if text_field is None:
        return ""
    if isinstance(text_field, str):
        return text_field.strip()
    if not isinstance(text_field, dict):
        return ""

    structured = (mode == "structured")
    bullet_label = "Bullets" if structured else "Key ideas"
    bullet_prefix = "-" if structured else "•"

    # Columns support
    if "columns" in text_field:
        cols = text_field.get("columns") or []
        lines = ["Two-column structure:" if structured else "Two groups of key ideas (for example left and right regions on the slide):"]
        for idx, col in enumerate(cols, start=1):
            heading = col.get("heading") or col.get("title") or f"Column {idx}"
            bullets = col.get("bullets") or []
            if structured:
                lines.append(f"Column {idx} heading: {heading}")
                if bullets:
                    lines.append("  Bullets:")
                    for b in bullets:
                        lines.append(f"  - {b}")
            else:
                lines.append(f"Group {idx} label: {heading}")
                if bullets:
                    lines.append("  Key ideas:")
                    for b in bullets:
                        lines.append(f"  {bullet_prefix} {b}")
        return "\n".join(lines).strip()

    lines = []
    heading = text_field.get("heading") or text_field.get("subtitle") or text_field.get("title")
    if heading:
        lines.append(f"Heading: {heading}" if structured else f"Key idea label: {heading}")
    body = text_field.get("body")
    if body:
        lines.append(f"Body: {body}")
    bullets = text_field.get("bullets") or []
    if bullets:
        lines.append(f"{bullet_label}:")
        for b in bullets:
            lines.append(f"{bullet_prefix} {b}")
    return "\n".join(lines).strip()


def _parse_yaml_outline(outline_path, specific_slides=None, mode: str = "balanced"):
    """
    Parse YAML-style outline: multi-doc separated by ---.
    """
    with open(outline_path, 'r', encoding='utf-8') as f:
        content = f.read()

    slides = []
    raw_docs = list(yaml.safe_load_all(content))
    index = 0
    for doc in raw_docs:
        if not doc:
            continue
        index += 1
        slide_num = doc.get("slide", index)
        if specific_slides and slide_num not in specific_slides:
            continue

        generate_flag = doc.get("generate", True)
        if not generate_flag:
            continue

        style_value = doc.get("style")
        layout_value = (doc.get("layout") or "full").lower()
        visual = doc.get("visual", "") or ""
        notes = doc.get("notes", "") or ""
        image_only = bool(doc.get("image_only", False))

        assets_field = doc.get("assets") or []
        if isinstance(assets_field, str):
            assets = [assets_field]
        elif isinstance(assets_field, list):
            assets = assets_field
        else:
            assets = []

        style_ref_field = doc.get("style_ref") or []
        if isinstance(style_ref_field, str):
            style_refs = [style_ref_field]
        elif isinstance(style_ref_field, list):
            style_refs = style_ref_field
        else:
            style_refs = []

        text_block = _format_text_block(doc.get("text"), mode=mode)

        content_dump = yaml.safe_dump(doc, sort_keys=False)

        slides.append({
            'number': slide_num,
            'title': doc.get("title", f"Slide {slide_num}"),
            'subtitle': doc.get("subtitle", ""),
            'content': content_dump,
            'asset_paths': assets,
            'style_refs': style_refs,
            'style': style_value,
            'layout': layout_value,
            'text': text_block,
            'text_raw': doc.get("text") or {},
            'visual': visual.strip(),
            'notes': notes.strip(),
            'image_only': image_only,
            'type': doc.get("type", "content"),
        })
    return slides


def parse_slides(outline_path, start_slide=1, end_slide=None, specific_slides=None, mode: str = "balanced"):
    return _parse_yaml_outline(outline_path, specific_slides=specific_slides, mode=mode)


def _layout_hint(layout: str) -> str:
    layout = (layout or "full").lower()
    ppt_layouts = {
        "title_slide": "Title slide: big title (and optional subtitle), minimal other content.",
        "title_and_content": "Title at the top, single main content area beneath it.",
        "two_content": "Two content columns side by side, left and right, each with its own heading and bullets.",
        "comparison": "Two columns for side-by-side comparison, with clear headings for each column.",
        "picture_with_caption": "Main picture on one side, text/caption on the other side.",
        "section_header": "Section divider slide with prominent title.",
        "blank": "Flexible canvas; choose any composition that fits.",
    }
    if layout in ppt_layouts:
        return ppt_layouts[layout]

    # Legacy mappings for convenience
    if layout == "split-right":
        return "Place the main visual composition on the RIGHT half; leave the LEFT calmer for text overlay."
    if layout == "split-left":
        return "Place the main visual composition on the LEFT half; leave the RIGHT calmer for text overlay."
    if layout == "title":
        return "Title/hero slide: strong central focus on the title area with minimal clutter."
    if layout == "loose":
        return "You may choose any layout that best communicates the concept; favor expressive composition."
    return "Use a full-frame 16:9 composition suitable as a standalone slide background."


def _variant_hint(variant: str) -> str:
    if variant == "title":
        return "Emphasize the main title; treat this as an opener/hero slide."
    if variant == "visual":
        return "Minimize rendered text; let imagery carry most of the meaning."
    return ""


def generate_slide(slide, style_text, style_pack_name, output_dir, project_root, mode, global_style_refs):
    print(f"Starting generation for Slide {slide['number']}...")

    # Pack comes from CLI; slide-level style is treated as a variant only.
    # Pack comes from CLI/deck; slide-level style is treated as a variant only.
    raw_variant = slide.get('style')
    variant = None
    if raw_variant:
        raw_variant = str(raw_variant)
        if ":" in raw_variant:
            # Backward compatibility: allow pack:variant but ignore the pack part.
            _, variant = raw_variant.split(":", 1)
        else:
            variant = raw_variant

    slide_title = slide.get('title') or f"Slide {slide['number']}"
    layout = slide.get('layout', "full")
    layout_hint = _layout_hint(layout)
    variant_hint = _variant_hint(variant)

    type_hint_map = {
        "title": "This is a title slide. Emphasize the main title with minimal clutter.",
        "section": "This is a section divider slide. Highlight the section title.",
        "content": "This is a standard content slide.",
        "image_only": "This is an image-only slide; minimize rendered text.",
        "transition": "This is a transitional slide; keep it simple and light.",
    }
    type_hint = type_hint_map.get(slide.get("type", "content"), "Standard content slide.")

    prompt_parts = [
        "You render full 16:9 presentation slide images.",
        "Render the slide in the same medium as the provided style reference; match its texture, palette, and typography. Do not introduce a different rendering style.",
        "",
        "GLOBAL VISUAL STYLE (must follow for all slides in this deck):",
        style_text,
        "",
        "STYLE PACK:",
        f"- Style pack: {style_pack_name}",
    ]

    # Build list of style refs (explicit or global) and assets
    style_refs = list(slide.get("style_refs") or global_style_refs or [])

    if style_refs:
        prompt_parts.append("STYLE REFERENCES: Use these as visual anchors for color/typography/layout. Maintain consistency with them.")
        prompt_parts.append(", ".join([Path(ref).name for ref in style_refs]))
        prompt_parts.append("STRICT: Match the medium/texture of the reference (no photorealism if the reference is chalk/ink/flat). Redraw everything in that style and avoid introducing a different rendering style.")

    if mode == "structured":
        prompt_parts.append("\nGLOBAL TONE: Structured. Prioritise clear, literal layouts; if bullets are present, organise them cleanly. Avoid overly decorative visuals.")
    elif mode == "expressive":
        prompt_parts.append("\nGLOBAL TONE: Expressive. You may replace plain bullet lists with more visual structures (diagrams, labelled arrows, cards) so long as the information content is preserved.")
    else:
        prompt_parts.append("\nGLOBAL TONE: Balanced. Mix clear structure with some expressive visual design, without letting decoration overpower legibility.")

    prompt_parts.extend(
        [
            "",
            "SLIDE ROLE & LAYOUT:",
            f"- Type: {type_hint}",
            f"- Layout: {layout}",
            f"- Layout hint: {layout_hint}",
            f"- Variant: {variant or 'default'}",
            f"- Variant hint: {variant_hint}",
        ]
    )

    # Structured outline pieces (style-neutral)
    text_block = slide.get("text")
    text_lines = []
    if text_block:
        if mode == "structured":
            text_lines.append(
                "STRUCTURED TEXT (these bullets should appear clearly on-slide, usually as bullet lists or short labelled blocks):"
            )
        else:
            text_lines.append(
                "CONTENT IDEAS (preserve the meaning of these points; you may present them as diagrams, flows, or labelled regions rather than literal bullet lists):"
            )
        if slide_title:
            text_lines.append(f"- Title: {slide_title}")
        subtitle = slide.get("subtitle", "")
        if subtitle:
            text_lines.append(f"- Subtitle: {subtitle}")

        # Render bullets or columns
        if isinstance(text_block, dict) and text_block.get("columns"):
            text_lines.append("- Columns:")
            for idx, col in enumerate(text_block.get("columns"), start=1):
                heading = col.get("heading") or f"Column {idx}"
                text_lines.append(f"  - {heading}:")
                for b in col.get("bullets", []):
                    text_lines.append(f"    - {b}")
        elif isinstance(text_block, dict) and text_block.get("bullets"):
            text_lines.append("- Bullets:")
            for b in text_block.get("bullets", []):
                text_lines.append(f"  - {b}")
        else:
            text_lines.append(_format_text_block(text_block))

    visual = slide.get("visual")
    if visual:
        text_lines.append("")
        text_lines.append("VISUAL GUIDANCE (style-neutral; interpret via style pack):")
        text_lines.append(visual)

    notes = slide.get("notes")
    if notes:
        text_lines.append("")
        text_lines.append("NOTES (speaker context; optional):")
        text_lines.append(notes)

    if slide.get("image_only"):
        text_lines.append("")
        text_lines.append("IMAGE-ONLY: Minimize rendered text; focus on the visual.")

    if text_lines:
        prompt_parts.append("")
        prompt_parts.extend(text_lines)

    prompt_parts.append(
        "\nTASK:\nGenerate a high-resolution, 16:9 slide image that reflects the outline while strictly following the style and layout guidance above.\nIf reference assets are provided, incorporate them naturally into the design."
    )

    prompt = "\n".join(prompt_parts)

    image_inputs = []
    combined_inputs = []
    if style_refs:
        combined_inputs.extend(style_refs)
    if slide.get('asset_paths'):
        combined_inputs.extend(slide['asset_paths'])

    if combined_inputs:
        for path_str in combined_inputs:
            if not os.path.isabs(path_str):
                asset_path = project_root / path_str
            else:
                asset_path = Path(path_str)

            if asset_path.exists():
                print(f"  Using asset: {asset_path}")
                prompt += f"\nNOTE: Incorporate the provided reference image ({asset_path.name}) into the design as described."
                image_inputs.append(str(asset_path))
            else:
                print(f"  WARNING: Asset file not found at {asset_path}. Skipping this asset.")

    output_filename = os.path.join(str(output_dir), f"slide_{slide['number']:02d}")

    try:
        gemini_generate_image.generate(
            prompt=prompt,
            image_paths=image_inputs if image_inputs else None,
            output_prefix=output_filename,
            image_size="1K",
            aspect_ratio="16:9"
        )
        print(f"Finished Slide {slide['number']}")
    except Exception as e:
        print(f"Error generating Slide {slide['number']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate slides")
    parser.add_argument("--enlarge", action="store_true", help="Enlarge existing slides to 4K")
    parser.add_argument("--slides", type=int, nargs="+", help="Specific slide numbers to process (e.g., --slides 8 11)")
    parser.add_argument("--yaml", type=str, default=None, help="Path to YAML slides file (overrides deck.yaml if provided)")
    parser.add_argument("--run-dir", type=str, default=None, help="Output subdirectory under generated_slides/ (required for --enlarge; ignored for generation).")
    parser.add_argument(
        "--style",
        type=str,
        default=None,
        help="Optional override for deck.yaml style_pack. Style name (styles/<name>.md) or path to style file.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        choices=["structured", "balanced", "expressive"],
        help="Optional override for deck.yaml mode. Controls how literally bullets vs ideas are rendered.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Prefer deck.yaml if present for defaults
    deck_cfg_path = project_root / "deck.yaml"
    deck_cfg = {}
    if deck_cfg_path.exists():
        try:
            deck_cfg = yaml.safe_load(deck_cfg_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"Warning: failed to parse deck.yaml: {e}", file=sys.stderr)
            deck_cfg = {}

    # Resolve outline path: CLI > deck.yaml > root slides.yaml > sample
    if args.yaml:
        outline_path = Path(args.yaml)
    else:
        yaml_from_deck = deck_cfg.get("yaml")
        if yaml_from_deck:
            outline_path = Path(yaml_from_deck)
            if not outline_path.is_absolute():
                outline_path = project_root / yaml_from_deck
        else:
            root_yaml = project_root / "slides.yaml"
            sample_yaml = project_root / "outlines" / "sample_slides.yaml"
            outline_path = root_yaml if root_yaml.exists() else sample_yaml
    base_output = project_root / "generated_slides"

    if args.enlarge:
        import glob
        import subprocess
        if args.run_dir:
            output_dir = Path(args.run_dir)
            if not output_dir.is_absolute():
                output_dir = base_output / args.run_dir
        else:
            if not base_output.exists():
                print("Error: generated_slides/ not found. Run generation first or pass --run-dir.", file=sys.stderr)
                sys.exit(1)
            candidates = list(base_output.rglob("slide_*_0.*"))
            if not candidates:
                print("Error: no slides found under generated_slides/. Run generation first or pass --run-dir.", file=sys.stderr)
                sys.exit(1)
            latest_file = max(candidates, key=lambda p: p.stat().st_mtime)
            output_dir = latest_file.parent
            print(f"No --run-dir provided. Using latest run directory: {output_dir}")

        if not output_dir.exists():
            print(f"Error: run directory not found: {output_dir}", file=sys.stderr)
            sys.exit(1)

        print("Starting batch enlargement...")
        slide_pattern = str(output_dir / "slide_*_0.*")
        files = glob.glob(slide_pattern)

        if args.slides:
            filtered_files = []
            for f in files:
                match = re.search(r'slide_(\d+)_0\.', f)
                if match:
                    num = int(match.group(1))
                    if num in args.slides:
                        filtered_files.append(f)
            files = filtered_files

        print(f"Found {len(files)} slides to enlarge.")

        for file_path in sorted(files):
            file_path_obj = Path(file_path)
            output_name = file_path_obj.stem + "_4k" + file_path_obj.suffix
            output_path = output_dir / output_name

            print(f"Enlarging {file_path_obj.name} -> {output_name}...")

            enlarge_script = script_dir / "gemini_enlarge_image.py"
            cmd = [sys.executable, str(enlarge_script), "--input", str(file_path), "--output", str(output_path)]

            try:
                subprocess.run(cmd, check=True)
                print(f"Finished {output_name}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to enlarge {file_path_obj.name}: {e}")

        print("Batch enlargement complete.")
        return

    # Generation mode: always create a fresh run directory <yaml-stem>/<timestamp>
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yaml_stem = outline_path.stem
    output_dir = base_output / yaml_stem / stamp

    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve style pack and mode: CLI > deck.yaml > defaults
    style_pack_name = args.style or deck_cfg.get("style_pack") or "glass_garden"
    mode = args.mode or deck_cfg.get("mode") or "balanced"

    style_text = load_style(style_pack_name, project_root)

    # Derive base style name (for auto style refs) from CLI/deck style arg
    style_path = Path(style_pack_name)
    if style_path.is_file():
        base_style_name = style_path.stem
    else:
        base_style_name = style_path.name

    # Find a matching style reference image, if any
    auto_style_refs = []
    auto_ref = find_style_reference(base_style_name, project_root)
    if auto_ref:
        auto_style_refs.append(str(auto_ref))

    specific_slides = args.slides if args.slides else None
    if not specific_slides:
        slides = parse_slides(str(outline_path), mode=mode)
    else:
        slides = parse_slides(str(outline_path), specific_slides=specific_slides, mode=mode)

    print(f"Found {len(slides)} slides to generate.")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                generate_slide,
                slide,
                style_text,
                base_style_name,
                output_dir,
                project_root,
                mode,
                auto_style_refs,
            )
            for slide in slides
        ]
        for future in futures:
            future.result()

    # Collect generated images in order and build artifacts
    slide_paths = []
    for slide in sorted(slides, key=lambda s: s.get("number", 0)):
        num = slide.get("number", 0)
        pattern = f"slide_{num:02d}_0.*"
        matches = list(output_dir.glob(pattern))
        if matches:
            slide_paths.append(sorted(matches)[0])

    if slide_paths:
        # Save PDF
        pdf_path = output_dir / "slides.pdf"
        try:
            imgs = []
            for p in slide_paths:
                with Image.open(p) as im:
                    if im.mode in ("RGBA", "P"):
                        im = im.convert("RGB")
                    imgs.append(im.copy())
            if imgs:
                imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:])
                print(f"Saved PDF: {pdf_path}")
        except Exception as e:
            print(f"Warning: failed to build PDF: {e}")

        # Write simple HTML index for this run
        index_path = output_dir / "index.html"
        lines = [
            "<!doctype html>",
            "<html><head><meta charset='utf-8'><title>Slides</title>",
            "<style>body{font-family:sans-serif;background:#f7f7f7;color:#222;margin:24px;} .slide{margin-bottom:32px;} img{max-width:100%;height:auto;}</style>",
            "</head><body>",
            f"<h1>Slides ({len(slide_paths)})</h1>",
            f"<p>Output directory: {output_dir}</p>",
        ]
        for p in slide_paths:
            name = p.name
            lines.append("<div class='slide'>")
            lines.append(f"<h3>{name}</h3>")
            lines.append(f"<img src='{name}' alt='{name}' />")
            lines.append("</div>")
        lines.append("</body></html>")
        index_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote index: {index_path}")


if __name__ == "__main__":
    main()
