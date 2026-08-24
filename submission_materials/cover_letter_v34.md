# Cover letter — NCS v34 submission

**Manuscript:** "Auditing when evidence integration improves therapeutic target prioritization"
**Journal:** *Nature Computational Science* (Content type: **Analysis**)

---

Dear Editors,

We are pleased to submit our manuscript, "Auditing when evidence integration improves therapeutic target prioritization", for consideration as an Analysis in *Nature Computational Science*.

Therapeutic target prioritization increasingly combines heterogeneous genomic, functional, network and pharmacological evidence. Yet an important methodological assumption remains insufficiently tested: when an integrated score performs better than a simpler baseline, does that gain reflect genuinely complementary information, or can it arise from endpoint construction and implementation choices?

Here, we address this question directly using pancreatic ductal adenocarcinoma (PDAC) as a testbed. We compare 13 scoring strategies across nine evidence layers and six primary evaluation endpoints spanning independent labels, constructed endpoints and circular controls. We find that fixed-form integration does not show a general advantage over network centrality on endpoints defined outside the evidence base. Apparent gains are localized to constructed endpoints containing a layer already used by the scorer. We further show that missing-data encoding and aggregation rules can materially change rankings, while learned nonlinear reweighting can recover signal from the same evidence layers. Cross-context transfer and a pharmacological-response stress test do not restore a consistent fixed-form integration advantage.

The main conceptual contribution is therefore not another target-ranking model, but an audit framework for determining when an apparent integration gain is biologically and computationally interpretable. The study separates predictive performance from circular benchmark diagnostics and proposes endpoint provenance, leakage assessment, representation sensitivity and external stress testing as necessary checks before integration gains are interpreted as improved therapeutic prioritization.

We believe this work is particularly well suited to *Nature Computational Science* because it addresses a broadly applicable computational problem at the intersection of machine learning evaluation, biomedical data integration and therapeutic discovery. The conclusions extend beyond PDAC: they concern how computational researchers should construct endpoints, benchmark multimodal methods and distinguish genuine information gain from benchmark- or implementation-induced performance inflation.

All primary inputs are public, the analysis is fully computational, and the released code regenerates the benchmark, sensitivity analyses and main display items. The manuscript includes explicit data availability, code availability, reproducibility and AI-use statements.

[RELATED MANUSCRIPTS: Insert either "The authors have no related manuscripts under consideration or in press elsewhere" or a complete disclosure of each related manuscript and its status.]

[PRIOR EDITORIAL DISCUSSION: Insert either "We have not previously discussed this manuscript with a Nature Computational Science editor" or provide the editor's name, date and substance of the discussion.]

Suggested reviewers are provided in `SUBMISSION_PACKAGE_v34.md` (pool of six; select 4–5 after author-conflict screening). We have not listed excluded reviewers because no author-specific conflict-of-interest information was supplied for this package; any exclusion request should be limited to genuine, documentable conflicts.

Thank you for considering our manuscript.

Sincerely,

[Corresponding author full name, degree]
[Department / Institution]
[City, Country]
[Email]
[ORCID]

---

*Prepared from `NCS_Submission_Package_v34.docx`. Placeholders in [brackets] must be completed before submission. Companion items: `author_contributions_v34.md`, `competing_interests_v34.md`, `SUBMISSION_PACKAGE_v34.md`.*
