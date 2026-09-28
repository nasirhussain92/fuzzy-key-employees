# Data

This folder holds a fixed snapshot of the public data used in the paper, so every result can be reproduced even if the original download links change.

| File | Source | Citation |
| --- | --- | --- |
| `raw/email-Eu-core-temporal.txt.gz` | Stanford SNAP, https://snap.stanford.edu/data/email-Eu-core-temporal.html | Paranjape, Benson & Leskovec (2017) |
| `raw/email-Eu-core-department-labels.txt.gz` | Stanford SNAP, https://snap.stanford.edu/data/email-Eu-core.html | Yin, Benson, Leskovec & Gleich (2017) |
| `SHA256SUMS` | Created when the snapshot was downloaded | — |

The notebook checks every file against `SHA256SUMS` before use and stops if a checksum does not match.
The files are unchanged copies of the SNAP originals; please cite the sources above when using them.

**Enron** (planned): the 420 MB CMU corpus (Klimt & Yang, 2004) is too large for GitHub. Only the derived table of employee-to-employee messages (`sender, receiver, time`) and the job-title list (Shetty & Adibi, 2004) will be stored here.
