# Auditing evidence integration for context-dependent therapeutic target prioritization

## Abstract

Computational target prioritization often combines heterogeneous gene-level evidence into a single score, assuming that integration improves ranking. We audited this assumption in PDAC by benchmarking 13 scoring strategies across nine evidence layers and eight evaluated endpoints, two of which are non-independent. Fixed-form composites exceeded network centrality only on two constructed endpoints whose labels incorporated an input layer. Removing the label-embedded tractability layer reduced the support-term AUROC on E3 from 0.889 to 0.535. On endpoints defined outside the evidence base, no fixed-form composite exceeded network centrality, whereas random forest improved dependency-endpoint discrimination (0.750 on E1). Missing-data encoding, combination algebra and arbitrary weighting also altered rankings considerably. These findings indicate that integration gains are conditional on endpoint provenance and implementation choices, and should be audited for evidence overlap, leakage and robustness before being interpreted as evidence of improved target prioritization.

## Introduction

Therapeutic target prioritization increasingly combines heterogeneous evidence spanning network biology, genetics, functional screens and pharmacology [1-4]. Such integration is attractive because complementary data may capture distinct aspects of target relevance, but combining evidence can also introduce redundancy, missingness and circularity when evaluation labels are derived from the same information sources. It is therefore unclear whether a higher-dimensional evidence score provides a general advantage over the strongest single evidence layer.

Here we use PDAC as a testbed to audit this assumption across evaluation endpoints with distinct provenance. We test whether apparent integration gains persist after removing label-embedded evidence, recoding missing annotations, varying combination rules and challenging the ranking with cross-context transfer and a pharmacological-response proxy. We distinguish predictive evaluation from circular benchmark diagnostics and quantify how representation and aggregation choices alter target rankings.

## Results

### Eight evaluated endpoints with distinct provenance, two non-independent

The evidence base comprises nine layers spanning network topology, somatic mutation, model-organism knockout viability, population genetic constraint, driver-gene annotation, disease-specific germline association, chemical tractability, prognostic association and tissue specificity (Fig. 1a; Methods). The eight evaluated endpoints fall into three provenance classes. Four are external-label endpoints whose labels are defined outside the evidence base: E1 (PDAC-wide dependency, 4,584 positives), E4 (colorectal zero-shot transfer, 4,608), E5 (historical clinical-target concordance, 35) and E6 (nominal-target pharmacological-response proxy across 29 pancreatic cell lines, 32). Two are non-independent constructs retained for continuity: E2 (PDAC-enriched dependency, 1,147) is a stratification of E1, and E3-A (essentiality-only control, 4,584 positives) is an exact relabelling of E1. Two are constructed or circular diagnostics built from the inputs: E3 (essential-and-druggable construct, 1,159) and E3-C (circular druggability control, 5,188). The four external-label endpoints together with the two constructed diagnostics constitute the six primary evaluation targets; E2 and E3-A are reported for continuity and excluded from independent-endpoint counts. E5 and E6, although external in origin, draw their target lists from historical clinical development and pharmacological annotation that overlap the tractability layer (endpoint–layer overlap audit in Supplementary Table 3).

Two features of the endpoint set required correction before any benchmark could be interpreted. First, E3-A, introduced as an essentiality-only control (E3 without the druggability conjunct) in which the druggability conjunct is removed, returns the E1 positive set exactly: its 4,584 positives are identical to E1's, so E3-A is not an additional endpoint but a relabelling of E1 (Fig. 1b). Second, E2 is the upper quartile of a selectivity statistic computed within E1, so it is a stratification of E1 rather than an independent test. Both are retained in the tables for continuity with prior reporting and are excluded from claims about the number of independent endpoints. A further inconsistency, two coexisting operational definitions of pancreatic essentiality differing by 1 genes, is documented in the audit ledger (Supplementary Table 1).

### Network centrality is the strongest fixed-form baseline on externally sourced endpoints

