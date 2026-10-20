#!/usr/bin/env python3
"""Build an RZCN program identification PDF from concatenated source text."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pymupdf


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrap_line(line: str, width: int) -> list[str]:
    line = line.replace("㍿", "U+337F")
    if len(line) <= width:
        return [line]
    chunks = [line[i : i + width] for i in range(0, len(line), width)]
    return [chunks[0]] + ["    " + chunk for chunk in chunks[1:]]


def load_visual_lines(path: Path, wrap_width: int) -> list[str]:
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("source text is empty")
    return [part for line in lines for part in wrap_line(line, wrap_width)]


def select_lines(
    visual: list[str],
    mode: str,
    page_lines: int,
    front_pages: int,
    back_pages: int,
) -> tuple[list[str], str, bool]:
    full_pages = math.ceil(len(visual) / page_lines)
    if mode == "auto":
        mode = "front-back" if full_pages >= front_pages + back_pages else "full"
    if mode == "full":
        selected = visual
        partial = len(selected) % page_lines != 0
        return selected, mode, partial
    if mode != "front-back":
        raise RuntimeError(f"unsupported mode: {mode}")
    need = (front_pages + back_pages) * page_lines
    if len(visual) < need:
        raise RuntimeError(f"front-back mode needs at least {need} visual lines, got {len(visual)}")
    selected = visual[: front_pages * page_lines] + visual[-back_pages * page_lines :]
    return selected, mode, False


def draw_header(page: pymupdf.Page, number: int, total_pages: int, software: str, version: str) -> None:
    page.insert_text((28, 18), f"{software} {version}", fontname="china-s", fontsize=9)
    page.insert_text((445, 18), f"第 {number} 页 / 共 {total_pages} 页", fontname="china-s", fontsize=9)
    page.draw_line((28, 23), (567, 23), color=(0.72, 0.72, 0.72), width=0.35)


def draw_footer(page: pymupdf.Page, marker: str, page_lines: int, source_lines: int | None) -> None:
    total = f"    源码总量 {source_lines} 行" if source_lines else ""
    page.insert_text((28, 830), f"{marker}    每页至少 {page_lines} 行{total}", fontname="china-s", fontsize=8)


def build_pdf(args: argparse.Namespace) -> dict:
    visual = load_visual_lines(args.source_text, args.wrap_width)
    selected, mode, partial = select_lines(
        visual,
        args.mode,
        args.page_lines,
        args.front_pages,
        args.back_pages,
    )
    pages = math.ceil(len(selected) / args.page_lines)
    if pages > 60:
        raise RuntimeError(f"selected material has {pages} pages, exceeds 60")
    if partial and not args.allow_partial_last_page:
        raise RuntimeError("full-source mode has a partial last page; pass --allow-partial-last-page after checking current platform rules")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open()
    doc.set_metadata(
        {
            "title": f"{args.software} {args.version} 程序鉴别材料",
            "author": args.software,
            "subject": "计算机软件著作权登记程序鉴别材料",
            "creator": args.software,
            "producer": args.software,
        }
    )

    source_total = args.source_lines
    for page_index in range(pages):
        page = doc.new_page(width=595, height=842)
        draw_header(page, page_index + 1, pages, args.software, args.version)
        y = 39
        for line in selected[page_index * args.page_lines : (page_index + 1) * args.page_lines]:
            page.insert_text((28, y), line, fontname="china-s", fontsize=args.font_size)
            y += args.line_height
        marker = "完整源程序"
        if mode == "front-back":
            marker = "连续前30页" if page_index < args.front_pages else "连续后30页"
        draw_footer(page, marker, args.page_lines, source_total)
    doc.save(args.output, garbage=4, deflate=True)
    doc.close()

    result = {
        "output": str(args.output),
        "software": args.software,
        "version": args.version,
        "mode": mode,
        "pages": pages,
        "page_lines": args.page_lines,
        "partial_last_page": partial,
        "visual_source_lines": len(visual),
        "selected_display_lines": len(selected),
        "sha256": sha256(args.output),
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-text", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--software", required=True)
    parser.add_argument("--version", default="V1.0")
    parser.add_argument("--mode", choices=["auto", "full", "front-back"], default="auto")
    parser.add_argument("--page-lines", type=int, default=50)
    parser.add_argument("--front-pages", type=int, default=30)
    parser.add_argument("--back-pages", type=int, default=30)
    parser.add_argument("--wrap-width", type=int, default=72)
    parser.add_argument("--font-size", type=float, default=6.2)
    parser.add_argument("--line-height", type=float, default=15.1)
    parser.add_argument("--source-lines", type=int)
    parser.add_argument("--allow-partial-last-page", action="store_true")
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_pdf(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
