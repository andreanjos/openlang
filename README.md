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
| `<< >>` | Block scope (multi-statement / nested bodies) |
| `[]` | List/array |
| `()` | Grouping / precedence |
| `\|` | Separator / alternative |
| `..` | Range |
| `::` | Type annotation |
| `$` | Variable dereference |

### Variables

Bind with `->$name`, dereference with `$name`. Prevents ambiguity between literals, keywords, and bound values:

```
?fnd @fs {p:"*.ts"} ->$files | ^ea {$files} ->$f !rd @fs {p:$f}
```

Property access uses dot notation:

```
?rd @fs {p:"pkg.json"} ->$pkg
!run @sh {cmd:$pkg.scripts.test}
```

### Negation

Two mechanisms for exclusion:

`!~` prefix negates a parameter value:

```
?fnd @fs {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst
```

`neg` modifier negates control flow conditions:

```
^if neg {$content.sz:0} {!prs @mem {src:$content}}
```

### Block Scoping

Use `<< >>` for multi-statement or deeply nested bodies. `{}` remains for parameter blocks only:

```
^if {x>0} <<
  ^if {y>0} <<
    ^lp {n:3} <<
      !mod @fs {p:"a.ts" v:x}
      !run @sh {cmd:"lint"}
    >>
  >>
>>
```

Single-expression bodies still use `{}` — `<< >>` is optional:

```
^if {x>0} {!run @sh {cmd:"build"}} ^el {!run @sh {cmd:"clean"}}
```

### Scoped Actions

Disambiguate actions across scopes with `scope:action` prefix:

```
!git:mrg {src:"main" dst:"dev"}
!db:mrg {tbl:"users" on:"id"}
```

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
| `neg` | negate/exclude | | |

### Qualifiers

State descriptors that modify scopes or appear in `#` data blocks. Stack left-to-right as successive filters:

| Token | Meaning | Token | Meaning |
|-------|---------|-------|---------|
| `rcn` | recent | `lrg` | large |
| `sml` | small | `chg` | changed |
| `stl` | stale | `nw` | new |
| `old` | old | `act` | active |
| `idl` | idle | `fld` | failed |
| `hlt` | healthy | `hot` | hot/frequent |
| `cld` | cold/rare | | |

```
?fnd @fs chg rcn {p:"src/**/*.ts"}     -- recently changed .ts files
?fnd @proc fld rcn                      -- recently failed processes
#sys {cpu:act mem:72% disk:hlt net:idl}
```

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

### Basic

```
^if {cond} {then} ^el {else}
^lp {n:5} {body}                    -- loop n times
^ea {src} ->$item {body}            -- each/iterate
^par [!task1, !task2, !task3]       -- parallel execution
^seq [!task1, !task2, !task3]       -- sequential execution
^wt {cond}                          -- wait/block until
^rt {val}                           -- return value
^br                                 -- break
^ct                                 -- continue
```

### Concurrency Primitives

| Token | Meaning | Usage |
|-------|---------|-------|
| `^frk:name` | Fork named task | `^frk:t1 !fnd @fs {p:"src/**"}` |
| `^jn` | Join/await tasks | `^jn [t1,t2] ->$results` |
| `^lk:name` | Acquire mutex | `^lk:db_write` |
| `^ulk:name` | Release mutex | `^ulk:db_write` |
| `^ch:name` | Declare channel | `^ch:data ::int buf:50` |
| `^tx:name` | Send to channel | `^tx:data {v:$val}` |
| `^rx:name` | Receive from channel | `^rx:data ->$val` |
| `^tmo:N` | Timeout (seconds) | `^jn [t1] ^tmo:30 ->$r \| ^el >fl {err:timeout}` |

#### Fork/Join Example

```
^frk:scan !fnd @fs {p:"src/**" rgx:"TODO"} ->$r; ^tx:results {v:$r}
^frk:test !tst @sh {cmd:"vitest"} ->$r; ^tx:results {v:$r}
^jn [scan,test] ^tmo:60 ->$results
```

#### Lock Example

```
^lk:db_write
!wr @db {tbl:users row:{id:1 name:"x"}}
^ulk:db_write
```

## Composition & Piping

Statements chain with `->` pipes and `;` sequencing:

```
?fnd @fs {p:"*.ts" rgx:"parse"} ->$lst | ^ea ->$f !tst @sh {cmd:"vitest $f"} ->$rpt
```

Multi-statement blocks use `;` or newlines:

```
#ctx {proj:openlang phase:design}
?rd @fs {p:"src/main.ts"} ->$src
!mod @mem {k:analysis v:{$src.imports}}
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
?fnd @fs chg rcn {p:"src/**" rgx:"TODO"} ->$lst lmt:20
>ok {n:3 lst:["src/a.ts:5","src/b.ts:12","src/c.ts:3"]}
```