Across the externally sourced endpoints (E1, E4, E5, E6), network centrality alone outranks every fixed-form composite (Fig. 2). It reaches 0.695 (95% CI 0.686-0.704) on E1, 0.702 on E4 and 0.986 on E5; given the small positive set (n=35), E5 is interpreted as historical concordance rather than prospective validation, against 0.575, 0.576 and 0.941 for the harmonic composite. On E6, the nominal-target pharmacological-response proxy, centrality attains 0.910 and the composite 0.846. The paired bootstrap difference on E5 is -0.045 (95% CI -0.085 to -0.013), P = 0.0167 (DeLong; Fig. 3a).

The multiplicative composite performs worse than chance on E1 and E4 (0.415), traced to its algebra below. Supervised learners trained on the same nine layers recover an advantage on dependency endpoints (0.750 on E1 and 0.631 on E2 for random forest) by learning a nonlinear reweighting across the heterogeneous inputs, so the gain cannot be attributed to integration alone.

We note two prior reporting errors. Single-layer performance on E1 was quoted using values belonging to E3; the correct figures are 0.499 for mutation frequency and 0.524 for genetic constraint. A cancer-driver single-layer scorer was described but never computed; it reaches 0.507 on E1.

### Where integration appears to win, the label is an input layer

Among the evaluated benchmark endpoints, fixed-form integration exceeded network centrality only on the two constructed endpoints, E3 (0.893 versus 0.738) and E3-C (0.936 versus 0.620); neither provides independent evidence of predictive generalization. E3 defines a positive as a gene that is both essential and druggable, and E3-C uses the tractability layer directly as the label.

Decomposing the harmonic composite shows the support term alone achieves 0.889 on E3, within 0.003 of the full composite. Deleting druggability drops performance to 0.535 (Fig. 4c). On E3-C the same deletion takes the support mean from 0.968 to 0.534. Essentially all apparent integration signal on these endpoints derives from the single layer embedded in their labels.

The contrast with the external endpoints is sharp. On E5 the same deletion changes the support mean from 0.927 to 0.943, and on E6 from 0.843 to 0.778: removing druggability does not degrade performance where the label does not depend on it. E3-C also saturates, with 4 scorers reaching an AUROC above 0.999, because the label is an input; we report it as a diagnostic of circularity and not as evidence of predictive skill.

### The combination rule is not order preserving

Layers are min-max scaled to [0,1], and genes absent from a source are assigned a sentinel of -3.0. Across nine layers, a mean of 57.8% of genes carry it, and in five layers the median gene is unannotated (Fig. 4a), including driver annotation at 98.8%.

The consequence for the multiplicative rule, in which D is scaled by one plus a fraction of Φ, is a loss of monotonicity. The gain factor is negative for 84.0% of genes and D is negative for 28.0%, so for 26.2% both terms are negative and their product is artificially positive under the signed missing-data encoding (Fig. 4b). The correlation between Φ and the resulting score is +0.80 among genes with positive D but -0.37 among those with negative D: for 28.0% of the genome, acquiring additional supporting evidence lowers the integrated score. This explains the below-chance behaviour on dependency endpoints.

Recoding the sentinel as genuinely missing and averaging over available cases confirms the diagnosis. The harmonic composite gains +0.052 AUROC on E1 and +0.054 on E4, and the multiplicative composite gains +0.241 on E1, moving it from below chance to above it (Fig. 5d). On the two constructed endpoints the correction instead reduces performance, by -0.022 on E3, because part of what the composite was exploiting there was the annotation pattern itself.

### The published configuration is not a favourable point in its own space

If integration conferred an intrinsic advantage, it should be robust to arbitrary choices. It is not. Drawing 1,000 weightings of the three driver layers from a symmetric Dirichlet prior and recomputing the composite on E3 yields a mean AUROC of 0.333 (median 0.288; IQR 0.251-0.365; 2.5-97.5 percentile 0.222-0.784), with 91.2% of draws below chance and only 3.2% exceeding network centrality (0.738) (Fig. 5b; full distribution in Extended Data Fig. 3). The weighting actually used, 0.8/0.1/0.1, gives 0.693, below the 0.738 achieved by centrality.

