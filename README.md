# RZCN

## 中文介绍

RZCN 是一个用于软件著作权登记材料制作与复核的 Codex Skill。它从真实项目源码和软件文档出发，在独立副本中完成事实确认、脱敏、人工维护风格整理、分页、PDF 生成和全量校验，不修改正式项目源码。

工作流：

1. 确认软件名称、版本、著作权人、完成日期、发表状态及权利取得方式。
2. 确定源码范围、文件数、总行数和文档来源。
3. 建立提交文件、源码副本、文档源稿和内部核对目录。
4. 只在源码副本中整理自然维护风格、口语化注释和适量拼音变量。
5. 清除服务器地址、部署路径、数据库连接、凭据、日志和工作流信息。
6. 按功能顺序拼接源码并处理长行续行。
7. 生成连续前30页和后30页，每页50行。
8. 使用完整文档生成文档鉴别材料；不足60页整套提交，每页至少30行。
9. 检查页数、行数、越界、截断、空白页和页码连续性。
10. 对比选定源码，核对副本文件数、逐文件行数和 SHA-256。
11. 扫描 PDF 文本和元数据，确保正式上传目录只保留规定文件。

## English Introduction

RZCN is a Codex Skill for preparing and reviewing software copyright registration materials. Starting from real project source code and software documentation, it works in an isolated copy to complete fact confirmation, desensitization, natural maintenance-style cleanup, pagination, PDF generation, and full verification without modifying the official project source.

Workflow:

1. Confirm the software name, version, copyright owner, completion date, publication status, and basis for acquiring rights.
2. Determine the source-code scope, file count, total line count, and document source.
3. Create directories for submission files, the source copy, document source, and internal audit records.
4. Perform natural maintenance-style cleanup only in the source copy, including conversational comments and a limited number of pinyin variable names.
5. Remove server addresses, deployment paths, database connections, credentials, logs, and workflow information.
6. Assemble source code in functional order and wrap long lines.
7. Generate continuous first 30 pages and last 30 pages with 50 lines per page.
8. Generate documentation identification material from a complete document; if it is under 60 pages, submit the entire document with at least 30 lines per page.
9. Verify page count, line count, overflow, truncation, blank pages, and page-number continuity.
10. Compare the selected source code and verify the copy's file count, per-file line counts, and SHA-256.
11. Scan PDF text and metadata and ensure only the required files remain in the official upload directory.

## Repository Contents

```text
rzcn/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ scripts/
│  ├─ build_program_pdf.py
│  ├─ build_document_pdf.py
│  └─ audit_materials.py
├─ references/
│  ├─ workflow.md
│  ├─ desensitization.md
│  └─ acceptance-checklist.md
└─ assets/templates/
   ├─ introduction.md
   ├─ material_audit.md
   ├─ platform_fields.txt
   └─ submission_notes.txt
```

## Usage / 使用

Place `rzcn/` in the Codex skills directory, then invoke:

```text
$rzcn Prepare and audit the software copyright filing package for the current project while preserving the official source code.
```

脚本依赖：

```text
Python 3.10+
PyMuPDF
python-docx
```

## Boundaries / 边界

RZCN is responsible for material engineering, desensitization, pagination, and consistency checks. It does not replace legal review or the applicant's confirmation of ownership, dates, and publication facts.

RZCN 不替代律师审查，也不替代申请人确认权属、日期和发表事实。

RZCN must not:

- modify official project source code;
- fabricate authors, Git history, maintenance records, or collaboration evidence;
- intentionally degrade code quality to manufacture human-looking traces;
- present a zero-result sensitive scan as a legal conclusion.

RZCN 禁止修改正式项目源码、虚构开发或维护记录、故意降低代码质量，以及把敏感扫描零命中表述为法律结论。

## License / 许可证

This project is open source under the [MIT License](LICENSE).

本项目采用 [MIT License](LICENSE) 开源。
