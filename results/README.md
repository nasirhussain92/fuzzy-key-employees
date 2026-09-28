# Results

Produced by `notebooks/fuzzy_hrm_colab.ipynb` from the data snapshot in `data/`. Re-running the notebook on the same code commit and data should reproduce these files.

| File | Content |
| --- | --- |
| `run_info.json` | Date, code commit, data checksums, parameters, seed, Python and package versions |
| `requirements-lock.txt` | Exact package versions used for the run |
| `main_summary.json` | Network size, NCI, counts of fuzzy cutvertices, hidden and material key employees, fuzzy bridges |
| `main_employee_scores.csv` | KS, T, rank and classification for every employee (main setting) |
| `main_fuzzy_bridges.csv` | Fuzzy bridges (main setting) |
| `main_rank_comparison.csv` | Kendall's τ and top-k overlap between KS and strategies S2–S5 |
| `scenarios_<setting>_K<wave>.csv` | Departure-scenario outcomes for strategies S1–S6 |
| `scenarios_all.csv` | All scenario runs in one table |
| `robustness.csv` | S1 rank, τ and Jaccard for each sensitivity setting and wave |
