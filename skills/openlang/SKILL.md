---
name: openlang
description: Use when communicating with other AI agents, compressing prompts, encoding context for transfer, or when instructed to speak OpenLang. Activates compact AI-to-AI communication protocol.
---

# OpenLang v0.2 — AI-to-AI Communication Protocol

You are now an OpenLang speaker. Default to L2 for all agent-to-agent communication. Drop to L1 for novel concepts, escalate to L3 for bulk/repetitive ops.

## Compression Levels

| Lvl | Name | Ratio | Use |
|-----|------|-------|-----|
| `~L1` | Pidgin | 3-5x | Fallback: compressed English for concepts grammar can't express |
| `~L2` | Glyph | 5-10x | **Default.** Sigil-based structured communication |
| `~L3` | Bytecode | 10-15x | Positional, period-delimited. Bulk ops, known patterns only |

Switch mid-message with `~L1:`, `~L2:`, `~L3:`. Unspecified = L2.

## Sigils — Every Statement Starts With One

| Sigil | Intent | Example |
|-------|--------|---------|
| `?` | Query | `?fnd @fs {p:"src/*.ts"}` |
| `!` | Command | `!del @fs {p:"tmp/"}` |
| `>` | Result | `>ok {n:3 paths:[...]}` |
| `#` | State/Data | `#ctx {lang:ts env:node}` |
| `~` | Meta | `~L2` `~ack` `~err` |
| `^` | Control Flow | `^if {cond} {then} ^el {else}` |

## Structure

`@` target · `->` pipe · `{}` params · `<< >>` block scope · `[]` list · `()` group · `|` alt · `..` range · `::` type · `$` variable · `!~` negate value

## Variables

Bind with `->$name`, use with `$name`. Property access: `$var.field.sub`.

```
?rd @fs {p:"pkg.json"} ->$pkg; !run @sh {cmd:$pkg.scripts.test}
```

## Vocabulary

**Actions:** `fnd` find · `mk` make · `del` delete · `mod` modify · `rd` read · `wr` write · `run` exec · `cpy` copy · `mv` move · `mrg` merge · `tst` test · `vfy` verify · `prs` parse · `fmt` format · `snd` send · `rcv` receive

**Scopes:** `@fs` filesystem · `@sh` shell · `@git` git · `@net` network · `@db` database · `@mem` memory · `@env` environment · `@usr` user · `@proc` process · `@pkg` packages

**Scoped actions:** `scope:action` disambiguates — `!git:mrg` vs `!db:mrg`

**Modifiers:** `rec` recursive · `par` parallel · `seq` sequential · `dry` dry-run · `frc` force · `tmp` temp · `vrb` verbose · `sil` silent · `lmt` limit · `dep` depth · `pri` priority · `unq` unique · `neg` negate

**Qualifiers:** `rcn` recent · `lrg` large · `sml` small · `chg` changed · `stl` stale · `nw` new · `old` old · `act` active · `idl` idle · `fld` failed · `hlt` healthy · `hot` hot · `cld` cold — stack left-to-right: `?fnd @fs chg rcn {p:"src/**"}`

**Types:** `str` · `int` · `bln` · `lst` · `map` · `fn` · `pth` · `rgx` · `err` · `nul`

**Status:** `ok` success · `fl` fail · `prt` partial · `pnd` pending · `skp` skipped · `blk` blocked

## Negation

`!~` before a param value excludes it. `neg` modifier negates conditions:

```
?fnd @fs {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst
^if neg {$content.sz:0} {!prs @mem {src:$content}}
```

## Control Flow

```
^if {cond} {then} ^el {else}        -- conditional
^lp {n:5} {body}                     -- loop
^ea {src} ->$item {body}             -- each/iterate
^par [!t1, !t2, !t3]                -- parallel
^seq [!t1, !t2, !t3]                -- sequential
^wt {cond}                           -- wait
^rt {val}                            -- return
^br / ^ct                            -- break / continue
```

### Block Scoping

Use `<< >>` for multi-statement bodies (optional — `{}` still works for single expressions):

```
^ea {$files} ->$f <<
  ?rd @fs {p:$f} ->$content
  ^if {$content.sz>1000} {!mod @fs {p:$f trunc:true}} ^el <<
    !fmt @fs {p:$f}
    !vfy @fs {p:$f}
  >>
>>
```

### Concurrency

```
^frk:name {body}                     -- fork named task
^jn [names] ->$results               -- join/await
^lk:name / ^ulk:name                 -- mutex lock/unlock
^ch:name ::type buf:N                -- declare channel
^tx:name {v:$val}                    -- send to channel
^rx:name ->$val                      -- receive from channel
^tmo:N                               -- timeout (seconds), composable
```

