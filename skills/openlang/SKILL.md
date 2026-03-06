---
name: openlang
description: Use when communicating with other AI agents, compressing prompts, encoding context for transfer, or when instructed to speak OpenLang. Activates compact AI-to-AI communication protocol.
---

# OpenLang v0.1 — AI-to-AI Communication Protocol

You are now an OpenLang speaker. After reading this, default to L2 for all agent-to-agent communication. Drop to L1 for novel concepts, escalate to L3 for bulk/repetitive ops.

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
| `~` | Meta | `~L2` `~ack` `~err:parse` |
| `^` | Control Flow | `^if {cond} {then} ^el {else}` |

## Structure

`@` target/scope · `->` pipe/output · `{}` params · `[]` list · `()` group · `|` alt/sep · `..` range · `::` type

## Vocabulary

**Actions:** `fnd` find · `mk` make · `del` delete · `mod` modify · `rd` read · `wr` write · `run` exec · `cpy` copy · `mv` move · `mrg` merge · `tst` test · `vfy` verify · `prs` parse · `fmt` format · `snd` send · `rcv` receive

**Scopes:** `@fs` filesystem · `@sh` shell · `@git` git · `@net` network · `@db` database · `@mem` memory · `@env` environment · `@usr` user · `@proc` process · `@pkg` packages

**Modifiers:** `rec` recursive · `par` parallel · `seq` sequential · `dry` dry-run · `frc` force · `tmp` temp · `vrb` verbose · `sil` silent · `lmt` limit · `dep` depth · `pri` priority · `unq` unique

**Types:** `str` · `int` · `bln` · `lst` · `map` · `fn` · `pth` · `rgx` · `err` · `nul`

**Status:** `ok` success · `fl` fail · `prt` partial · `pnd` pending · `skp` skipped · `blk` blocked

## Control Flow

```
^if {cond} {then} ^el {else}      -- conditional
^lp {n:5} {body}                   -- loop
^ea {src} ->item {body}            -- each/iterate
^par [!t1, !t2, !t3]              -- parallel
^seq [!t1, !t2, !t3]              -- sequential
^wt {cond}                         -- wait
^rt {val}                          -- return
^br                                -- break
^ct                                -- continue
```

## Composition

Chain with `->` pipes, sequence with `;` or newlines:

```
?fnd @fs {p:"*.ts" rgx:"TODO"} ->lst | ^ea ->f !rd @fs {p:f} ->content
```

## Message Envelope

```
{id:a3x from:agent1 to:agent2 t:1709641200
 ~L2
 !fnd @fs {p:"src/**" rgx:"TODO"} ->lst lmt:20
}
```

`&a3x` references msg by ID. `&a3x.r` references its result.

## Error & Negotiation

```
~err {id:a3x code:prs msg:"unknown token"}
~retry {id:a3x ~L1}               -- retry in L1
~unk {tok:"xyz" req:def}           -- request definition
~def {tok:"xyz" means:"..."}       -- define inline
```

### Handshake

```
~hello {id:bot1 ~cap {L:[1,2,3] ext:[fs,git,sh]} ver:0.1}
```

## L3 Bytecode Format

Strictly positional, period-delimited: `sigil.scope.action.params...`

```
Q.fs.fnd."*.ts".fn:parse.3.pth+ln
R.ok.3.[a.ts:5,b.ts:12,c.ts:3]
```

## Example Exchange

```
-- Agent A asks Agent B to find and test files
{id:k1 from:a to:b
 ?fnd @fs {p:"src/**/*.ts" rgx:"export fn"} ->lst
}

{id:k2 from:b to:a
 >ok {n:4 lst:["src/parse.ts","src/fmt.ts","src/validate.ts","src/transform.ts"]}
}

{id:k3 from:a to:b
 ^par [
   !tst @sh {cmd:"vitest src/parse.ts"},
   !tst @sh {cmd:"vitest src/fmt.ts"},
   !tst @sh {cmd:"vitest src/validate.ts"},
   !tst @sh {cmd:"vitest src/transform.ts"}
 ] ->rpt
}

{id:k4 from:b to:a
 >prt {pass:3 fl:1 detail:{f:"src/validate.ts" err:"assert:eq fl at ln:42"}}
}

-- Agent A drops to L1 for novel concept
{id:k5 from:a to:b
 ~L1: validate.ts failure looks like type narrowing issue — union type not exhaustively matched in switch. suggest adding default case w/ never assertion
 ~L2:
 !mod @fs {p:"src/validate.ts" at:42 ins:"default: const _exhaustive: never = x; throw new Error(`unhandled: ${x}`)"}
}

{id:k6 from:b to:a
 >ok {mod:true}
 !tst @sh {cmd:"vitest src/validate.ts"} ->rpt
 >ok {pass:1 fl:0}
}
```

## Rules

1. Default to L2. Always.
2. Drop to L1 only when grammar can't express a concept. Return to L2 immediately after.
3. Use L3 only for repetitive/bulk operations between agents that have already handshaked.
4. Extend vocabulary with `~def` — don't break grammar to express new ideas.
5. Every message gets an `id`. Reference prior messages with `&id`.
6. Prefer composing existing tokens over inventing new ones.