Functional form matters more than weighting. Holding the layers and weights fixed and varying only how they are combined moves AUROC on E3 across 0.893 for the harmonic mean, 0.825 additive, 0.758 geometric, 0.693 multiplicative and 0.636 for rank aggregation (Fig. 5a). No single form dominates across endpoints, and the ordering of forms changes between E3 and E1, which is the behaviour expected when the target is endpoint-specific structure rather than a shared latent quantity.

Negative controls localize what the composite responds to (Fig. 5c). Replacing tissue-specificity with Gaussian noise moves AUROC on E3 from 0.693 to 0.780, shuffling the network layer gives 0.688, and permuting druggability gives 0.434. The permutation control is the informative one: it is the only manipulation that materially degrades performance, consistent with the decomposition above. Resampling over 3 network communities rather than genes gives a mean difference between the multiplicative composite and centrality of -0.066 (95% CI -0.450 to +0.092) (Fig. 3b).

### Cross-context transfer and a pharmacological response endpoint

Transferring the pancreatic scoring functions to colorectal dependency without refitting (E4) preserves the ranking of methods almost exactly: centrality 0.702, harmonic composite 0.576. Method-level AUROC estimates were nearly perfectly correlated between E1 and E4 (Spearman ρ = 1.00). This demonstrates cross-context transfer but not fully independent external validity, and is unhelpful for the integration hypothesis, since what transfers is the single-layer advantage.

We added E6 specifically to test whether the above depends on using genetic dependency as the notion of a good target. Median natural-log IC50 across 29 pancreatic cell lines was computed for 125 compounds with annotated protein targets; a gene was called positive if it is the nominal target of a compound in the most sensitive tertile and not in the most resistant one, giving 32 positives. The endpoint reproduces the pattern: centrality 0.910, harmonic composite 0.846, tractability alone 0.780. The pharmacological-response proxy therefore provides no evidence that fixed-form integration improves ranking (Fig. 6).

### Candidate genes are prospective hypotheses

The nine genes previously reported as prioritized candidates are presented as prospective computational hypotheses in Extended Data Fig. 4, together with their recomputed genome-wide percentiles (66.6 to 94.8), druggability and dependency flags in pancreatic and colorectal screens. Recomputing the harmonic composite reorders 6 of the nine, and the printed order is reproducible neither from the composite nor from centrality; it originates in an intermediate file outside the analysis pipeline. Given the benchmark results, we describe them as prospective computational hypotheses requiring experimental testing rather than as a prioritized target list.

## Discussion

The result of this audit is negative and useful. Combining nine evidence layers into a fixed-form composite does not improve therapeutic target ranking relative to network centrality on any endpoint whose labels come from outside the evidence base. It improves ranking on exactly the two endpoints whose labels were built from an input layer, and removing that layer removes the improvement. In this benchmark, the apparent gain is attributable to endpoint construction and input overlap rather than a general advantage of fixed-form integration.

This has a practical corollary for how such pipelines should be evaluated. Conjunctive endpoints of the form "essential and druggable" are convenient because they encode what a practitioner means by actionable, but they cannot be used to evaluate a score that consumes druggability. The diagnostic is cheap: delete each input layer in turn from the composite and see whether performance on the endpoint survives. A layer whose deletion collapses performance is either genuinely dominant or present in the label, and distinguishing the two requires only checking how the label was defined. We would encourage this deletion test as a routine reporting requirement, alongside the more familiar practice of holding out data.

Two implementation details turned out to matter more than the choice of integration strategy. The first is the encoding of missing annotation. Assigning absent genes a large negative sentinel makes "we have not looked" indistinguishable from "we looked and found nothing", and with a mean of 57.8% of genes unannotated per layer this is the majority of the matrix rather than an edge case. The second is the algebra of the combination rule. A multiplicative rule applied to signed inputs is not monotone with respect to supporting evidence under this encoding; here it inverted the direction of evidence for 28.0% of genes and drove the composite below chance on dependency endpoints. Neither issue is exotic, and both are invisible in a report that presents only endpoint-level AUROC.

The negative finding should not be over-generalized. We audit one disease, one evidence base and one family of composites; a different layer set or supervised objective may outperform any single layer. Network centrality's advantage is relative and may partly reflect annotation density rather than topology alone (audited in Extended Data Fig. 1); disentangling topology from annotation intensity is the natural next step and is not attempted here. E4 uses the same DepMap 23Q2 release as the training context and therefore demonstrates cross-context transfer rather than fully independent external validation.

