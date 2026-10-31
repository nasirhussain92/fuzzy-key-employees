# fuzzy-key-employees

Code, data snapshot and results for *Survivor Loss and Fuzzy Cutvertices: Mathematical Modelling of Key-Person Risk in Informal Communication Networks* (Sahar Altaf and Nasir Hussain, Karachi Institute of Economics and Technology; Sumaira Yousuf Khan, Dawood University of Engineering and Technology). The working title of the manuscript was *Hidden Key Employees in Informal Communication Networks*; the code and results are unchanged. The reported results were produced with code commit 3fbc326; later commits change only documentation, comments and author information.

## Repository structure

```
fuzzy-key-employees/
├── README.md
├── LICENSE                   # MIT (code)
├── CITATION.cff              # how to cite; authors with ORCID
├── requirements.txt          # minimum package versions
├── .gitignore
├── fuzzy_hrm.py              # the model (manuscript Sections 3–4, Supplementary Material)
├── verify.py                 # brute-force checks; must print ALL CHECKS PASSED
├── benchmark.py              # synthetic speed test (not findings)
├── make_figures.py           # draws Figures 2–3 from results/ (python make_figures.py)
├── figures/                  # figure2.png, figure3.png (600 dpi)
├── supplement/
│   └── Supplementary_Material.pdf  # proofs and implementation details (S1–S3)
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
