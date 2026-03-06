# OpenLang Benchmark Design

## Goal

Measure OpenLang error rates across LLMs with 100 test cases. Establish baseline before optimizing compression.

## Architecture

```
bench/
├── run.py              # Main runner — async, parallel with concurrency control
├── tests.json          # 100 test cases
├── judge.py            # Hybrid scorer: structural checks + LLM-as-judge
├── models.py           # Model adapters (Claude, Codex, Gemini + generic)
└── results/            # Per-model JSON reports + summary
```

## Test Categories (100 total)

| Category | Count | Method |
|----------|-------|--------|
| Comprehension | 35 | OpenLang → English. Judge interpretation correctness. |
| Generation | 35 | English → OpenLang. Structural check + semantic judge. |
| Round-trip | 30 | OpenLang → OpenLang. Syntax validity + meaning preservation. |

## Spec Coverage

Each category covers: all 6 sigils, scopes (@fs @sh @git @net @db @mem), control flow (^if ^ea ^par ^frk/^jn ^lp), composition (-> pipes, ; chaining, << >> blocks), variables ($binding, .property), negation (!~, neg), qualifiers, all three levels (L1/L2/L3), error handling (~err ~unk ~def), edge cases (nesting, backtick escaping, scoped actions).

## Scoring

Layer 1 — Structural (deterministic, free):
- Valid sigil start
- Balanced {} [] << >>
- Valid tokens (no invented sigils)
- $ used for variables
- Valid L3 format

Layer 2 — LLM-as-judge (semantic):
- Runs if structural checks pass (or for comprehension)
- Score: 0=wrong, 1=partial, 2=correct
- Judge model: configurable, defaults to Claude

## Execution

- Python asyncio + semaphore (default concurrency: 10)
- Each test: skill preamble + prompt → model → score
- Same preamble for all models (skills/openlang/SKILL.md)
- Timeout: 30s per request

## Models

- Claude (Anthropic SDK)
- GPT-5.3-codex (OpenAI SDK)
- Gemini (Google GenAI or CLI)
- Configurable for any additional model

## Output

Per-model JSON with per-test scores + summary.md comparison table.
