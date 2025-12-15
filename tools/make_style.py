import argparse
import os
import sys
import subprocess
from pathlib import Path


STYLE_TEXT_PROMPT = """You are an expert slide designer.

Create a full style pack in Markdown for an image-model-driven slide renderer.
The style pack must be self-contained and written as clear instructions for an image model.

User description of the desired style:
{user_style}

Output requirements:
- Output only Markdown, no YAML, no code fences.
- Use this structure:
  1) Title line: "# Visual Design Language: <Style Name>"
  2) "**Role**" section (1–2 sentences)
  3) "**Philosophy**" section (2–4 sentences)
  4) "## 1. Core visual style" with Background / Colour / Typography subsections
  5) "## 2. Layout patterns" describing title, content, two_content, picture_with_caption, section_header, image_only
  6) "## 3. Assets" describing how to integrate logos/QR/photos
  7) "## 4. Execution rules" with 4–7 numbered rules
- Keep it concise but specific. Avoid mentioning any other existing styles by name.
"""


def generate_style_markdown(name: str, description: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY must be set to auto-generate a style pack.")

    try:
        from google import genai
    except Exception as e:
        raise RuntimeError("google-genai is not installed. Install requirements first.") from e

    model = os.environ.get("TEXT_MODEL", "gemini-2.0-flash")
    client = genai.Client(api_key=api_key)
    prompt = STYLE_TEXT_PROMPT.format(user_style=description)
    resp = client.models.generate_content(model=model, contents=prompt)
    text = getattr(resp, "text", None)
    if not text:
        # Fallback for SDK versions that store parts
        try:
            text = resp.candidates[0].content.parts[0].text
        except Exception:
            text = ""
    text = text.strip()
    if not text.startswith("# Visual Design Language"):
        # Ensure title line exists
        text = f"# Visual Design Language: {name}\n\n" + text
    return text


def write_style_file(project_root: Path, name: str, markdown_text: str) -> Path:
    styles_dir = project_root / "styles"
    styles_dir.mkdir(parents=True, exist_ok=True)
    path = styles_dir / f"{name}.md"
    path.write_text(markdown_text, encoding="utf-8")
    return path


def generate_reference_image(project_root: Path, name: str, style_text: str) -> None:
    imgs_dir = project_root / "imgs"
    imgs_dir.mkdir(parents=True, exist_ok=True)
    output_prefix = imgs_dir / f"style_ref_{name}"

    prompt = (
        "Generate a single reference slide that illustrates this visual style. "
        "Use a 16:9 layout with a clear title, a short bullet/idea list, and a small diagram or chart. "
        "Render everything in the described style.\n\n"
        "STYLE PACK:\n"
        f"{style_text}"
    )

    cmd = [
        sys.executable,
        str(project_root / "tools" / "gemini_generate_image.py"),
        "--prompt",
        prompt,
        "--output",
        str(output_prefix),
        "--size",
        "1K",
        "--aspect-ratio",
        "16:9",
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Create a new style pack and optional reference image.")
    parser.add_argument("--name", required=True, help="Style slug, e.g. minimal_grid")
    parser.add_argument("--description", required=True, help="Plain-English description of the style")
    parser.add_argument("--no-image", action="store_true", help="Only create styles/<name>.md, skip reference image")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    name = args.name.strip()
    if not name:
        print("Error: --name cannot be empty", file=sys.stderr)
        sys.exit(1)

    print(f"Generating style pack '{name}'...")
    try:
        style_md = generate_style_markdown(name, args.description)
    except Exception as e:
        print(f"Error generating style pack text: {e}", file=sys.stderr)
        sys.exit(1)

    style_path = write_style_file(project_root, name, style_md)
    print(f"Wrote style file: {style_path}")

    if not args.no_image:
        print("Generating style reference image...")
        try:
            generate_reference_image(project_root, name, style_md)
        except subprocess.CalledProcessError as e:
            print(f"Error generating reference image: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"Wrote reference image(s) under imgs/style_ref_{name}_0.*")


if __name__ == "__main__":
    main()