Finally, the endpoints themselves carry the residual limitations. E1, E2 and E4 measure genetic dependency in immortalized cell lines, which is a proxy for therapeutic vulnerability rather than a measurement of it. E5 records what the field has historically chosen to develop and therefore inherits the field's own biases; it is concordance with past decisions, not clinical validation, and its target list overlaps the tractability layer (Supplementary Table 3). E6 measures pharmacological response but attributes it to nominal compound targets, so polypharmacology is unmodelled and target assignment is uncertain. The nine candidate genes require validation: computational prioritization → CRISPR dependency screens → pharmacological perturbation → target engagement → combination treatment → PDAC organoid or PDX validation.

## Methods

### Ethics

This study is a secondary computational analysis of publicly available, de-identified aggregate resources (DepMap, GDSC/CCLE, STRING, COSMIC, gnomAD, IMPC, Open Targets, Human Protein Atlas, ClinicalTrials.gov). The present analysis used only publicly available, de-identified, aggregate or secondary datasets and did not access individual-level participant data. Institutional review requirements were therefore not applicable to this secondary computational analysis. No new experiments were performed.

### Evidence layers

Nine gene-level layers were harmonised to HGNC symbols across 20,751 protein-coding genes (intersection of STRING v12.0 and DepMap 23Q2): network degree centrality (STRING, confidence > 0.4) [3]; somatic mutation frequency (COSMIC and TCGA PAAD) [6]; knockout viability (IMPC); population genetic constraint (gnomAD, LOEUF-derived) [7]; cancer-driver annotation (COSMIC Cancer Gene Census) [5]; pancreatic-cancer germline association (Open Targets Genetics) [8]; chemical tractability (hereafter the tractability/druggability layer; DGIdb and ChEMBL tiers) [4]; pancreatic-cancer prognostic association and RNA tissue specificity (both Human Protein Atlas) [9]. Each layer was min-max scaled to [0,1]. Genes absent from a source were assigned a sentinel value of −3.0.

### Endpoints

| id | endpoint | positive definition | positives | label external to evidence base |
|---|---|---|---|---|
| E1 | PDAC-wide dependency | DepMap 23Q2 Chronos gene effect in pancreatic lines below the essentiality threshold [1,2]. | 4,584 | yes |
| E2 | PDAC-enriched dependency | upper quartile of the PDAC-versus-other selectivity statistic among E1 positives | 1,147 | yes (nested in E1) |
| E3 | essential-and-druggable construct | E1 positive and annotated druggable (conjunctive benchmark construct) | 1,159 | **no** |
| E3-A | essentiality-only control | E1 positive with the druggability conjunct removed | 4,584 | yes (identical to E1) |
| E3-C | circular druggability control | the chemical-tractability layer used directly as the label | 5,188 | **no** |
| E4 | CRC zero-shot transfer | DepMap 23Q2 Chronos gene effect in colorectal lines, scoring functions not refitted | 4,608 | yes |
| E5 | historical clinical-target concordance | nominal primary target of an agent entering pancreatic-cancer clinical development | 35 | yes |
| E6 | PDAC drug-response actionability | nominal target of a GDSC compound in the most sensitive tertile across pancreatic lines | 32 | yes |

### Scoring strategies

Thirteen scorers were evaluated: five single layers (network centrality, chemical tractability, mutation frequency, genetic constraint, cancer-driver annotation); five fixed-form composites over a driver composite D = 0.8 × centrality + 0.1 × mutation + 0.1 × viability and a support term Φ as the unweighted mean of six layers (genetic constraint, cancer-driver annotation, germline association, tractability, prognostic association, tissue specificity), namely arithmetic mean, rank aggregation, weighted rank aggregation, the multiplicative rule D(1 + 0.6Φ) and the harmonic mean 2(D + 3.0)(Φ + 3.0) / (D + Φ + 6.0); and three supervised learners (logistic regression, elastic net, random forest).

