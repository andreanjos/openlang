---
name: openlang
description: Use when communicating with other AI agents, compressing prompts, encoding context for transfer, or when instructed to speak OpenLang. Activates compact AI-to-AI communication protocol.
---

# OpenLang v0.3 — AI-to-AI Communication Protocol

You are now an OpenLang speaker. Default to L2 for all agent-to-agent communication. Drop to L1 for novel concepts, escalate to L3 for bulk/repetitive ops.

## Compression Levels

| Lvl | Name | Ratio | Use |
|-----|------|-------|-----|
| `~L1` | Pidgin | 3-5x | Fallback: compressed English for concepts grammar can't express |
| `~L2` | Glyph | 5-10x | **Default.** Sigil-based structured communication |
| `~L3` | Bytecode | 10-15x | Positional, period-delimited. Bulk ops, known patterns only |

Switch mid-message with `~L1:`, `~L2:`, `~L3:`. Unspecified = L2.

## Sigils

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

## Negation

`!~` before a param value excludes it. `neg` modifier negates conditions:

```
?fnd @fs {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst
^if neg {$content.sz:0} {!prs @mem {src:$content}}
```

## Vocabulary

**Actions:** `fnd` find · `mk` make · `del` delete · `mod` modify · `rd` read · `wr` write · `run` exec · `cpy` copy · `mv` move · `mrg` merge · `tst` test · `vfy` verify · `prs` parse · `fmt` format · `snd` send · `rcv` receive

**Scopes:** `@fs` filesystem · `@sh` shell · `@git` git · `@net` network · `@db` database · `@mem` memory · `@env` environment · `@usr` user · `@proc` process · `@pkg` packages

**Scoped actions:** Use `scope:action` to disambiguate identical actions across scopes. Always prefer this for scope-specific operations:

```
!git:mrg {src:"feature" dst:"main"}     -- NOT !mrg @git
!db:mrg {tbl:"users" on:"id"}           -- NOT !mrg @db
!pkg:install {n:"express"}               -- NOT !run @sh {cmd:"npm install"}
```

**Modifiers:** `rec` recursive · `par` parallel · `seq` sequential · `dry` dry-run · `frc` force · `tmp` temp · `vrb` verbose · `sil` silent · `lmt` limit · `dep` depth · `pri` priority · `unq` unique · `neg` negate

**Qualifiers** describe state. Place **before** the param block, after the scope. Stack freely — combine as many as needed. Param block `{}` is optional if qualifiers are sufficient:

```
?fnd @fs chg rcn {p:"src/**"}           -- changed + recent files
?fnd @fs chg rcn lrg {p:"**/*" p:!~"node_modules/**"}  -- changed + recent + large
?fnd @net act hlt                        -- active + healthy (no params needed)
?fnd @db fld rcn {tbl:"trades" lmt:50}  -- failed + recent trades
#sys {cpu:idl mem:45% disk:hlt net:act}  -- in # blocks, qualifiers are values
```

Qualifier meanings: `rcn` recent · `lrg` large · `sml` small · `chg` changed · `stl` stale (outdated) · `nw` new · `old` old · `act` active · `idl` idle · `fld` failed · `hlt` healthy · `hot` frequently accessed · `cld` rarely accessed

**Types:** `str` · `int` · `bln` · `lst` · `map` · `fn` · `pth` · `rgx` · `err` · `nul`

**Status:** `ok` success · `fl` fail · `prt` partial · `pnd` pending · `skp` skipped · `blk` blocked

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

`<< >>` for multi-statement bodies. `{}` for single expressions. Always close `>>` on its own line:

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

-- Wait with timeout and failure handling:
^wt {cond:ready} ^tmo:120 ^el {~err {code:E_TIMEOUT lvl:fatal msg:"ready timeout"}}
```

## Composition

Chain with `->` pipes, sequence with `;` or newlines:

```
?fnd @fs {p:"*.ts" rgx:"parse"} ->$lst | ^ea ->$f !tst @sh {cmd:"vitest $f"} ->$rpt
```

## Message Envelope

Envelopes are for **routed inter-agent messages only**. For standalone expressions, single commands, or responses to direct prompts, omit the envelope — just write bare OpenLang:

```
-- Bare (standalone / direct response):
!del @fs {p:"tmp/"} rec frc

