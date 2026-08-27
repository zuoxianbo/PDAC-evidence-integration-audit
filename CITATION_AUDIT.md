# CITATION_AUDIT — 参考文献引用位置/内容匹配度 + 更新性核对

**日期：** 2026-08-26 · **对象：** `manuscript.docx`（32 篇参考文献）
**方法：** CrossRef API 逐条反查 DOI（标题/第一作者/期刊/卷/年份）；正文上标引用号上下文对照文献主题。

## 一、真实性（CrossRef 核实）

32 条 DOI 全部 `HTTP 200`，标题/作者/期刊/卷页与 manuscript 一致，**0 幻觉引用**。

- 上轮已修正唯一作者错误：#27 "Ochoa, D." → "Ghoussaini, M."（Open Targets Genetics）。
- 7 条年份与 CrossRef "issued" 差 1 年（#9/#21/#22/#25/#27/#28/#32），均为 **online-first vs print-year** 的正常差异，manuscript 用 print-year 正确。

## 二、引用位置 ↔ 内容匹配度（32/32 匹配）

| 引用号 | 正文论点（引用位置） | 所引文献主题 | 匹配 |
|---|---|---|---|
| 1–3 | 大规模功能筛选使癌症依赖可测量 + 基因组/药理资源 | DepMap / CRISPR–Cas9 筛 / 药理基因组交互 | ✅ |
| 4–10 | 多组学/多模态数据整合捕捉互补生物学 | 多模态 AI / 多组学 benchmark 系列 | ✅ |
| 5–6,9–10 | benchmark 显示整合获益取决于数据/任务/评估设定 | Cantini/Hu/Luecken/Liu benchmark | ✅ |
| 11–12 | 生物 ML 中证据重叠造成信息泄漏/循环评估 | 数据泄漏指南 / 因果建模泛化 | ✅ |
| 13–14 | 靶点标签(essentiality/druggability)可能与证据相连 | 人遗传学优先级评分 / 临床依赖图 | ✅ |
| 1–2,15–16 | PDAC testbed 合理性 | 依赖 + 药物敏感性 | ✅ |
| 15 | 缺失值表征敏感性 vs 蛋白组不完整数据 | HarmonizR（缺失值处理）| ✅ 精确 |
| 16–18 | 药物反应预测 cell line→tumor 需显式迁移 | 药物敏感性 / 迁移学习 | ✅ 精确 |
| 4,7–8,13,14,19,20–21 | 整合是常见策略（Discussion 首句） | 多模态 + 靶点 + dependency map | ✅ |
| 4–6,9,10,17,18 | 预处理/模态/评估设计改变排名 | 多模态 + 药物反应 | ✅ |
| 22 | STRING 网络层 | STRING 2023（对应 evidence_layers V11）| ✅ |
| 23,24 | 体细胞突变（COSMIC + TCGA-PAAD） | TCGA-PAAD / COSMIC CGC | ✅ |
| 25 | IMPC 敲除存活 | IMPC | ✅ |
| 26 | gnomAD 遗传约束 | gnomAD | ✅ |
| 24 | 癌症驱动注释 | COSMIC Cancer Gene Census | ✅ |
| 27 | 生殖系关联 | Open Targets Genetics | ✅ |
| 28–29 | 化学成药性（DGIdb + ChEMBL） | DGIdb 3.0 / ChEMBL | ✅ |
| 30 | 预后关联（HPA） | HPA 病理图谱 | ✅ |
| 31 | 组织特异性（HPA） | HPA 蛋白组图谱 | ✅ |
| 32 | GDSC 药敏 | GDSC | ✅ |

## 三、是否有更新文献可替换

**结论：无需要替换的引用。**

1. **方法学引用（#1–21）已是最新**：核心文献集中在 2021–2026，含 2024–2026 的 Hu/Liu/Baltušytė/Pacini/Carli/Shi/Pun/Arafeh，无过时文献。
2. **数据源引用（#22–32）对应实际使用版本**：分析数据为 `evidence_layers_v11.json`（内部版本 V11，11 层），各数据源引用的是其数据库标准/奠基论文（STRING 2023、GDSC、IMPC、gnomAD、Open Targets、DGIdb、ChEMBL、HPA）。数据源引用应锚定"实际使用版本"而非"最新版本"，否则引用与数据脱节、破坏可复现性。
3. **可标注（非必须改）**：DGIdb 3.0(2018) / ChEMBL(2015) 在数据库社区有更新版（DGIdb 4.0/5.0、ChEMBL 34），但 V11 数据未显式记录其子版本，引用标准论文是稳妥选择，不构成错误。

## 四、结论

- **引用位置与内容：32/32 匹配，无错引、无张冠李戴。**
- **更新性：无需替换（方法学已最新，数据源锚定实际版本）。**
- **citation order：1→32 严格按首次出现顺序递增，无跳号/重复。**
- 唯一实质错误（#27 作者）已在上轮修正。

*本核对仅记录，无需改动 manuscript。*
