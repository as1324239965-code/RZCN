#!/usr/bin/env python3
"""Audit an RZCN filing package and fail on material inconsistencies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import pymupdf

AUTOMATION_RE = re.compile(
    r"(?<![A-Za-z])(AI|ChatGPT|Codex|GPT|Claude|OpenAI|Anthropic|LLM|DeepSeek|Gemini|Copilot|工作流)(?![A-Za-z])"
    r"|人工智能|智能体|大模型|模型生成|自动生成|提示词|生成式",
    re.I,
)
SECRET_RE = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|"
    r"\b1[3-9]\d{9}\b|"
    r"postgresql://|"
    r"redis://|"
    r"BEGIN (?:RSA|OPENSSH|PRIVATE)|"
    r"root@|"
    r"password\s*=|"
    r"secret\s*=|"
    r"access[_-]?key\s*=|"
    r"admin[_-]?key\s*=",
    re.I,
)
URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.I)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrapped(line: str, width: int) -> list[str]:
    line = line.replace("㍿", "U+337F")
    if len(line) <= width:
        return [line]
    chunks = [line[i : i + width] for i in range(0, len(line), width)]
    return [chunks[0]] + ["    " + chunk for chunk in chunks[1:]]


def normalize(line: str) -> str:
    return re.sub(r"\s+", " ", line.replace("⋯", "…")).strip()


def outside_spans(page: pymupdf.Page) -> int:
    spans = [
        span
        for block in page.get_text("dict")["blocks"]
        if block.get("type") == 0
        for line in block["lines"]
        for span in line["spans"]
    ]
    return sum(
        span["bbox"][0] < 0
        or span["bbox"][2] > page.rect.width
        or span["bbox"][1] < 0
        or span["bbox"][3] > page.rect.height
        for span in spans
    )


def text_rows(page: pymupdf.Page, tolerance: float = 2.5) -> int:
    values = sorted(
        line["bbox"][1]
        for block in page.get_text("dict")["blocks"]
        if block.get("type") == 0
        for line in block["lines"]
    )
    rows = 0
    previous = None
    for value in values:
        if previous is None or value - previous > tolerance:
            rows += 1
        previous = value
    return rows


def sensitive_hits(text: str) -> list[str]:
    hits = {match.group(0) for match in SECRET_RE.finditer(text)}
    for match in URL_RE.finditer(text):
        host = urlparse(match.group(0)).hostname or ""
        allowed = host in {"localhost", "example.com", "example.invalid", "host"}
        if host and not allowed and not host.startswith("<"):
            hits.add(match.group(0))
    return sorted(hits)


def pdf_info(
    path: Path,
    software: str,
    version: str,
    is_program: bool,
    lines_per_page: int,
) -> tuple[dict, list[str], list[str]]:
    doc = pymupdf.open(path)
    issues = []
    page_details = []
    text_lines = []
    header_ok = True
    footer_ok = True
    metadata_text = json.dumps(doc.metadata, ensure_ascii=False)
    for index, page in enumerate(doc):
        lines = [line for line in page.get_text("text").splitlines() if line.strip()]
        text_lines.extend(lines)
        rows = text_rows(page)
        outside = outside_spans(page)
        page_details.append({"page": index + 1, "text_lines": len(lines), "rows": rows, "outside": outside})
        if outside:
            issues.append(f"{path.name} page {index + 1}: {outside} text spans outside page")
        if lines:
            header_ok &= f"{software} {version}" in lines[0]
        if is_program:
            header_ok &= f"第 {index + 1} 页 / 共 {doc.page_count} 页" in lines[1] if len(lines) > 1 else False
            footer_ok &= ("连续前30页" in lines[-1] or "连续后30页" in lines[-1] or "完整源程序" in lines[-1]) if lines else False
    doc.close()

    all_text = "\n".join(text_lines)
    info = {
        "path": str(path),
        "pages": len(page_details),
        "sha256": sha256(path),
        "page_details": page_details,
        "automation_terms": sorted({m.group(0) for m in AUTOMATION_RE.finditer(all_text)}),
        "sensitive_terms": sensitive_hits(all_text),
        "metadata_automation_terms": sorted({m.group(0) for m in AUTOMATION_RE.finditer(metadata_text)}),
        "metadata_sensitive_terms": sensitive_hits(metadata_text),
    }
    if is_program:
        info["header_ok"] = bool(header_ok)
        info["footer_ok"] = bool(footer_ok)
        info["all_pages_line_count"] = all(detail["text_lines"] == lines_per_page + 3 for detail in page_details)
        if not info["header_ok"]:
            issues.append(f"{path.name}: header mismatch")
        if not info["footer_ok"]:
            issues.append(f"{path.name}: footer mismatch")
        if not info["all_pages_line_count"]:
            issues.append(f"{path.name}: pages must contain {lines_per_page} source rows plus header/footer")
    if info["automation_terms"] or info["metadata_automation_terms"]:
        issues.append(f"{path.name}: automation-related terms found")
    if info["sensitive_terms"] or info["metadata_sensitive_terms"]:
        issues.append(f"{path.name}: sensitive terms found")
    return info, text_lines, issues


def source_check(source_copy: Path | None, base_copy: Path | None) -> tuple[dict, list[str]]:
    if not source_copy and not base_copy:
        return {"checked": False}, []
    if not source_copy or not base_copy:
        return {"checked": False}, ["source-copy and base-copy must be supplied together"]
    source_files = {p.relative_to(source_copy).as_posix(): p for p in source_copy.rglob("*") if p.is_file()}
    base_files = {p.relative_to(base_copy).as_posix(): p for p in base_copy.rglob("*") if p.is_file()}
    missing = sorted(base_files.keys() - source_files.keys())
    extra = sorted(source_files.keys() - base_files.keys())
    line_mismatches = []
    for relative in sorted(base_files.keys() & source_files.keys()):
        base_lines = len(base_files[relative].read_text(encoding="utf-8").splitlines())
        copy_lines = len(source_files[relative].read_text(encoding="utf-8").splitlines())
        if base_lines != copy_lines:
            line_mismatches.append({"file": relative, "base": base_lines, "copy": copy_lines})
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in source_files.values())
    info = {
        "checked": True,
        "file_count": len(source_files),
        "missing": missing,
        "extra": extra,
        "line_mismatches": line_mismatches,
        "automation_terms": sorted({m.group(0) for m in AUTOMATION_RE.finditer(source_text)}),
        "sensitive_terms": sensitive_hits(source_text),
    }
    issues = []
    if missing or extra or line_mismatches:
        issues.append("source filing copy inventory or line counts differ from the baseline")
    if info["automation_terms"]:
        issues.append("source filing copy contains automation-related terms")
    if info["sensitive_terms"]:
        issues.append("source filing copy contains sensitive terms")
    return info, issues


def upload_check(upload_dir: Path, allowed: set[Path], allow_extra: bool) -> tuple[dict, list[str]]:
    files = sorted(path for path in upload_dir.iterdir() if path.is_file())
    extra = [path.name for path in files if path.resolve() not in allowed]
    info = {"files": [path.name for path in files], "extra": extra}
    issues = [] if allow_extra or not extra else ["upload directory contains files outside the approved PDF set"]
    return info, issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material-root", type=Path, required=True)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--software", required=True)
    parser.add_argument("--version", default="V1.0")
    parser.add_argument("--source-text", type=Path)
    parser.add_argument("--source-copy", type=Path)
    parser.add_argument("--base-copy", type=Path)
    parser.add_argument("--upload-dir", type=Path)
    parser.add_argument("--allow-extra-upload", action="store_true")
    parser.add_argument("--program-pages", type=int, default=60)
    parser.add_argument("--program-mode", choices=["auto", "full", "front-back"], default="auto")
    parser.add_argument("--front-pages", type=int, default=30)
    parser.add_argument("--back-pages", type=int, default=30)
    parser.add_argument("--program-lines-per-page", type=int, default=50)
    parser.add_argument("--document-rows-per-page", type=int, default=30)
    parser.add_argument("--document-pages", type=int)
    parser.add_argument("--wrap-width", type=int, default=72)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    issues = []
    program_info, program_lines, program_issues = pdf_info(
        args.program, args.software, args.version, True, args.program_lines_per_page
    )
    document_info, document_lines, document_issues = pdf_info(
        args.document, args.software, args.version, False, args.document_rows_per_page
    )
    issues.extend(program_issues)
    issues.extend(document_issues)

    if program_info["pages"] != args.program_pages:
        issues.append(f"program PDF has {program_info['pages']} pages, expected {args.program_pages}")

    document_content_rows = [max(0, detail["rows"] - 2) for detail in document_info["page_details"]]
    document_info["content_rows"] = document_content_rows
    if any(rows < args.document_rows_per_page for rows in document_content_rows):
        issues.append("document PDF has a page below the required content-row minimum")
    if args.document_pages and document_info["pages"] != args.document_pages:
        issues.append(f"document PDF has {document_info['pages']} pages, expected {args.document_pages}")

    source_info, source_issues = source_check(args.source_copy, args.base_copy)
    issues.extend(source_issues)

    program_mode = args.program_mode
    if program_mode == "auto":
        program_mode = "front-back" if program_info["pages"] == args.front_pages + args.back_pages else "full"
    program_info["mode"] = program_mode
    if program_mode == "front-back" and program_info["pages"] != args.front_pages + args.back_pages:
        issues.append("front-back program mode must contain exactly front-pages + back-pages pages")

    if args.source_text:
        raw = [line for line in args.source_text.read_text(encoding="utf-8").splitlines() if line.strip()]
        visual = [wrapped_part for line in raw for wrapped_part in wrapped(line, args.wrap_width)]
        if program_mode == "front-back":
            front_count = args.front_pages * args.program_lines_per_page
            back_count = args.back_pages * args.program_lines_per_page
            expected = visual[:front_count] + visual[-back_count:]
        else:
            expected = visual
        code_lines = []
        doc = pymupdf.open(args.program)
        for page in doc:
            lines = [line for line in page.get_text("text").splitlines() if line.strip()]
            code_lines.extend(lines[2:-1])
        doc.close()
        actual_normalized = [normalize(line) for line in code_lines]
        expected_normalized = [normalize(line) for line in expected]
        mismatches = sum(a != b for a, b in zip(actual_normalized, expected_normalized))
        mismatches += abs(len(actual_normalized) - len(expected_normalized))
        source_info["selected_source_mismatches"] = mismatches
        if mismatches:
            issues.append(f"program PDF differs from selected source text in {mismatches} rows")

    upload_info = {"checked": False}
    if args.upload_dir:
        allowed = {args.program.resolve(), args.document.resolve()}
        upload_info, upload_issues = upload_check(args.upload_dir, allowed, args.allow_extra_upload)
        issues.extend(upload_issues)

    result = {
        "ok": not issues,
        "issues": issues,
        "program": program_info,
        "document": document_info,
        "source_copy": source_info,
        "upload": upload_info,
    }
    output = args.output_json or args.material_root / "99_内部核对_勿上传" / "rzcn_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
