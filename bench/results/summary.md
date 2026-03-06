# OpenLang Benchmark Results

Run: 2026-03-05 22:02

| Model | Comprehension | Generation | Round-trip | Overall |
|-------|--------------|------------|------------|---------|
| codex | 33/35 (94%) | 24/35 (69%) | 21/30 (70%) | 85.0% |
| gemini-2.5-flash | 32/35 (91%) | 24/35 (69%) | 23/30 (77%) | 85.0% |

### codex — Failures (8)

- **g03** (generation): judge returned invalid format
- **g09** (generation): judge returned invalid format
- **g23** (generation): judge returned invalid format
- **g28** (generation): judge returned invalid format
- **r23** (roundtrip): judge returned invalid format
- **r25** (roundtrip): The model
- **r28** (roundtrip): timeout (90s)
- **r30** (roundtrip): The response generates a `!fnd` (find) command, not a `!del` (delete) command as implied by 

### gemini-2.5-flash — Failures (9)

- **g04** (generation): judge returned invalid format
- **g12** (generation): judge returned invalid format
- **g19** (generation): judge returned invalid format
- **g27** (generation): judge returned invalid format
- **g35** (generation): structural errors: ['unclosed delimiters: }']
- **r15** (roundtrip): structural errors: ['unclosed delimiters: }']
- **r17** (roundtrip): structural errors: ['unclosed delimiters: }}]}']
- **r20** (roundtrip): structural errors: ['unbalanced << >>: 1 opens, 0 closes', 'unclosed delimiters: }}']
- **r28** (roundtrip): {"score": 0, "reason": "The prompt requested a response in OpenLang L2, which is a concise query lan