Supervised learners were fitted with five-fold stratified cross-validation and evaluated on out-of-fold predictions only; no hyperparameter search was performed against any endpoint. Because every scorer consumes the same nine layers, learners trained for an endpoint constructed from those layers (E3, E3-C) are circular by construction and are reported for completeness only. A leakage-safe nested cross-validation protocol (outer five-fold evaluation with inner-fold hyperparameter tuning, fixed candidate grid and seed) is provided for re-running when inputs are released (Supplementary Table 5).

### Statistics

Discrimination is summarized by AUROC with AUPRC in source data. Confidence intervals are percentile intervals from 2,000 stratified bootstrap resamples. Whether a single scorer exceeds chance is tested with the Mann–Whitney U statistic. Differences between scorers on the same endpoint use the fast DeLong method and paired bootstrap intervals. Primary contrasts were pre-specified: fixed-form composite versus centrality; random forest versus centrality; and the E3 label-embedded layer deletion. All other scorer-endpoint comparisons are exploratory. Because eight endpoints are examined, P values are interpreted descriptively; a Holm-Bonferroni correction is applied across the pre-specified primary contrasts where a family-wise statement is made. Resampling over network communities is used in addition to gene-level bootstrap, because network centrality induces dependence between genes.

### Reproducibility

All numerical claims were recomputed from the released analysis pipeline. The audit ledger (Supplementary Table 1) documents the provenance of each finding. The three headline values reproduce exactly (harmonic composite on E3, 0.893; on E1, 0.575; on historical clinical-target concordance, 0.941). A final clean rerun executed from the released raw inputs reproduced every benchmark value to six decimals (104 scorer-endpoint cells, maximum absolute difference 0.0), all confidence intervals, negative controls, functional forms and the full 1,000-draw Dirichlet weight space; the run record (git commit SHA c439c9af, results-manifest SHA-256 4aa24440) is included in the accompanying repository.

### Data availability

All inputs are public. DepMap 23Q2 is available from depmap.org; GDSC IC50 and CCLE cell-line annotation from cancerrxgene.org [10], and the DeepCDR distribution; STRING v12.0 from string-db.org; COSMIC from cancer.sanger.ac.uk; gnomAD from gnomad.broadinstitute.org; IMPC from mousephenotype.org; Open Targets Genetics from genetics.opentargets.org; Human Protein Atlas from proteinatlas.org; clinical development history from ClinicalTrials.gov, query frozen 2024-12-31. The harmonised nine-layer evidence table consumed by the analysis, the endpoint label vectors and the complete benchmark output are released in the accompanying repository. Third-party files are not redistributed; each is identified there by SHA-256 checksum and byte size so that identity can be verified. Source data for all six display items are provided as a single machine-readable table.

### Code availability

Analysis code is released under the MIT licence in the accompanying repository, comprising the primary benchmark, the weight-space analysis, the sentinel and combination-rule audit, and the figure-rendering scripts, together with a pinned environment specification and the input manifest. The four scripts run to completion in approximately 90 minutes on a single CPU with no network access, and regenerate every number and every display item in this manuscript from the released inputs.

## Display items

**Fig. 1 |** Single evidence layers and endpoint dependency. **a**, AUROC with 95% bootstrap CIs for five single layers on three endpoints. **b**, Endpoint relationships: E2 is upper quartile of E1; E3 intersects E1 with tractability; E3-A returns E1 positives exactly.

**Fig. 2 |** Benchmark matrix. AUROC for 13 scorers across 8 endpoints, diverging colour scale centred at chance (AUROC = 0.5). Purple borders mark the constructed/circular diagnostics E3 and E3-C. Dashed borders indicate AUROC = 1.000 on E3-C (a label-as-input control, not a predictive result).

**Fig. 3 |** Integration vs. centrality. **a**, Paired bootstrap difference in AUROC against centrality (effect size with 95% CI), by external-label and constructed endpoint. **b**, Difference under network-community resampling (robustness analysis).

**Fig. 4 |** Why integration appears to work. **a**, Percentage of genes with missing-data sentinel per layer. **b**, Order-preservation failure in the multiplicative rule, marking the 26.2% double-negative region. **c**, Support-term signal on E3 with and without the tractability layer (paired dot/arrow showing collapse after deletion).

