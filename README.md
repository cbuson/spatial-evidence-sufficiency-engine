# Spatial Evidence-Sufficiency Reference Engine

[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/Code%20license-MIT-green.svg)](LICENSE)
[![Supplementary license: CC BY 4.0](https://img.shields.io/badge/Supplementary-CC%20BY%204.0-lightgrey.svg)](LICENSE-SUPPLEMENTARY.md)

Reference implementation and reproducibility package for the manuscript:

**From incomplete spatial evidence to bounded inference: an integrative evidence-sufficiency methodology developed across four scientific applications**

Associated manuscript authors:

- Carlos Busón Buesa — Universidade Federal de Mato Grosso do Sul (UFMS) — ORCID: 0000-0002-1446-2252
- Sandra Garcia Gabas — Universidade Federal de Mato Grosso do Sul (UFMS) — ORCID: 0000-0002-1027-0288

## Purpose

This repository implements a domain-neutral logical engine for evaluating the **sufficiency of spatial evidence for an explicit scientific target**.

The engine receives evidence that has already been assigned to spatial units and evaluates a declared evidence contract. It preserves explicit epistemic states, distinguishes critical from non-critical requirements, retains exact bottlenecks, and returns a claim boundary that limits interpretation.

The implementation is intentionally independent of geometry processing. Spatial assignment may be performed in QGIS, PostGIS, GeoPandas, GRASS GIS, ArcGIS, or another GIS environment before the evidence is passed to the engine.

## What the engine does

The reference engine preserves the evidence states:

- `SUPPORTED`
- `VERIFIED_NEGATIVE`
- `UNKNOWN`
- `CONFLICT`
- `NOT_APPLICABLE`
- `INVALID`

Requirements can use:

- `ANY`
- `ALL`
- `COUNT_AT_LEAST`

The bounded target output is one of:

- `SUPPORTABLE`
- `REJECTED_BY_EVIDENCE`
- `NON_EVALUABLE`
- `NOT_APPLICABLE`

The output also retains the requirement-level states, bottlenecks, and `claim_boundary`.

## What the engine does not do

The engine does **not**:

- predict mineral deposits;
- calculate mineral prospectivity;
- estimate groundwater potential;
- interpolate spatial values;
- assign evidence to geometries;
- replace domain expertise;
- convert missing information into zero;
- establish authorization, consent, occurrence, resource, reserve, or other claims beyond the declared target contract.

A reproducible contract is not automatically a scientifically valid contract. Domain adequacy must come from appropriate theory, standards, empirical evidence, or expert judgment.

## Repository contents

| File | Purpose |
|---|---|
| `evidence_sufficiency_engine.py` | Domain-neutral reference engine |
| `test_engine.py` | Eight unit tests for the generic engine |
| `run_pag_tb_td.py` | PAG-ETR T-B exact reproduction and T-D contract-sensitivity run |
| `pag_tb_fixture.json` | Compact frozen PAG-ETR M2/M4 state-vector fixture |
| `pag_tb_exact_engine_summary.csv` | Scale-specific T-B reproduction summary |
| `pag_td_contract_sensitivity.csv` | T-D structural contract-sensitivity results |
| `pag_tb_td_report.json` | Machine-readable combined reproduction report |
| `supplementary/Supplementary_Methodology_Workbook.xlsx` | Methodological inventory, audit evidence, and quantitative supplementary material |
| `CITATION.cff` | Citation metadata |
| `CHANGELOG.md` | Version history |
| `RELEASE_CHECKLIST.md` | GitHub/Zenodo release procedure |
| `SHA256SUMS.txt` | Checksums for the frozen public package |

## Reproduce the reference tests

Python 3.10 or newer is required. The engine uses only the Python standard library.

```bash
python test_engine.py
```

Expected result:

```text
Ran 8 tests
OK
```

## Reproduce PAG-ETR T-B and T-D

```bash
python run_pag_tb_td.py
```

The script regenerates:

- `pag_tb_exact_engine_summary.csv`
- `pag_td_contract_sensitivity.csv`
- `pag_tb_td_report.json`

For the frozen fixture included in version 1.0.0, the expected control result is:

- 2,759 cell-scale cases;
- 8,277 overall/M2/M4 cell-output comparisons;
- 110 baseline `SUPPORTABLE` cell-scale instances;
- 2,649 baseline `NON_EVALUABLE` cell-scale instances;
- zero discrepancies in the T-B semantic reproduction.

These results establish **internal semantic reproducibility for the frozen PAG-ETR contract**. They are not external validation.

## Scientific interpretation boundary

The package implements bounded inference. In particular:

- evidence sufficiency is not phenomenon occurrence;
- model evaluability is not mineral prospectivity;
- documentary sufficiency is not groundwater potential;
- investigation priority is not authorization for fieldwork;
- territorial evidence is not community consent.

A favourable aggregate cannot override a blocked critical gate.

## Associated development applications

The methodology was developed across four related spatial applications:

- JOAJU MS — https://github.com/cbuson/atlas-interativo-ms
- ITA ARANDU MS — https://github.com/cbuson/atlas-geocientifico-ms
- PAG-ETR MS — https://github.com/cbuson/pag-etr-ms
- PIH-MS — https://github.com/cbuson/pih-ms

These applications are development cases, not independent replications.

## Citation

repository URL:

`https://github.com/cbuson/spatial-evidence-sufficiency-engine`

Busón Buesa, C., & Garcia Gabas, S. (2026). Spatial Evidence-Sufficiency Reference Engine (Versión v1.0.2) [Software informático]. Zenodo. https://doi.org/10.5281/zenodo.23047388

## Versioning

The manuscript reproduction package is frozen as **v1.0.0**.

Future changes should use semantic versioning and must not overwrite the archived v1.0.0 release used for the manuscript.

## Licenses

- Source code is released under the **MIT License**. See `LICENSE`.
- The supplementary workbook and generated tabular/JSON outputs are released under **CC BY 4.0**. See `LICENSE-SUPPLEMENTARY.md`.

## Contact

Carlos Busón Buesa  
Universidade Federal de Mato Grosso do Sul (UFMS), Brazil  
ORCID: 0000-0002-1446-2252  
Email: carlos.buson@ufms.br
