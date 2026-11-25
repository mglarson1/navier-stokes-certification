# Verification workflow

The entry point `tools/verify_bundle.py` authenticates all nine original
submission files using `data/archive-lock.json`, extracts the two archives into
a new directory, and runs the archived checks with bytecode writing disabled.
It does not rewrite the original programs, translate their formulas or replace
their exact arithmetic with floating-point calculations.

| Stage | Check | Mode |
|---|---|---|
| `integrity` | New manifest, release bindings and exact scalar budget | Both |
| `arrays` | 96 NPZ archives / 875 array identities, including dtype and payload | Both |
| `enclosures` | Stored full-space bounds, 25 weighted loads and exact aggregation | Both |
| `scalars` | Frozen independent scalar and continuous-time reduction replay | Portable |
| `geometry` | Frozen independent tree/partition and wall checks | Portable |
| `cover` | Frozen independent physical-cover and vertex-map replay | Portable |
| `earlier` | Earlier manifest and six unconditional exact scalar assemblies | Both |

`passed: true` in the summary means these selected checks completed with success
reports. It is not a claim that omitted production arithmetic has been rerun.
Detailed native reports can contain `full_drag_certificate: false` because they
are individual proof components; the assembled release and its integrity check
are the place to read the completed certificate status.

## Manual commands

After checking the archive hashes, extract both archives under the same parent.
From `T2_certificate_v1`, these are the original seven commands:

```sh
python3 -B verification/verify.py --report ../integrity.json
python3 -B verification/arrays.py --report ../arrays.json
python3 -B verification/enclosures.py --out ../enclosures
python3 -B verification/replay.py scalars --out ../scalars
python3 -B verification/replay.py geometry --out ../geometry
python3 -B verification/replay.py cover --out ../cover
python3 -B verification/verify_earlier.py --archive ../earlier_certificates_2026-11-17 --report ../earlier-check.json
```

All output paths must stay outside the frozen evidence. Do not edit a file inside
an archive to adjust a path; the archived replay adapter already redirects the
recorded native paths to local extracted files. A fresh directory is recommended
for every manual replay as well.

## Additional numerical recomputation

`verification/replay.py loads --out ...` is an optional, substantial numerical
rerun of six complete selected physical-load cells. It requires compatible
Linux x86-64 extended-precision NumPy arrays. It is not run by this portable
entry point and must not be described as an exhaustive production audit.
Consult the guide and `FULL_RECOMPUTATION.txt` inside the T2 archive before
attempting further regeneration.

## Download and failure handling

HTTPS downloads are size-bounded and authenticated before their final filenames
are accepted. Partial downloads are removed on failure. A failed run retains
its logs and failure summary; choose a new work directory for a rerun. Archive
extraction rejects links, devices, duplicate member names, paths outside the
expected root, and unexpected total file counts or sizes.

An offline local-file run does not download packages or contact CM1/HPC2N.
Install dependencies first. The wrapper records the actual interpreter and
package versions; the tested versions are pinned in the requirements file.

## Repository tests

The lightweight tests exercise corruption detection, unsafe archive rejection,
fresh-directory enforcement, false-success rejection and curated-file identity.
They test the publication wrapper, not the mathematical theorem. A complete
portable run with the actual archives is recorded separately in the publication
preparation review and must be repeated from the public deposit after release.