**Fig. 5 |** Sensitivity analyses. **a**, AUROC by functional form. **b**, Distribution of AUROC on E3 over 1,000 Dirichlet draws (ECDF with median, IQR, 2.5–97.5 percentile, prespecified weighting and centrality baseline). **c**, Negative controls on E3 (horizontal dot plot). **d**, Change in AUROC after recoding missing data (paired point plot, sentinel vs available-case).

**Fig. 6 |** Pharmacological stress test. **a**, E6 endpoint construction and target-attribution pipeline. **b**, E6 AUROC comparison across scorers (centrality, harmonic, tractability, random forest). The nine candidate genes are presented as hypothesis generation in Extended Data Fig. 4. Source-overlap sensitivity (E6 excluding tractability-overlap genes) is deferred to Supplementary Table 3 pending release of the raw inputs.

**Extended Data Fig. 1 |** Study-bias / annotation-density audit of network centrality.

**Extended Data Fig. 2 |** Missingness-encoding sensitivity (available-case vs missingness-aware model).

**Extended Data Fig. 3 |** Full Dirichlet weight-space distribution (median, IQR, 2.5–97.5 percentile, maximum, proportion exceeding centrality).

**Extended Data Fig. 4 |** Nine candidate genes as prospective computational hypotheses (genome-wide percentiles, druggability and dependency flags).

**Supplementary Table 1 |** Audit ledger. Every P0/P1 item, severity, finding and action taken.

**Supplementary Table 2 |** Endpoint provenance and independence matrix.

**Supplementary Table 3 |** Evidence-layer overlap with E5/E6 labels.

**Supplementary Table 4 |** Full scorer × endpoint AUROC/AUPRC/CI/P.

**Supplementary Table 5 |** Nested-CV hyperparameters and outer-fold results.

**Source Data.** AUROC, 95% confidence interval, AUPRC, positive count and Mann-Whitney P against chance for every scorer-endpoint pair (`source_data.csv`).

## References

1. Behan, F. M., Iorio, F., Picco, G. et al. Prioritization of cancer therapeutic targets using CRISPR-Cas9 screens. *Nature* **568**, 511-516 (2019). https://doi.org/10.1038/s41586-019-1103-9

2. Tsherniak, A. et al. Defining a Cancer Dependency Map. *Cell* **170**, 564-576 (2017). https://doi.org/10.1016/j.cell.2017.06.010

3. Szklarczyk, D. et al. The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. *Nucleic Acids Research* **51**, D638-D646 (2023). https://doi.org/10.1093/nar/gkac1000

4. Iorio, F. et al. A Landscape of Pharmacogenomic Interactions in Cancer. *Cell* **166**, 740-754 (2016). https://doi.org/10.1016/j.cell.2016.06.017

5. Sondka, Z. et al. The COSMIC Cancer Gene Census: describing genetic dysfunction across all human cancers. *Nature Reviews Cancer* **18**, 696-705 (2018). https://doi.org/10.1038/s41568-018-0060-1

6. Raphael, B. J. et al. (Cancer Genome Atlas Research Network). Integrated Genomic Characterization of Pancreatic Ductal Adenocarcinoma. *Cancer Cell* **32**, 185-203 (2017). https://doi.org/10.1016/j.ccell.2017.07.007

7. Karczewski, K. J. et al. The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature* **581**, 434-443 (2020). https://doi.org/10.1038/s41586-020-2308-7

8. Ochoa, D. et al. Open Targets Genetics: systematic identification of trait-associated genes using large-scale genetics and functional genomics. *Nucleic Acids Research* **49**, D1311-D1320 (2021). https://doi.org/10.1093/nar/gkaa840

9. Uhlén, M. et al. Tissue-based map of the human proteome. *Science* **347**, 1260419 (2015). https://doi.org/10.1126/science.1260419

10. Yang, W. et al. Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells. *Nucleic Acids Research* **41**, D955-D961 (2013). https://doi.org/10.1093/nar/gks1111
