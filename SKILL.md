---
name: rzcn
description: Prepare and audit Chinese software copyright registration source-code and documentation identification materials (RZCN), including isolated source copies, desensitization, natural maintenance-style cleanup, page and line rules, PDF generation, and final submission checks. Use when asked for 软著、程序鉴别材料、文档鉴别材料、软件著作权登记材料, or RZCN.
metadata:
  short-description: 制作和复核软著程序及文档鉴别材料
---

# RZCN

Produce a complete, internally consistent software-copyright submission package from real project evidence. The goal is a defensible filing package, not merely two generated PDFs.

## Operating workflow

1. Freeze the registration facts and identify the exact source and document scope.
2. Create an isolated material workspace and a source-copy baseline.
3. Build the filing source copy without changing the live project.
4. Apply a restrained natural maintenance-style pass to the copy only.
5. Desensitize the source, document, metadata, filenames, and reports.
6. Order and wrap source code, then generate the program identification PDF.
7. Rebuild one factual document and generate the documentation identification PDF.
8. Audit page counts, row minimums, bounds, source continuity, and source-copy line parity.
9. Scan both PDFs and the filing copy for secrets and tool/workflow traces.
10. Hash the final PDFs, keep only approved upload files, and report unresolved facts.

## Establish the filing contract

- Read project rules, current state, handoff, version manifests, and the source/document locations before acting.
- Record the software full name, short name, version, copyright owner, development mode, completion date, publication state, first-publication facts, and rights acquisition basis. Do not invent missing legal facts.
- Keep the project source read-only. All formatting, redaction, and natural-style cleanup happens in a separately copied filing source tree.
- Use an isolated output folder with:
  - `00_提交文件/`: only the final PDFs and, if requested, a checksum file kept outside the upload set.
  - `01_源码登记副本_脱敏/`: edited filing copy only.
  - `02_文档源稿_勿上传/`: editable manual source.
  - `99_内部核对_勿上传/`: scripts, text extracts, previews, manifests, and audit records.
- Never describe compilation, scans, or generated PDFs as legal acceptance. Applicant identity and ownership facts remain subject to human confirmation.

## Prepare the program material

1. Inventory the exact source scope and record file count, language counts, and total line count.
2. Create the independent filing copy. Preserve each source file's line count unless the user explicitly permits otherwise.
3. Apply the natural maintenance-style pass only to the copy:
   - Use specific, colloquial maintenance comments tied to actual behavior.
   - Add a small number of safe pinyin local variables where they remain readable and compilable.
   - Avoid uniform template comments, excessive decoration, and obviously generated section banners.
   - Do not intentionally degrade correctness. Do not fabricate Git history, authors, review trails, or co-worker activity.
   - Do not rename public APIs, database contracts, serialized fields, or cross-module identifiers without a dependency audit.
4. Redact before pagination. Read [references/desensitization.md](references/desensitization.md).
5. Order files by a defensible functional sequence. Place large low-value string or legal-text blocks away from the selected tail when the ordering is otherwise custom and still continuous.
6. Apply the official page rule:
   - For a source longer than 60 pages at 50 lines per page, submit the continuous first 30 pages and continuous last 30 pages.
   - If the complete source is under 60 pages, submit the complete source. Do not invent filler code.
7. Wrap long source lines within the printable width. Never allow clipping or text outside the page. Each program page must contain at least 50 nonblank display lines of source.
8. Generate the PDF with the software name/version, continuous page numbers, and a clear front/back marker.

Use [scripts/build_program_pdf.py](scripts/build_program_pdf.py) when a plain concatenated source text is available.

## Prepare the documentation material

- Select one complete document that actually describes composition, design, functions, development, testing, installation, or use. A software manual or design specification is suitable.
- If the complete document is under 60 pages, submit the entire document. If it is 60 pages or more, submit continuous first 30 pages plus continuous last 30 pages.
- Every submitted document page must contain at least 30 nonblank text rows. Do not pad with repeated or meaningless lines.
- Remove stale tables of contents or update their pagination after rebuilding.
- Use factual appendices or terminology sections to complete a final partial page when necessary.
- Sanitize interface keys, vendor details, server endpoints, and internal deployment facts that are not needed to describe the software.

Use [scripts/build_document_pdf.py](scripts/build_document_pdf.py) for a DOCX/TXT manual. Supply a factual appendix file when the input would leave a final page below the 30-row minimum.

## Desensitize and scan

At minimum remove or replace:

- public/private server IPs, SSH targets, deployment roots, internal DNS names, and private URLs;
- database URIs, passwords, tokens, private keys, signing material, account names, and management credentials;
- real phone numbers, personal email addresses, and customer identifiers;
- automation workspace names, model/tool logs, prompt transcripts, workflow records, and internal process notes;
- comments that expose unrelated systems, operational secrets, or data-retention internals.

Treat a zero-match scan as a hygiene result, not proof of authorship. Also inspect PDF text and metadata, not only source files.

## Build and audit

1. Generate both PDFs from the filing copies, not from the live project.
2. Render or inspect every page for blank pages, clipping, overlap, page-number continuity, and visual density.
3. Compare extracted program lines with the selected source text. Normalize whitespace and known font substitutions, then require zero unexplained mismatches.
4. Verify source-copy file inventory and line counts against the pre-edit copy.
5. Verify page counts and physical rows:
   - program: 60 pages when using front/back mode, 50 source rows per page;
   - document: complete or front/back mode as applicable, at least 30 numbered rows per page.
6. Scan PDF text, source copy, and metadata for automation terms and concrete sensitive values.
7. Run syntax or format parsing where feasible. Do not run the live application unless separately authorized.
8. Record SHA-256 hashes and keep only the intended PDFs in the upload folder.

Run [scripts/audit_materials.py](scripts/audit_materials.py) after generation. Use [references/acceptance-checklist.md](references/acceptance-checklist.md) for the final review.

## Stop conditions

Stop and report instead of claiming completion when:

- ownership, completion date, publication state, or rights basis is unresolved;
- the source scope or registration version is ambiguous;
- a secret remains in the filing copy or PDF;
- a page violates the line minimum, has clipped text, or the selected source cannot be traced continuously;
- the preparation requires changing live source or fabricating evidence;
- the final upload directory contains non-submission working files.

## Reporting

Report separately:

- changed and intentionally unchanged scope;
- material folder and source-copy path;
- program/document page counts and line rules;
- redaction and scan results;
- source inventory and line-count checks;
- syntax/format checks;
- PDF hashes;
- unresolved applicant facts and `[未验证]` items.
