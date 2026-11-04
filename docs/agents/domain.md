# 领域文档

Engineering skills 探索代码库时，按以下规则读取领域文档。

## 探索前读取

- 根目录的 `GLOSSARY.md`。
- `docs/adr/` 中与当前工作相关的 ADR。

文件不存在时直接继续，无需报告缺失或预先建议创建。`/domain-modeling` 会在术语或决策明确后按需创建它们。

## 文件结构

本仓库采用 single-context 布局：

```text
/
├── GLOSSARY.md
├── docs/adr/
│   └── 0001-example.md
└── src/
```

## 使用 glossary 中的术语

在 issue 标题、重构提案、假设和测试名称中命名领域概念时，使用 `GLOSSARY.md` 定义的术语，避免使用其中明确排除的同义词。

如果需要的概念尚未收录，先判断是否误用了项目未采用的语言；如果确实存在领域模型空缺，记录下来并交由 `/domain-modeling` 处理。

## 标记与 ADR 的冲突

如果输出与已有 ADR 冲突，明确指出冲突及重新讨论的理由，不要静默覆盖。
