# RZCN

RZCN 是一个用于中国计算机软件著作权登记材料制作与复核的 Codex Skill。

它从真实项目源码和软件文档出发，在独立材料副本中完成事实确认、脱敏、人工维护风格整理、分页、PDF 生成和全量校验。正式项目源码不会被修改。

## 工作流

1. 确认软件名称、版本、著作权人、开发完成日期、发表状态、首次发表信息和权利取得方式。
2. 确认源码目录、语言、文件数、总行数及文档来源。
3. 建立提交文件、源码登记副本、文档源稿和内部核对目录。
4. 只在源码副本中整理自然维护风格、口语化注释和适量拼音局部变量。
5. 清除服务器地址、部署路径、数据库连接、凭据、私有日志和自动化工作流信息。
6. 按功能顺序拼接源码，处理长行续行，生成连续前30页和后30页，每页50行。
7. 使用完整文档生成文档鉴别材料；不足60页整套提交，每页至少30行。
8. 检查所有页面的越界、截断、空白、行数、页码和文字完整性。
9. 对比程序材料与选定源码，并核对副本文件数和逐文件行数。
10. 扫描 PDF 文本与元数据，计算 SHA-256，确保正式上传目录只保留规定 PDF。
11. 报告已验证结果、未验证项和申请人仍需确认的事实。

## 内容

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

## 使用

将 `rzcn/` 放入 Codex skills 目录后，可调用：

```text
$rzcn 按完整工作流为当前项目制作软著程序鉴别材料和文档鉴别材料，只修改独立副本，完成脱敏、PDF 生成和全量复核。
```

脚本依赖：

```text
Python 3.10+
PyMuPDF
python-docx
```

## 边界

RZCN 负责材料工程、脱敏、分页和一致性检查，不替代律师审查，也不替代申请人确认权属、日期和发表事实。

RZCN 禁止：

- 修改正式项目源码；
- 虚构作者、Git 历史、维护记录或多人协作证据；
- 故意降低代码质量以制造人工痕迹；
- 将敏感扫描零命中表述为法律结论。
