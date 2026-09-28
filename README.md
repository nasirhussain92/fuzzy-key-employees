# fuzzy-key-employees

Code, data snapshot and results for *Hidden Key Employees in Informal Communication Networks: A Fuzzy Graph Model of Key-Person Risk for Human Resource Planning* (Sahar Altaf and Nasir Hussain, Karachi Institute of Economics and Technology).

## Repository structure

```
fuzzy-key-employees/
├── README.md
├── LICENSE                   # MIT (code)
├── CITATION.cff              # how to cite; authors with ORCID
├── requirements.txt          # minimum package versions
├── .gitignore
├── fuzzy_hrm.py              # the model (manuscript Sections 3–4, Appendix A)
├── verify.py                 # brute-force checks; must print ALL CHECKS PASSED
├── benchmark.py              # synthetic speed test (not findings)
├── notebooks/
│   └── fuzzy_hrm_colab.ipynb # full analysis in Google Colab
├── data/
│   ├── README.md             # sources and citations
│   ├── SHA256SUMS            # checksums of the snapshot
│   └── raw/                  # unchanged copies of the public data
└── results/
    ├── README.md             # what each result file contains
    └── ...                   # outputs of the notebook, incl. run_info.json
```

## Reproduce the results

1. Open `notebooks/fuzzy_hrm_colab.ipynb` in Google Colab (File → Open notebook → GitHub).
2. Runtime → Run all. The notebook verifies the code, checks the data against `data/SHA256SUMS`, and writes all outputs to Google Drive.
3. Compare the new files with `results/`. `results/run_info.json` lists the code commit, data checksums, seed and package versions of the published run; `results/requirements-lock.txt` pins the exact versions.

## Run locally

```
pip install -r requirements.txt
python verify.py
python benchmark.py 100
```

## Contact

Corresponding author: Nasir Hussain, nhussain@kiet.edu.pk
