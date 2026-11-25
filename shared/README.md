# Shared tools

This directory is reserved for code used by more than one paper. No numerical
code has been moved here during the initial setup: Paper 1 remains a byte-for-byte
copy of its tested standalone companion.

When another paper needs the same code, move the common functionality here in a
reviewed change, retain the paper-specific inputs and assumptions in its own
folder, and test both affected workflows. Published source snapshots and cited
tags remain unchanged; later versions identify their own tested dependencies.