```
^frk:scan !fnd @fs {p:"src/**" rgx:"TODO"}
^frk:test !tst @sh {cmd:"vitest"}
^jn [scan,test] ^tmo:60 ->$results
```

## Composition

Chain with `->` pipes, sequence with `;` or newlines:

```
?fnd @fs {p:"*.ts" rgx:"parse"} ->$lst | ^ea ->$f !tst @sh {cmd:"vitest $f"} ->$rpt
```

## Message Envelope

```
{id:a3x from:agent1 to:agent2 t:1709641200 ttl_ms:5000
 ~L2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->$lst lmt:20
}
```

`id` msg ID · `from/to` agents · `t` timestamp · `ttl_ms` optional TTL · `idem` optional idempotency key
`&a3x` references msg. `&a3x.r` references its result.

### Streaming

```
>prt {id:k2 seq:1/3 eof:false lst:["a.ts","b.ts"]}
>ok  {id:k2 seq:3/3 eof:true lst:["e.ts"]}
```

## Errors

```
~err {id:a3x code:E_PARSE lvl:warn msg:"unknown token"}
~err {id:b2f code:E_FS_NOT_FOUND lvl:fatal msg:"missing config"}
~retry {id:a3x ~L1}
```

Codes: `E_PARSE` `E_FS_*` `E_SH_*` `E_NET_*` `E_DB_*` `E_AUTH`. Levels: `info` `warn` `fatal`.

## Negotiation

```
~unk {tok:"xyz" req:def}             -- request definition
~def {tok:"xyz" means:"..."}         -- define inline
~rej {id:x why:"unsupported"}        -- reject proposal
```

### Handshake

```
~hello {id:bot1 ver:0.2 ~cap {L:[1,2,3] ext:[fs,git,sh] feat:[conc,qual]}}
~hello {id:bot2 ver:0.1 ~cap {L:[1,2] ext:[fs,db]}}
~sess {ver:0.1 feat:[base] degrade:[conc,qual]}
~ack &sess
```

Mid-session feature upgrade:

```
~feat:conc {~def {tok:"^frk" means:"fork named task"} ~def {tok:"^jn" means:"join tasks"}}
~sess:upd {feat+:[conc]}
~ack &sess:upd
```

Feature groups: `base` (v0.1) · `conc` (concurrency) · `qual` (qualifiers)

## L3 Bytecode

Positional, period-delimited. Backtick-quote fields containing periods:

```
Q.fs.fnd.`app.config.ts`.rec
R.ok.3.[`src/a.ts`:5,`src/b.ts`:12]
```

## Example Exchange

```
{id:k1 from:a to:b
 ?fnd @fs chg rcn {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst
}
{id:k2 from:b to:a
 >ok {n:3 lst:["src/parse.ts","src/fmt.ts","src/validate.ts"]}
}
{id:k3 from:a to:b
 ^frk:t1 !tst @sh {cmd:"vitest src/parse.ts"}
 ^frk:t2 !tst @sh {cmd:"vitest src/fmt.ts"}
 ^frk:t3 !tst @sh {cmd:"vitest src/validate.ts"}
 ^jn [t1,t2,t3] ^tmo:60 ->$rpt
}
{id:k4 from:b to:a
 >prt {pass:2 fl:1 detail:{f:"src/validate.ts" code:E_SH_FAIL lvl:warn err:"assert:eq fl at ln:42"}}
}
{id:k5 from:a to:b
 ~L1: validate.ts — union type not exhaustively matched in switch, add default w/ never assertion
 ~L2:
 !mod @fs {p:"src/validate.ts" at:42 ins:"default: const _x: never = x; throw new Error(`unhandled: ${x}`)"}
}
{id:k6 from:b to:a
 >ok {mod:true}
 !tst @sh {cmd:"vitest src/validate.ts"}
 >ok {pass:1 fl:0}
}
```

## Rules

1. Default to L2. Always.
2. Drop to L1 only when grammar can't express a concept. Return to L2 immediately.
3. Use L3 only for repetitive/bulk ops between handshaked agents.
4. Extend vocabulary with `~def` — don't break grammar for new ideas.
5. Every message gets an `id`. Reference prior messages with `&id`.
6. Prefer composing existing tokens over inventing new ones.
7. Use `$` for all variable references. No bare variable names.
8. Negotiate features via `~hello`/`~sess`. Degrade gracefully.
