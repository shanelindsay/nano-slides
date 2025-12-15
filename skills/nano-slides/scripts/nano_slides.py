#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO = Path(os.environ.get("NANO_SLIDES_REPO", "/home/sl/github/nano-slides")).expanduser()


def _repo_path(repo_arg: str | None) -> Path:
    repo = Path(repo_arg).expanduser() if repo_arg else DEFAULT_REPO
    return repo.resolve()


def _require_repo(repo: Path) -> None:
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo not found: {repo}")
    if not (repo / "tools" / "generate_slides.py").exists():
        raise SystemExit(f"Not a nano-slides repo (missing tools/generate_slides.py): {repo}")


def _uv_run(repo: Path, argv: list[str]) -> int:
    req = repo / "requirements.txt"
    if not req.exists():
        raise SystemExit(f"requirements.txt not found in repo: {repo}")

    cmd = [
        "uv",
        "run",
        "--no-project",
        "--with-requirements",
        str(req),
        *argv,
    ]
    return subprocess.call(cmd)


def _latest_run_dir(repo: Path) -> Path | None:
    base = repo / "generated_slides"
    if not base.exists():
        return None
    candidates = [p for p in base.rglob("slide_*_0.*")]
    if not candidates:
        return None
    latest_file = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest_file.parent


def cmd_generate(args: argparse.Namespace) -> int:
    repo = _repo_path(args.repo)
    _require_repo(repo)
    script = repo / "tools" / "generate_slides.py"

    argv = ["python", str(script)]
    if args.yaml:
        argv += ["--yaml", args.yaml]
    if args.style:
        argv += ["--style", args.style]
    if args.mode:
        argv += ["--mode", args.mode]
    if args.slides:
        argv += ["--slides", *[str(x) for x in args.slides]]

    rc = _uv_run(repo, argv)
    run_dir = _latest_run_dir(repo)
    if run_dir:
        print(f"Latest run: {run_dir}")
    return rc


def cmd_enlarge(args: argparse.Namespace) -> int:
    repo = _repo_path(args.repo)
    _require_repo(repo)
    script = repo / "tools" / "generate_slides.py"

    run_dir = args.run_dir
    if args.latest:
        latest = _latest_run_dir(repo)
        if not latest:
            print("No generated slides found under generated_slides/", file=sys.stderr)
            return 1
        run_dir = str(latest)

    argv = ["python", str(script), "--enlarge"]
    if run_dir:
        argv += ["--run-dir", run_dir]
    if args.slides:
        argv += ["--slides", *[str(x) for x in args.slides]]
    return _uv_run(repo, argv)


def cmd_export_pptx(args: argparse.Namespace) -> int:
    repo = _repo_path(args.repo)
    _require_repo(repo)
    script = repo / "tools" / "export_pptx.py"

    run_dir = args.run_dir
    if args.latest:
        latest = _latest_run_dir(repo)
        if not latest:
            print("No generated slides found under generated_slides/", file=sys.stderr)
            return 1
        run_dir = str(latest)
    if not run_dir:
        print("export-pptx requires --run-dir or --latest", file=sys.stderr)
        return 2

    argv = ["python", str(script), "--run-dir", run_dir]
    if args.yaml:
        argv += ["--yaml", args.yaml]
    if args.output:
        argv += ["--output", args.output]
    if args.use_4k:
        argv += ["--use-4k"]
    return _uv_run(repo, argv)


def cmd_make_style(args: argparse.Namespace) -> int:
    repo = _repo_path(args.repo)
    _require_repo(repo)
    script = repo / "tools" / "make_style.py"

    argv = ["python", str(script), "--name", args.name, "--description", args.description]
    return _uv_run(repo, argv)

def cmd_latest(args: argparse.Namespace) -> int:
    repo = _repo_path(args.repo)
    _require_repo(repo)
    latest = _latest_run_dir(repo)
    if not latest:
        print("No generated slides found under generated_slides/", file=sys.stderr)
        return 1
    print(latest)
    index_html = latest / "index.html"
    pdf = latest / "slides.pdf"
    if index_html.exists():
        print(index_html)
    if pdf.exists():
        print(pdf)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nano_slides.py",
        description="Thin wrapper around /home/sl/github/nano-slides tools (generation, 4K upscaling, PPTX export).",
    )
    parser.add_argument("--repo", default=None, help="Path to nano-slides repo (default: $NANO_SLIDES_REPO or /home/sl/github/nano-slides)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Generate draft slide images (and PDF/HTML viewer).")
    p_gen.add_argument("--yaml", default=None, help="Path to YAML outline file.")
    p_gen.add_argument("--style", default=None, help="Style pack name under styles/ or path to a style .md.")
    p_gen.add_argument("--mode", choices=["structured", "balanced", "expressive"], default=None)
    p_gen.add_argument("--slides", type=int, nargs="+", default=None)
    p_gen.set_defaults(func=cmd_generate)

    p_enl = sub.add_parser("enlarge", help="Upscale slides to 4K for a run directory.")
    p_enl.add_argument("--run-dir", default=None, help="Run directory path (or subdir under generated_slides/).")
    p_enl.add_argument("--latest", action="store_true", help="Use the most recent run under generated_slides/.")
    p_enl.add_argument("--slides", type=int, nargs="+", default=None)
    p_enl.set_defaults(func=cmd_enlarge)

    p_pptx = sub.add_parser("export-pptx", help="Export a run directory to an image-only PPTX.")
    p_pptx.add_argument("--run-dir", default=None, help="Run directory path (or subdir under generated_slides/).")
    p_pptx.add_argument("--latest", action="store_true", help="Use the most recent run under generated_slides/.")
    p_pptx.add_argument("--yaml", default=None, help="Optional YAML outline path for speaker notes.")
    p_pptx.add_argument("--output", default=None, help="Optional output PPTX path.")
    p_pptx.add_argument("--use-4k", action="store_true", help="Prefer 4K images if present.")
    p_pptx.set_defaults(func=cmd_export_pptx)

    p_style = sub.add_parser("make-style", help="Scaffold a new style pack and reference image placeholder.")
    p_style.add_argument("--name", required=True, help="New style name (e.g. minimal_grid).")
    p_style.add_argument("--description", required=True, help="One-line description of the style.")
    p_style.set_defaults(func=cmd_make_style)

    p_latest = sub.add_parser("latest", help="Print the most recent run directory (and common artefacts if present).")
    p_latest.set_defaults(func=cmd_latest)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
