# OpenLang Benchmark Results

Run: 2026-03-05 21:52

| Model | Comprehension | Generation | Round-trip | Overall |
|-------|--------------|------------|------------|---------|
| codex | 35/35 (100%) | 25/35 (71%) | 22/30 (73%) | 86.0% |
| gemini-2.5-flash | 27/35 (77%) | 27/35 (77%) | 23/30 (77%) | 82.5% |

### codex — Failures (10)

- **g10** (generation): judge returned invalid format
- **g12** (generation): judge returned invalid format
- **g14** (generation): judge returned invalid format
- **g23** (generation): judge returned invalid format
- **g24** (generation): judge returned invalid format
- **g28** (generation): judge returned invalid format
- **g34** (generation): judge returned invalid format
- **r14** (roundtrip): judge returned invalid format
- **r25** (roundtrip): judge returned invalid format
- **r28** (roundtrip): judge returned invalid format

### gemini-2.5-flash — Failures (12)

- **c17** (comprehension): The response only translates the very first part of the first line, missing the type, buffer capacity, the producer fork, and the receive operation entirely. It comprehends only a tiny fraction of the input.
- **g12** (generation): judge returned invalid format
- **g18** (generation): structural errors: ['unbalanced << >>: 2 opens, 0 closes']
- **g22** (generation): structural errors: ["line doesn't start with sigil: '`R.ok.2.[`src/main.config.ts`:10,`src/ap'"]
- **g26** (generation): structural errors: ['unclosed delimiters: }']
- **g28** (generation): judge error: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}}
- **r06** (roundtrip): structural errors: ["line doesn't start with sigil: 'agents:{active:4 idle:2},'", "line doesn't start with sigil: 'mem:{pct:83},'", "line doesn't start with sigil: 'disk:{sts:hlt}'"]
- **r17** (roundtrip): structural errors: ['unclosed delimiters: }}}]}']
- **r20** (roundtrip): structural errors: ['unbalanced << >>: 2 opens, 0 closes', 'unclosed delimiters: }']
- **r25** (roundtrip): structural errors: ['unclosed delimiters: }']
- **r28** (roundtrip): structural errors: ['unclosed delimiters: }}']
- **r29** (roundtrip): no reason
