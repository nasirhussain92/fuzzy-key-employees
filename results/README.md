# Results

Produced by `notebooks/fuzzy_hrm_colab.ipynb` from the data snapshot in `data/` (code commit and environment in `run_info.json`). Table numbers refer to the manuscript.

| File | Content | Manuscript |
| --- | --- | --- |
| `run_info.json` | Date, code commit, data checksums, parameters, seed, Python and package versions | Section 5, Data and Code Availability |
| `requirements-lock.txt` | Exact package versions of the published run | — |
| `reproduction_check.txt` | Independent re-computation on a different machine and environment; differences, tolerance and file hashes | Section 5 (reproducibility statement) |
| `main_summary.json` | Network size, NCI, fuzzy cutvertices, hidden and material key members, fuzzy bridges | Table 7; Section 5.2 |
| `main_employee_scores.csv` | KS, T, rank, contacts, non-pendant bridges and classification for every member (main setting) | Section 5.1 text (KS values, medians, Spearman) |
| `main_fuzzy_bridges.csv` | Fuzzy bridges with membership and pendant flag (main setting) | Section 5.2 |
| `main_rank_comparison.csv` | Kendall's τ and top-k overlap between KS and strategies S2–S5 | Table 8 |
| `scenarios_main_K1.csv`, `_K5.csv`, `_K10.csv` | Departure-scenario outcomes for S1–S6, main setting, waves 1%, 5%, 10% | Table 9; Section 5.3 crisp outcomes |
| `scenarios_<setting>_K<wave>.csv` | The same for the sensitivity settings | Table 10 (S1 rank) |
| `scenarios_all.csv` | All scenario runs in one table | — |
| `robustness_compact.csv` | τ, Jaccard and S1 rank per sensitivity setting | Table 10 |
| `robustness.csv` | The same, per setting and wave | Table 10 |
| `department_label_check.json` | Same-department share under an ID match versus chance | Section 4.1 (labels not used) |

Note: the files use the column name `employees` for network nodes; in the manuscript these are reported as members, because the dataset does not record employment status.
