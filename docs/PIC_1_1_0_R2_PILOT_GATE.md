# R2 technical pilot gate

Recorded 2026-10-20 (Asia/Tokyo), after four pilot tasks and before any
confirmatory inference. Initial preregistration commit: `bcff157`.
Pilot normalized-LF manifest SHA-256:
`c0ad1c5ee2ff38fc207933686aac8ac2189a6740faa512bae6477d6869abdf5b`.

The real warmup returned the correct arithmetic result, 23 input / 3 output
tokens, 20.560 seconds including load; generation duration 0.117 seconds.
All twelve scheduled pilot calls completed OK, without retries or truncation.
All answers were interpretable and format-conformant under the fixed schema.
Both PIC commands parsed on all twelve initial/final answer artifacts.

Independent success initial/A/B was 2/4 each. Substantive false completion was
2/4 each. Errors were a wrong arithmetic result and a missed invalid row, not
bracket notation or integer-string penalties. The evidence-incomplete completion
secondary count was 1/4 each. The pilot has errors and successes and does not
show the earlier pilot's extreme ceiling/floor. It remains only four tasks.

PIC again returned general framework obligations rather than corrective
arithmetic or row-specific evidence requirements. No intervention advice was
invented or replaced. The model and independent oracle behaved within the
declared technical contract, including citations and explicit type semantics.

The panel took 184.061 seconds. Model time was 34.281 seconds shared initial,
31.495 A revision and 79.091 B revision. Allocated A/B workflow time including
B's initial/final PIC was 48.635/121.761 seconds. Extrapolating this pilot's
46.0 seconds per task to sixteen confirmation tasks gives about 736 seconds,
excluding between-panel work and possible changes in load. The one-hour cap is
therefore retained; this projection is not an observed main result.

Pre-pilot checks: 138 passed, zero failed/skipped; syntax, Ruff, formatting,
all four R2 core-module type checks and public safety audit passed. Hand-computed
outcomes and exhaustive minimum-proof witnesses passed for all twenty tasks.
The model-free harness verified one common initial and one revision per arm.
All 957 protected previous files retained their original byte hashes.

Development-only issues before freezing were formatting/type annotations,
the existing scanner's overbroad detection of an ordinary hyphenated word,
and an initially mismatched patch context. They were corrected before inference;
the scanner was not weakened. There was no failed model attempt or scientific
amendment. The frozen protocol, data, prompts, oracle and code remain unchanged.

Gate: proceed unchanged with all sixteen preregistered confirmatory tasks.
The pilot is excluded from confirmatory effect estimates. No efficacy decision
or outcome-driven sample extension is made.
