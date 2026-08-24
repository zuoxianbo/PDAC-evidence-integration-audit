Dear Editor,

We are submitting our manuscript, "Auditing evidence integration for context-dependent therapeutic target prioritization", for consideration as an Analysis in *Nature Computational Science*.

This study audits a widely held but rarely tested assumption in computational target prioritization: that combining heterogeneous gene-level evidence into a single integrated score improves therapeutic target ranking. Using pancreatic ductal adenocarcinoma (PDAC) as a testbed, we benchmark thirteen scoring strategies across nine evidence layers and eight evaluation endpoints whose provenance we classify explicitly into external-label, non-independent, and constructed/circular classes. Our central finding is negative but actionable: fixed-form evidence integration does not improve ranking relative to the strongest single evidence layer (network centrality) on any endpoint whose labels are defined outside the evidence base. Apparent integration gains arise only on constructed endpoints whose labels embed an input layer, and vanish once that layer is removed (support-term AUROC on E3 falls from 0.889 to 0.535). We further show that a random draw from the composite's weight space is centred below chance (mean AUROC 0.333; 91.2% of 1,000 Dirichlet draws below 0.5), locating the reported advantage in endpoint construction and implementation choices rather than any intrinsic benefit of integration.

We believe this work is a good fit for *Nature Computational Science* because it (1) provides a reproducible, provenance-aware framework for auditing evidence integration, (2) demonstrates concretely how label leakage, missing-data encoding, and combination algebra can manufacture spurious integration gains, and (3) offers a cheap, generalizable diagnostic—the input-layer deletion test—that we argue should become a routine reporting requirement.

The manuscript contains six display items, five Supplementary Tables, four Extended Data Figures, and a single machine-readable source-data table. All inputs are public; analysis code is released under the MIT licence with a pinned environment specification and input manifest, so every number and figure regenerates from released inputs. Data-availability and code-availability statements are included in the Methods.

We confirm this manuscript is original, has not been published elsewhere, and is not under consideration by another journal. All authors have approved the submission and agree to its consideration by *Nature Computational Science*.

Thank you for considering our work.

Sincerely,

Zuoxianbo (on behalf of all authors)
Department of Big Data Center
China-Japan Friendship Hospital, Beijing, China
