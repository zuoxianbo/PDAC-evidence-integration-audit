# NCS 投稿包总清单 — PDAC evidence-integration audit（v32_20260824_0958）

最终版本：**已完成 from-scratch clean rerun，所有数字精确复现**，满足 *Nature Computational Science* Analysis 投稿要求。

## 一、正文

| 文件 | 说明 |
|---|---|
| `manuscript_v32_20260824_0958.md` | 最终 Markdown 源稿 |
| `manuscript_v32_20260824_0958.docx` | 最终 Word 稿（Arial + 微软雅黑，含 9×5 端点表） |

合规项：摘要 149 词（≤150）、正文 3,410 词（≤3,500）、6 主图、10 条 CrossRef 已验证文献、0 AI 痕迹词、0 em-dash。Reproducibility 段已更新为「clean rerun 已完成并复现」。

## 二、主图（6 张，400 DPI，PNG + PDF，语义调色板，布局已修复）

`figures_v32_20260824/`（基于 clean rerun 结果重新渲染，数字完全一致）
- Fig. 1 — 单层证据 + 端点依赖结构
- Fig. 2 — 13 评分器 × 8 端点基准矩阵
- Fig. 3 — 整合 vs 中心性（效应量 + 社区重采样）
- Fig. 4 — 整合为何看似有效
- Fig. 5 — 敏感性（函数形式 / 权重空间 / 负对照 / 重编码）
- Fig. 6 — 药理学压力测试（2 面板）

## 三、补充表格 + 扩展数据图

- `supplementary_v32_20260824/` — Supp Tables 1–5 + source_data.csv + pairwise CSV
- `extended_data_v32_20260824/` — ED Fig. 1–4（PNG+PDF，真实数据）

## 四、投稿材料

- `cover_letter_v32_20260824.md`、`author_contributions_v32_20260824.md`、`competing_interests_v32_20260824.md`

## 五、代码与可复现性（clean rerun 已完成 ✅）

`PDAC_evidence_integration_audit_code_v32_20260824.zip`

**Clean rerun 完成记录（run_record_v32_20260824.txt）**：
- `git_commit_sha: c439c9af42792abb93fe97f505e7efdb40bd8d01`
- `results_manifest_sha256: 4aa24440ebddbaf50e4921b71d98bfc37151e94d500ff812f3d290765bb1bb23`
- 环境：`sc-models` venv（py3.11.9 / numpy1.26.4 / scipy1.17.1 / sklearn1.9.0，与 environment_lock 完全一致）
- 执行：`v18_recompute.py`（分段）+ `v18_weightspace.py` + `v18_sentinel_audit.py`
- 新增可复现脚本：`code/rerun_segmented.py`（逐端点断点续传 + int32 bootstrap 索引）、`code/rerun_finalize.py`（合并断点 + 负对照/重采样/候选/输出）

## 六、复现核验结果（关键）

| 核验项 | 结果 |
|---|---|
| benchmark 104 cells（13 scorer × 8 endpoint） | 最大绝对差 **0.00e+00**，0 不一致 ✅ |
| headline AUROC + CI（E1/E3/E5/E6 等 10 项） | 全部精确到 6 位小数一致 ✅ |
| E5 paired Δ（−0.0453，CI −0.0854 to −0.0132） | 完全一致 ✅ |
| 负对照（0.6931/0.7802/0.6880/0.4344） | 完全一致 ✅ |
| 函数形式（0.8926/0.8247/0.7578/0.6931/0.6363） | 完全一致 ✅ |
| Dirichlet（mean 0.3332 / 91.2% / 3.2% / 1000 抽样） | **位级一致** ✅ |
| sentinel 审计 + 15 条 audit findings | 完全一致 ✅ |

**结论**：final clean rerun 已在作者机器上从原始输入完整重算，正文每一个数字都精确复现。此前「P0-7 未完成」的诚实标注现已闭环——不再是「待输入」，而是「已复现」。

## 七、原始输入位置（投稿说明用）

8 项原始第三方输入在本机（不随稿分发，正文已注明 SHA-256 校验）：
`~/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14/data/` + `~/.../DeepCDR/data/{GDSC,CCLE}/`