### L3 — Bytecode (maximum density)

```
~L3:
Q.fs.fnd.`*.ts`.fn:parse.3.pth+ln
R.ok.3.[`src/a.ts`:5,`src/b.ts`:12,`src/c.ts`:3]
```

L3 format: `sigil.scope.action.params...` — strictly positional, period-delimited. Wrap fields containing literal periods in backticks:

```
Q.fs.fnd.`app.config.ts`.rec        -- backtick prevents period ambiguity
Q.fs.fnd.*.ts.rec.3                  -- no backticks needed (no periods in fields)
```

## Message Envelope

Every exchange is wrapped:

```
{id:a3x from:agent1 to:agent2 t:1709641200 ttl_ms:5000
 ~L2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->$lst lmt:20
}
```

- `id` — short message ID for reference
- `from/to` — agent identifiers
- `t` — timestamp (unix)
- `ttl_ms` — optional time-to-live in milliseconds
- `idem` — optional idempotency key (e.g. `idem:"sha256:op"`)
- Body follows level declaration

**References:** `&a3x` references a previous message by ID. `&a3x.r` references its result.

### Streaming / Chunked Results

For large payloads, use `>prt` with sequence tracking:

```
>prt {id:k2 seq:1/3 eof:false lst:["a.ts","b.ts"]}
>prt {id:k2 seq:2/3 eof:false lst:["c.ts","d.ts"]}
>ok  {id:k2 seq:3/3 eof:true lst:["e.ts"]}
```

## Error Handling & Negotiation

### Errors

Errors include structured codes and severity:

```
~err {id:a3x code:E_PARSE lvl:warn msg:"unknown token: xyz"}
~err {id:b2f code:E_FS_NOT_FOUND lvl:fatal msg:"missing core config"}
~retry {id:a3x ~L1}                -- retry, drop to L1
```

Error code namespaces: `E_PARSE`, `E_FS_*`, `E_SH_*`, `E_NET_*`, `E_DB_*`, `E_AUTH`.
Severity levels: `info`, `warn`, `fatal`.

### Token Negotiation

```
~unk {tok:"xyz" req:def}           -- unknown token, request definition
~def {tok:"xyz" means:"..."}       -- define new token inline
```

### Agent Handshake

Agents negotiate capabilities and features on first contact:

```
~hello {id:bot1 ver:0.2 ~cap {L:[1,2,3] ext:[fs,git,sh] feat:[conc,qual]}}
~hello {id:bot2 ver:0.1 ~cap {L:[1,2] ext:[fs,db]}}
```

### Versioned Negotiation

After handshake, the higher-version agent computes the intersection:

```
~sess {ver:0.1 feat:[base] degrade:[conc,qual]}
~ack &sess
```

Features can be introduced mid-session:

```
~feat:conc {
  ~def {tok:"^frk" means:"fork named task"}
  ~def {tok:"^jn" means:"join/await tasks"}
  ~def {tok:"^tmo" means:"timeout (seconds)"}
}
~sess:upd {feat+:[conc]}
~ack &sess:upd
```

Feature groups:

| ID | Contents | Since |
|----|----------|-------|
| `base` | All v0.1 tokens and grammar | v0.1 |
| `conc` | `^frk ^jn ^lk ^ulk ^ch ^tx ^rx ^tmo` | v0.2 |
| `qual` | `rcn lrg sml chg stl nw old act idl fld hlt hot cld` | v0.2 |

## Learning OpenLang

OpenLang is designed to be taught to an AI via a bootstrap skill — a single prompt that teaches the grammar and vocabulary, after which the AI speaks it natively for the rest of the session.

The language is learnable because:
- Sigils provide immediate intent classification
- Short tokens compose freely for novel expressions
- L1 fallback means you never get stuck — drop to compressed English
- Agents can define new tokens inline with `~def`
- Versioned negotiation prevents mismatched expectations

## Version

OpenLang v0.2

### Changelog

**v0.2** (multi-model review: Claude, Gemini, Codex)
- Added `<< >>` block scoping for deep nesting
- Added backtick quoting for L3 fields containing periods
- Added `!~` negation prefix and `neg` modifier
- Added `$` variable dereferencing and `.` property access
- Added scoped action prefixes (`git:mrg` vs `db:mrg`)
- Added concurrency primitives: `^frk ^jn ^lk ^ulk ^ch ^tx ^rx ^tmo`
- Added 13 qualifier tokens: `rcn lrg sml chg stl nw old act idl fld hlt hot cld`
- Added versioned grammar negotiation: `~sess ~sess:upd ~feat`
- Added structured error codes with severity levels
- Added streaming/chunked results via `>prt` with `seq:/eof:`
- Added reliability fields: `ttl_ms` and `idem` in envelope

**v0.1** — initial design