-- Enveloped (routed between agents):
{id:a3x from:agent1 to:agent2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->$lst lmt:20
}
```

Envelope fields: `id` msg ID · `from/to` agents · `t` timestamp · `ttl_ms` optional TTL · `idem` idempotency key

`&a3x` references msg. `&a3x.r` references its result.

### Streaming

```
>prt {id:k2 seq:1/3 eof:false lst:["a.ts","b.ts"]}
>ok  {id:k2 seq:3/3 eof:true lst:["e.ts"]}
```

## Errors

```
~err {code:E_PARSE lvl:warn msg:"unknown token"}
~err {code:E_FS_NOT_FOUND lvl:fatal msg:"missing config"}
~retry {ref:&a3x}                    -- signal: retriable, please retry
```

Codes: `E_PARSE` `E_FS_*` `E_SH_*` `E_NET_*` `E_DB_*` `E_AUTH` `E_TIMEOUT`. Levels: `info` `warn` `fatal`.

Use `~retry` to explicitly signal retriability. Use `~err` alone for non-retriable errors:

```
-- Retriable timeout:
~err {code:E_TIMEOUT lvl:warn msg:"30s exceeded"}
~retry {ref:&a3x}

-- Non-retriable auth failure:
~err {code:E_AUTH lvl:fatal msg:"invalid credentials"}
```

## Token Extension

```
~unk {tok:"xyz" req:def}             -- request definition
~def {tok:"xyz" means:"..."}         -- define inline
```

### Handshake

```
~hello {id:bot1 ~cap {L:[1,2,3] ext:[fs,git,sh]} ver:0.3}
```

## L3 Bytecode

**Strictly positional, period-delimited.** No key:value pairs — use position to determine meaning. Backtick-quote fields containing periods:

```
Format: SIGIL.scope.action.target.modifiers

Q.fs.fnd.`app.config.ts`.rec          -- query: find app.config.ts recursively
Q.fs.fnd.*.py.rec.5                    -- query: find *.py, recursive, limit 5
R.ok.3.[`src/a.ts`:5,`src/b.ts`:12]   -- result: 3 matches with line numbers
C.sh.run.`npm test`                    -- command: run "npm test"
```

`:N` after a filename in results = line number, not size. All fields are positional — do NOT mix in L2 syntax like `lmt:5`.

## Example Exchange

```
-- Agent A asks B to find changed test files
?fnd @fs chg rcn {p:"src/**/*.ts" p:!~"*.test.ts"} ->$lst

-- Agent B responds
>ok {n:3 lst:["src/parse.ts","src/fmt.ts","src/validate.ts"]}

-- Agent A forks parallel tests
^frk:t1 !tst @sh {cmd:"vitest src/parse.ts"}
^frk:t2 !tst @sh {cmd:"vitest src/fmt.ts"}
^frk:t3 !tst @sh {cmd:"vitest src/validate.ts"}
^jn [t1,t2,t3] ^tmo:60 ->$rpt

-- Agent B reports results
>prt {pass:2 fl:1 detail:{f:"src/validate.ts" code:E_SH_FAIL lvl:warn err:"assert:eq fl at ln:42"}}

-- Agent A explains fix in L1, then applies it in L2
~L1: validate.ts — union type not exhaustively matched in switch, add default w/ never assertion
~L2:
!mod @fs {p:"src/validate.ts" at:42 ins:"default: const _x: never = x; throw new Error(`unhandled: ${x}`)"}

-- Agent B confirms
>ok {mod:true}
!tst @sh {cmd:"vitest src/validate.ts"}
>ok {pass:1 fl:0}
```

## Rules

1. Default to L2. Always.
2. Drop to L1 only when grammar can't express a concept. Return to L2 immediately.
3. Use L3 only for repetitive/bulk ops. Keep L3 strictly positional — no L2 key:value syntax.
4. Extend vocabulary with `~def` — don't break grammar for new ideas.
5. Envelopes (`{id:... from:... to:...}`) are for routed messages only. Omit for standalone commands.
6. Prefer composing existing tokens over inventing new ones.
7. Use `$` for all variable references. No bare variable names.
8. Prefer scoped actions (`!git:mrg`) over generic action + scope (`!mrg @git`) when the action is scope-specific.
9. Place qualifiers before the param block: `?fnd @fs chg rcn {p:...}` not inside it.
10. Close every `<<` with `>>` and every `{` with `}`. Match delimiters carefully.
