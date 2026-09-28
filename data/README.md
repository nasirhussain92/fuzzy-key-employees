# Data

This folder holds a fixed snapshot of the public data used in the paper, so every result can be reproduced even if the original download links change.

| File | Source | Citation | Use |
| --- | --- | --- | --- |
| `raw/email-Eu-core-temporal.txt.gz` | Stanford SNAP, https://snap.stanford.edu/data/email-Eu-core-temporal.html | Paranjape, Benson & Leskovec (2017) | All analyses |
| `raw/email-Eu-core-department-labels.txt.gz` | Stanford SNAP, https://snap.stanford.edu/data/email-Eu-core.html | Yin, Benson, Leskovec & Gleich (2017) | Node-ID check only (Section 4.1) |
| `SHA256SUMS` | Created when the snapshot was downloaded | — | Integrity check |

The notebook checks both files against `SHA256SUMS` before use and stops if a checksum does not match. The files are unchanged copies of the SNAP originals; please cite the sources above when using them.

The department labels belong to the static email-Eu-core release. Matched to the temporal data by node ID, the same-department share of linked pairs equals the chance level (0.048), so the IDs of the two releases do not correspond and the labels are not used in the analysis. The notebook reproduces this check (`results/department_label_check.json`).
