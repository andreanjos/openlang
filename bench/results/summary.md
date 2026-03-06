# OpenLang Benchmark Results

Run: 2026-03-05 22:57

| Model | Comprehension | Generation | Round-trip | Overall |
|-------|--------------|------------|------------|---------|
| codex | 33/35 (94%) | 30/35 (86%) | 25/30 (83%) | 93.5% |
| gemini-2.5-flash | 34/35 (97%) | 31/35 (89%) | 26/30 (87%) | 95.0% |

### codex — Failures (1)

- **r12** (roundtrip): structural errors: ["unbalanced ']'", 'unclosed delimiters: }']

### gemini-2.5-flash — Failures (1)

- **r16** (roundtrip): The model's response is correct. The prompt requested specific details ("12 files changed and no conflicts"), and the model correctly encoded these de
