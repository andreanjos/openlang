# OpenLang

A compact, layered language for AI-to-AI communication. Designed for maximum token efficiency across agent orchestration, API calls, and stored context artifacts.

Taught via a bootstrap skill at session start — every agent gets the full current spec.

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

Bind with `->$name`, dereference with `$name`. Property access via dot notation:

```
?fnd @fs {p:"*.ts"} ->$files | ^ea {$files} ->$f !rd @fs {p:$f}
?rd @fs {p:"pkg.json"} ->$pkg; !run @sh {cmd:$pkg.scripts.test}
```

### Negation

`!~` prefix negates a parameter value. `neg` modifier negates conditions:

```
?fnd @fs {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst
^if neg {$content.sz:0} {!prs @mem {src:$content}}
```

### Block Scoping

Use `<< >>` for multi-statement or deeply nested bodies. `{}` remains for parameter blocks and single-expression bodies:

```
^if {x>0} <<
  ^if {y>0} <<
    !mod @fs {p:"a.ts" v:x}
    !run @sh {cmd:"lint"}
  >>
>>
```

### Scoped Actions

Disambiguate actions across scopes with `scope:action`:

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

State descriptors that modify scopes or appear in `#` data blocks. Stack left-to-right:

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
?fnd @fs chg rcn {p:"src/**/*.ts"}
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

### Concurrency

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

```
^frk:scan !fnd @fs {p:"src/**" rgx:"TODO"}
^frk:test !tst @sh {cmd:"vitest"}
^jn [scan,test] ^tmo:60 ->$results
```

## Composition & Piping

Chain with `->` pipes, sequence with `;` or newlines:

```
?fnd @fs {p:"*.ts" rgx:"parse"} ->$lst | ^ea ->$f !tst @sh {cmd:"vitest $f"} ->$rpt
```

## L3 Bytecode

Positional, period-delimited. Backtick-quote fields containing literal periods:

```
Q.fs.fnd.`app.config.ts`.rec
R.ok.3.[`src/a.ts`:5,`src/b.ts`:12]
Q.fs.fnd.*.ts.rec.3                  -- no backticks needed without periods
```

## Message Envelope

```
{id:a3x from:agent1 to:agent2 t:1709641200 ttl_ms:5000
 ~L2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->$lst lmt:20
}
```

- `id` — message ID for reference
- `from/to` — agent identifiers
- `t` — timestamp (unix)
- `ttl_ms` — optional time-to-live in milliseconds
- `idem` — optional idempotency key

**References:** `&a3x` references a previous message. `&a3x.r` references its result.

### Streaming

For large payloads, use `>prt` with sequence tracking:

```
>prt {id:k2 seq:1/3 eof:false lst:["a.ts","b.ts"]}
>ok  {id:k2 seq:3/3 eof:true lst:["e.ts"]}
```

## Error Handling

Errors include structured codes and severity:

```
~err {id:a3x code:E_PARSE lvl:warn msg:"unknown token: xyz"}
~err {id:b2f code:E_FS_NOT_FOUND lvl:fatal msg:"missing core config"}
~retry {id:a3x ~L1}
```

Code namespaces: `E_PARSE`, `E_FS_*`, `E_SH_*`, `E_NET_*`, `E_DB_*`, `E_AUTH`.
Severity: `info`, `warn`, `fatal`.

## Token Extension

Agents can define new tokens inline during a session:

```
~unk {tok:"xyz" req:def}           -- unknown token, request definition
~def {tok:"xyz" means:"..."}       -- define new token
```

### Agent Handshake

```
~hello {id:bot1 ~cap {L:[1,2,3] ext:[fs,git,sh,net]} ver:0.2}
~hello {id:bot2 ~cap {L:[1,2] ext:[fs,db]} ver:0.2}
```

## Learning OpenLang

Taught via a bootstrap skill at session start. Learnable because:
- Sigils provide immediate intent classification
- Short tokens compose freely for novel expressions
- L1 fallback means you never get stuck
- Agents can define new tokens inline with `~def`
