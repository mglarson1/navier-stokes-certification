# Preparation checks, 25 November 2026

The new entry point was tested against copies of the nine original submission
files. All nine sizes and SHA-256 hashes matched. It extracted both archives
into a fresh temporary location and completed all seven portable checks:
integrity, arrays, stored enclosures, scalar/time replay, geometry replay,
physical-cover replay, and the earlier archive.

The run took approximately 314 seconds on the preparation machine, including
copying, hashing and extraction. This is an observed local runtime, not a
prediction for downloads or other machines. The environment was Python 3.12.0,
NumPy 2.5.2 and mpmath 1.3.0 on macOS arm64.

The extracted file totals were 63,707 and 65,707, including each root manifest.
The exact T = 2 outward interval was reproduced. All 13 wrapper/provenance tests
passed, including corrupted downloads, disabled assertions and a false-success
report. These tests concern the wrapper; they do not establish new mathematics.

The unchanged figure script rebuilt both PNG figures byte-for-byte identically
to the revised manuscript and reproduced the exact derived budget JSON.

The publication deposit includes the fresh replay reports and a separate
publication verification summary. The original proof evidence and its earlier
verification reports remain unchanged. No fresh numerical load-cell audit or
exhaustive production spatial rerun was performed during this preparation.

The eventual public Zenodo upload has not yet been downloaded or verified:
no public record exists at this stage. That is a separate release check.
