# Releases for a series of papers

One repository hosts continuing software development. Each paper has a stable
identifier, its own companion directory and a separately identifiable evidence
deposit. This is a project convention; it does not require every future paper
to use the same authors, software licence or data record.

## Paper-specific release record

For each released paper, record:

- paper title and author order;
- exact repository commit and tag, such as `paper1-v1.0.0`;
- version-specific evidence DOI and direct record link;
- source snapshot and archive SHA-256 identities;
- exact verification commands, dependencies, observed outcomes and scope;
- the assumptions and limitations supporting the mathematical claims;
- licences and third-party terms for the material actually included.

Before the first public release, complete those fields using real identifiers,
confirm the licences and verify a fresh extraction of the final source snapshot
and local evidence files. After publication, repeat verification from a fresh
public download. Do not invent
identifiers, declare a draft public, or infer a complete production-arithmetic
audit from file checks and selected replay stages.

## Preservation

Do not move a published tag or replace a released evidence archive. If a result
or its supporting files change, issue a new paper release and a new version of
that paper's evidence record. Cite the version-specific DOI. A different paper
starts a distinct record, even when it reuses some data or code; link the records
and state the reuse explicitly.

Git tags identify complete repository snapshots rather than isolated folders.
The accompanying deposit must include the source files needed for that paper,
including any shared code used by that commit, so the proof workflow remains
available without relying on a changing branch or an external checkout.

The current Paper 1 companion has its own `REPOSITORY_MANIFEST.json`. Its initial
import is intentionally byte-for-byte identical to the tested preparation.
Changing a checked paper file requires new checks and a deliberately updated
manifest for the new version. Never update a manifest merely to conceal an
unexplained mismatch.

## What stays out of Git

Keep multi-gigabyte frozen evidence archives, large generated caches and routine
job outputs in the archival deposit or working storage. Git holds source,
instructions, small authoritative records, figure inputs and evidence links.
Private working notes and manuscript drafts are not included by default.

## Sources for the archival workflow

- [GitHub: releases and tags](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [Zenodo: versions of a record](https://help.zenodo.org/docs/deposit/manage-versions/)

Repository structure and the per-paper naming convention above are our design
choices; the linked documentation describes the underlying services.
