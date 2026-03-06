# OpenLang

A compact, layered language for AI-to-AI communication. Designed for maximum token efficiency across agent orchestration, API calls, and stored context artifacts.

## Compression Levels

| Level | Name | Compression | Use Case |
|-------|------|-------------|----------|
| `~L1` | Pidgin | 3-5x | Novel concepts, nuance, fallback when grammar can't express something |
| `~L2` | Glyph | 5-10x | Default working mode |
| `~L3` | Bytecode | 10-15x | Repetitive ops, bulk data, known patterns |

Speakers shift between levels mid-message as needed. Default is L2 if unspecified.

## Core Syntax

### Sigils

Every statement starts with a sigil declaring intent:

| Sigil | Meaning | Example |
|-------|---------|---------|
| `?` | Query | `?fnd @fs {p:"src/*.ts"}` |
| `!` | Command | `!del @fs {p:"tmp/"}` |
| `>` | Result | `>ok {found:3 paths:[...]}` |
| `#` | State/Data | `#ctx {lang:ts env:node deps:[react,next]}` |
| `~` | Meta/Control | `~L2` `~ack` `~err:parse` |
| `^` | Control Flow | `^if {cond} !do {x} ^el !do {y}` |

### Structural Tokens

| Token | Meaning |
|-------|---------|
| `@` | Target/scope |
| `->` | Output format / pipe |
| `{}` | Parameter block |
| `[]` | List/array |
| `()` | Grouping / precedence |
| `\|` | Separator / alternative |
| `..` | Range |
| `::` | Type annotation |

## Vocabulary

### Actions

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `fnd` | find/search | `mk` | make/create |
| `del` | delete | `mod` | modify/edit |
| `rd` | read | `wr` | write |
| `run` | execute | `cpy` | copy |
| `mv` | move | `mrg` | merge |
| `tst` | test | `vfy` | verify |
| `prs` | parse | `fmt` | format |
| `snd` | send | `rcv` | receive |

### Scopes (@targets)

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `@fs` | filesystem | `@sh` | shell |
| `@git` | git repo | `@net` | network/API |
| `@db` | database | `@mem` | memory/context |
| `@env` | environment | `@usr` | user |
| `@proc` | process | `@pkg` | packages |

### Modifiers

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `rec` | recursive | `par` | parallel |
| `seq` | sequential | `dry` | dry run |
| `frc` | force | `tmp` | temporary |
| `vrb` | verbose | `sil` | silent |
| `lmt` | limit | `dep` | depth |
| `pri` | priority | `unq` | unique |

### Types (:: annotations)

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `str` | string | `int` | integer |
| `bln` | boolean | `lst` | list |
| `map` | key-value map | `fn` | function |
| `pth` | path | `rgx` | regex |
| `err` | error | `nul` | null/none |

### Response Status

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `ok` | success | `fl` | fail |
| `prt` | partial | `pnd` | pending |
| `skp` | skipped | `blk` | blocked |

## Control Flow

```
^if {cond} {then} ^el {else}
^lp {n:5} {body}                    -- loop n times
^ea {src} ->item {body}             -- each/iterate
^par [!task1, !task2, !task3]       -- parallel execution
^seq [!task1, !task2, !task3]       -- sequential execution
^wt {cond}                          -- wait/block until
^rt {val}                           -- return value
^br                                 -- break
^ct                                 -- continue
```

## Composition & Piping

Statements chain with `->` pipes and `;` sequencing:

```
?fnd @fs {p:"*.ts" fn:parse} ->lst | ^ea ->f !tst @sh {cmd:"vitest {f}"} ->rpt
```

*Find all .ts files containing function "parse", for each run vitest, output report.*

Multi-statement blocks use `;` or newlines:

```
#ctx {proj:openlang phase:design}
?rd @fs {p:"src/main.ts"} ->src
!mod @mem {k:analysis v:{src.imports}}
>ok {stored:true}
```

## Layer Examples

### L1 — Pidgin (compressed English fallback)

```
~L1: need concept — token weight decay across conv window, older ctx less reliable
~L2:
!mk @mem {k:decay fn:{age->1/(1+age)}}
```

Use L1 when the grammar can't express a novel concept. Drop back to L2/L3 once formalized.

### L2 — Glyph (default)

```
?fnd @fs {p:"src/**" rgx:"TODO"} ->lst lmt:20
>ok {n:3 lst:["src/a.ts:5","src/b.ts:12","src/c.ts:3"]}
```

### L3 — Bytecode (maximum density)

```
~L3:
Q.fs.fnd."*.ts".fn:parse.3.pth+ln
R.ok.3.[src/a.ts:5,src/b.ts:12,src/c.ts:3]
```

L3 format: `sigil.scope.action.params...` — strictly positional, period-delimited.

## Message Envelope

Every exchange is wrapped:

```
{id:a3x from:agent1 to:agent2 t:1709641200
 ~L2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->lst lmt:20
}
```

- `id` — short message ID for reference
- `from/to` — agent identifiers
- `t` — timestamp (unix)
- Body follows level declaration

**References:** `&a3x` references a previous message by ID. `&a3x.r` references its result.

## Error Handling & Negotiation

```
~err {id:a3x code:prs msg:"unknown token: xyz"}
~retry {id:a3x ~L1}                -- retry, drop to L1
~unk {tok:"xyz" req:def}           -- unknown token, request definition
~def {tok:"xyz" means:"..."}       -- define new token inline
~cap {L:[1,2] ext:[fs,git,sh]}    -- capability declaration
```

### Agent Handshake

Agents negotiate capabilities on first contact:

```
~hello {id:bot1 ~cap {L:[1,2,3] ext:[fs,git,sh,net]} ver:0.1}
~hello {id:bot2 ~cap {L:[1,2] ext:[fs,db]} ver:0.1}
```

## Learning OpenLang

OpenLang is designed to be taught to an AI via a bootstrap skill — a single prompt that teaches the grammar and vocabulary, after which the AI speaks it natively for the rest of the session.

The language is learnable because:
- Sigils provide immediate intent classification
- Short tokens compose freely for novel expressions
- L1 fallback means you never get stuck — drop to compressed English
- Agents can define new tokens inline with `~def`
- Capability negotiation prevents mismatched expectations

## Version

OpenLang v0.1 — initial design.
