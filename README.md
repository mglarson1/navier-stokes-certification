# Navier–Stokes certification

Reproducible verification code and paper-specific evidence maps for the
certification of quantities in Navier–Stokes flows.

This repository supports a series of related papers. Reusable software belongs
in `shared/`; each paper has a self-contained companion under `papers/`, with
its own authorship, assumptions, commands and data record. The large frozen
evidence archives are distributed through per-paper archival deposits.

**Current status:** repository setup. Public releases, licences and evidence
DOIs have not yet been finalized. No DOI or publication date is implied here.

## Papers

| Paper | Authors | Result and companion |
|---|---|---|
| Certified drag for a three-dimensional Navier–Stokes wake and the horizon of energy-based certification | Erik Burman and Mats G. Larson | [Paper 1: completed T = 2 drag certificate](papers/paper1-certified-drag/README.md) |

For Paper 1, the certified drag interval is
`[0.112699029269657744, 0.112852594864699145]`, under the paper's specified
model, exact initial field, weak-solution class and arithmetic assumptions.
Uniqueness of weak solutions is neither assumed nor established. See the
[full scope](papers/paper1-certified-drag/docs/SCOPE.md) before using the result.

## Structure

```text
shared/                         reusable tools as they emerge
papers/
  paper1-certified-drag/         tested companion for the first paper
docs/                           release and preservation policy
tools/                          checks on the repository's paper snapshots
```

Paper 1 initially preserves all 25 files of the tested standalone companion,
including its own verification wrapper, requirements, exact records and figure
code. Its existing commands work from within its folder. Common numerical
code will be extracted into `shared/` when another paper actually needs it;
the current proof checks have not been refactored during repository setup.

## Start with Paper 1

From the repository root:

```sh
python3 -B tools/check_paper_snapshots.py
cd papers/paper1-certified-drag
python3 -B -m unittest discover -s tests -v
```

For the complete seven-check evidence replay, follow that folder's
[verification instructions](papers/paper1-certified-drag/docs/VERIFICATION.md)
and [quick start](papers/paper1-certified-drag/README.md). The evidence archives
are not included in Git. The prior preparation passed all seven checks on a
fresh extraction; this repository import preserves the verified companion bytes.

## Cite a fixed paper release

Each paper will identify an exact repository commit and a paper-specific tag,
for example `paper1-v1.0.0`, plus its own version-specific Zenodo evidence DOI.
The tag is a repository snapshot; its name identifies the paper whose
reproducibility package it supports. Development can continue on `main` without
changing the cited snapshot. A repository tag alone is not our preservation
guarantee: the source snapshot and checksums will also be archived with the data.

Different papers receive distinct evidence records. Updates to the evidence for
the same paper become versions of that paper's record. Authors and licences are
recorded per paper; a new paper does not automatically inherit the first paper's
author list or funding. See [the release policy](docs/RELEASE_POLICY.md).

Keep a separate repository if a future project has substantially different
software, contributors or access requirements. For this connected sequence of
Navier–Stokes certification papers, one shared repository keeps improvements
to the common tools together while retaining individually citable results.
