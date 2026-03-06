# OpenLang Benchmark Results

Run: 2026-03-05 22:12

| Model | Comprehension | Generation | Round-trip | Overall |
|-------|--------------|------------|------------|---------|
| codex | 35/35 (100%) | 29/35 (83%) | 26/30 (87%) | 94.0% |
| gemini-2.5-flash | 34/35 (97%) | 33/35 (94%) | 27/30 (90%) | 96.5% |

### codex — Failures (2)

- **g17** (generation): judge returned invalid format
- **r25** (roundtrip): The model attempted to execute the natural language instruction directly, resulting in an error message and a skip instruction. The expected response was the OpenLang L2 code representing the instruction, not an execution log.

### gemini-2.5-flash — Failures (1)

- **g19** (generation): judge returned invalid format
