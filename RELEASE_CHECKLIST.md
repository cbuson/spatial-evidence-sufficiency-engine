# Release checklist for GitHub + Zenodo

Use this checklist for the manuscript-associated release.

## Before creating the GitHub release

- [ ] Confirm the repository is public.
- [ ] Confirm `python test_engine.py` returns `Ran 8 tests` and `OK`.
- [ ] Run `python run_pag_tb_td.py`.
- [ ] Confirm `total_cells = 2759`.
- [ ] Confirm `total_cell_output_comparisons = 8277`.
- [ ] Confirm `total_discrepancies = 0`.
- [ ] Confirm no `__pycache__`, `.pyc`, temporary Office files, passwords, tokens, or private paths are committed.
- [ ] Confirm the supplementary workbook is the intended public version.
- [ ] Confirm both authors approve the public release.
- [ ] Update `SHA256SUMS.txt` if any frozen file changed.
- [ ] Commit and push the final state.

## GitHub release

Create a release with:

- Tag: `v1.0.0`
- Release title: `Spatial Evidence-Sufficiency Reference Engine v1.0.0`
- Mark as: full release, not prerelease

Suggested release notes:

> Frozen reproducibility release associated with the manuscript “From incomplete spatial evidence to bounded inference: an integrative evidence-sufficiency methodology developed across four scientific applications”. Includes the domain-neutral Python reference engine, eight unit tests, frozen PAG-ETR M2/M4 fixture, T-B exact semantic reproduction, T-D contract-sensitivity outputs, and supplementary methodological workbook. The frozen reproduction contains 2,759 cell-scale cases and 8,277 overall/M2/M4 comparisons with zero discrepancies. This establishes internal semantic reproducibility for the frozen contract, not external validation.

## Zenodo

1. Connect Zenodo to GitHub.
2. Enable archiving for this repository.
3. Create/publish GitHub release `v1.0.0`.
4. Confirm Zenodo creates the archived version and DOI.
5. Check creator names and ORCIDs.
6. Check title and version.
7. Record both:
   - version DOI for `v1.0.0`;
   - concept DOI, if shown by Zenodo.
8. For the manuscript, cite the **version DOI** corresponding to the exact release used.

## After Zenodo DOI is minted

Replace the manuscript placeholder with:

> The complete reproducibility package is available from the GitHub repository https://github.com/cbuson/spatial-evidence-sufficiency-engine. The exact version used in this study is archived in Zenodo as version 1.0.0, DOI: https://doi.org/10.5281/zenodo.XXXXXXX.

Then update the README citation section with the real DOI and create a small
metadata-only commit if needed. Do not alter the archived `v1.0.0` tag.
