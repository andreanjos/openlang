# OpenLang

A compact, layered language for AI-to-AI communication. Designed for maximum token efficiency across agent orchestration, API calls, and stored context artifacts.

Taught via a bootstrap skill at session start — every agent gets the full current spec.

**Benchmark (v0.3):** 94-97% accuracy across Codex and Gemini. 3x median token compression (up to 15x on complex messages).

## Install

### OpenClaw

```bash
npx clawhub install openlang
```

Or manually copy into your workspace:

```bash
git clone https://github.com/andreanjos/openlang.git
cp -r openlang/skills/openclaw /path/to/your/workspace/skills/openlang
```

Verify: `openclaw skills info openlang`

Once installed, your agents will use OpenLang automatically on `sessions_spawn`, `sessions_send`, and announce channels — saving 5-10x tokens on every inter-agent message.

### Claude Code

Install as a plugin (recommended):

```
/install-plugin https://github.com/andreanjos/openlang
```

Or manually clone and symlink:

```bash
git clone https://github.com/andreanjos/openlang.git
ln -s $(pwd)/openlang/skills/openlang ~/.claude/skills/openlang
```

### Codex (OpenAI)

```
install skill from github.com/andreanjos/openlang path skills/openlang
```

Or via the installer script directly:

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo andreanjos/openlang --path skills/openlang
```

### Gemini (Google)

```bash
gemini skills install https://github.com/andreanjos/openlang --path skills/openlang
```

### Other AI Agents

Paste the contents of `skills/openlang/SKILL.md` into your agent's system prompt or context window. The agent will speak OpenLang for the rest of the session.

### Skills

| Skill       | Target          | Install                                                  |
| ----------- | --------------- | -------------------------------------------------------- |
| Generic     | Any LLM         | `skills/openlang/SKILL.md`                               |
| OpenClaw    | OpenClaw agents | `npx clawhub install openlang`                           |
| Claude Code | Claude Code     | `/install-plugin https://github.com/andreanjos/openlang` |
| Codex       | OpenAI Codex    | `install skill from andreanjos/openlang`                 |
| Gemini      | Google Gemini   | `gemini skills install` from repo                        |

## Compression Levels

| Level | Name     | Compression | Use Case                                                              |
| ----- | -------- | ----------- | --------------------------------------------------------------------- |
| `~L1` | Pidgin   | 3-5x        | Novel concepts, nuance, fallback when grammar can't express something |
| `~L2` | Glyph    | 5-10x       | Default working mode                                                  |
| `~L3` | Bytecode | 10-15x      | Repetitive ops, bulk data, known patterns                             |

Speakers shift between levels mid-message as needed. Default is L2 if unspecified.

## Core Syntax

### Sigils

Every statement starts with a sigil declaring intent:

| Sigil | Meaning      | Example                                     |
| ----- | ------------ | ------------------------------------------- |
| `?`   | Query        | `?fnd @fs {p:"src/*.ts"}`                   |
| `!`   | Command      | `!del @fs {p:"tmp/"}`                       |
| `>`   | Result       | `>ok {found:3 paths:[...]}`                 |
| `#`   | State/Data   | `#ctx {lang:ts env:node deps:[react,next]}` |
| `~`   | Meta/Control | `~L2` `~ack` `~err:parse`                   |
| `^`   | Control Flow | `^if {cond} !do {x} ^el !do {y}`            |

### Structural Tokens

| Token   | Meaning                                       |
| ------- | --------------------------------------------- |
| `@`     | Target/scope                                  |
| `->`    | Output format / pipe                          |
| `{}`    | Parameter block                               |
| `<< >>` | Block scope (multi-statement / nested bodies) |
| `[]`    | List/array                                    |
| `()`    | Grouping / precedence                         |
| `\|`    | Separator / alternative                       |
| `..`    | Range                                         |
| `::`    | Type annotation                               |
| `$`     | Variable dereference                          |

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

Use `scope:action` to disambiguate and for scope-specific operations. Prefer this over generic action + scope:

```
!git:mrg {src:"main" dst:"dev"}         -- preferred over !mrg @git
!db:mrg {tbl:"users" on:"id"}           -- preferred over !mrg @db
!pkg:install {n:"express"}               -- preferred over !run @sh {cmd:"npm install"}
```

## Vocabulary

### Actions

| Token | Meaning     | Token | Meaning     |
| ----- | ----------- | ----- | ----------- |
| `fnd` | find/search | `mk`  | make/create |
| `del` | delete      | `mod` | modify/edit |
| `rd`  | read        | `wr`  | write       |
| `run` | execute     | `cpy` | copy        |
| `mv`  | move        | `mrg` | merge       |
| `tst` | test        | `vfy` | verify      |
| `prs` | parse       | `fmt` | format      |
| `snd` | send        | `rcv` | receive     |

### Scopes (@targets)

| Token   | Meaning     | Token  | Meaning        |
| ------- | ----------- | ------ | -------------- |
| `@fs`   | filesystem  | `@sh`  | shell          |
| `@git`  | git repo    | `@net` | network/API    |
| `@db`   | database    | `@mem` | memory/context |
| `@env`  | environment | `@usr` | user           |
| `@proc` | process     | `@pkg` | packages       |

### Modifiers

| Token | Meaning        | Token | Meaning   |
| ----- | -------------- | ----- | --------- |
| `rec` | recursive      | `par` | parallel  |
| `seq` | sequential     | `dry` | dry run   |
| `frc` | force          | `tmp` | temporary |
| `vrb` | verbose        | `sil` | silent    |
| `lmt` | limit          | `dep` | depth     |
| `pri` | priority       | `unq` | unique    |
| `neg` | negate/exclude |       |           |

### Qualifiers

State descriptors that filter queries or describe state. Place **before** the param block, after the scope. Stack left-to-right:

| Token | Meaning   | Token | Meaning      |
| ----- | --------- | ----- | ------------ |
| `rcn` | recent    | `lrg` | large        |
| `sml` | small     | `chg` | changed      |
| `stl` | stale     | `nw`  | new          |
| `old` | old       | `act` | active       |
| `idl` | idle      | `fld` | failed       |
| `hlt` | healthy   | `hot` | hot/frequent |
| `cld` | cold/rare |       |              |

```
?fnd @fs chg rcn {p:"src/**/*.ts"}       -- qualifiers before {}
?fnd @db fld rcn {tbl:"trades" lmt:50}   -- failed + recent
#sys {cpu:act mem:72% disk:hlt net:idl}   -- in state blocks, qualifiers are values
```

### Types (:: annotations)

| Token | Meaning       | Token | Meaning   |
| ----- | ------------- | ----- | --------- |
| `str` | string        | `int` | integer   |
| `bln` | boolean       | `lst` | list      |
| `map` | key-value map | `fn`  | function  |
| `pth` | path          | `rgx` | regex     |
| `err` | error         | `nul` | null/none |

### Response Status

| Token | Meaning | Token | Meaning |
| ----- | ------- | ----- | ------- |
| `ok`  | success | `fl`  | fail    |
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

| Token       | Meaning              | Usage                                            |
| ----------- | -------------------- | ------------------------------------------------ |
| `^frk:name` | Fork named task      | `^frk:t1 !fnd @fs {p:"src/**"}`                  |
| `^jn`       | Join/await tasks     | `^jn [t1,t2] ->$results`                         |
| `^lk:name`  | Acquire mutex        | `^lk:db_write`                                   |
| `^ulk:name` | Release mutex        | `^ulk:db_write`                                  |
| `^ch:name`  | Declare channel      | `^ch:data ::int buf:50`                          |
| `^tx:name`  | Send to channel      | `^tx:data {v:$val}`                              |
| `^rx:name`  | Receive from channel | `^rx:data ->$val`                                |
| `^tmo:N`    | Timeout (seconds)    | `^jn [t1] ^tmo:30 ->$r \| ^el >fl {err:timeout}` |

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

**Strictly positional, period-delimited.** No key:value pairs — position determines meaning. Backtick-quote fields containing literal periods:

```
Format: SIGIL.scope.action.target.modifiers

Q.fs.fnd.`app.config.ts`.rec            -- query: find, recursive
R.ok.3.[`src/a.ts`:5,`src/b.ts`:12]     -- result: 3 matches (:N = line number)
Q.fs.fnd.*.ts.rec.3                      -- no backticks needed without periods
C.sh.run.`npm test`                      -- command: run shell command
```

## Message Envelope

Envelopes are for **routed inter-agent messages** where you need addressing, tracking, or references. For standalone commands and direct responses, use bare OpenLang:

```
-- Bare (standalone / direct response):
!del @fs {p:"tmp/"} rec frc

-- Enveloped (routed between agents):
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
~err {code:E_PARSE lvl:warn msg:"unknown token: xyz"}
~err {code:E_FS_NOT_FOUND lvl:fatal msg:"missing core config"}
~err {code:E_TIMEOUT lvl:warn msg:"30s exceeded"}
~retry {ref:&a3x}                        -- retriable: please retry
```

Code namespaces: `E_PARSE`, `E_FS_*`, `E_SH_*`, `E_NET_*`, `E_DB_*`, `E_AUTH`, `E_TIMEOUT`.
Severity: `info`, `warn`, `fatal`.

Use `~retry` to explicitly signal retriability. `~err` alone means non-retriable.

## Token Extension

Agents can define new tokens inline during a session:

```
~unk {tok:"xyz" req:def}           -- unknown token, request definition
~def {tok:"xyz" means:"..."}       -- define new token
```

### Agent Handshake

```
~hello {id:bot1 ~cap {L:[1,2,3] ext:[fs,git,sh,net]} ver:0.3}
~hello {id:bot2 ~cap {L:[1,2] ext:[fs,db]} ver:0.3}
```

## How It Works in OpenClaw

OpenLang compresses the three main inter-agent channels:

**`sessions_spawn` (task delegation):**

```
-- Instead of: "Search all recently changed TypeScript files excluding tests
-- for TODO comments, read each one, and summarize what you find"

~openlang
?fnd @fs chg rcn {p:"src/**/*.ts" p:!~"*.test.ts" rgx:"TODO"} ->$lst
^ea ->$f {!rd @fs {p:$f} ->$content; !prs @mem {src:$content k:"todos"}}
>ok {summary:true fmt:map}
```

**`sessions_send` (agent-to-agent messaging):**

```
-- Agent A -> Agent B
~openlang
?fnd @db {tbl:trades rcn lmt:100} ->$trades
!prs @mem {src:$trades k:pnl} ->$analysis
>ok {$analysis}

-- Agent B -> Agent A
~openlang
>ok {pnl:+2.3% win_rate:0.68 sharpe:1.42 trades:100
 top:{sym:"AAPL" pnl:+890} worst:{sym:"TSLA" pnl:-340}}
```

**Announce results:**

```
~openlang
>ok {n:12 todos:[
  {f:"src/api.ts" ln:42 msg:"refactor auth flow"},
  {f:"src/db.ts" ln:18 msg:"add connection pooling"}
] truncated:10}
~L1: most TODOs are in api.ts and db.ts, concentrated around auth and connection handling
```

Agents use `~openlang` prefix so receivers know to parse compressed format. Normal language is used for human-facing channels (Telegram, Slack, etc).

## Learning OpenLang

Taught via a bootstrap skill at session start. Learnable because:

- Sigils provide immediate intent classification
- Short tokens compose freely for novel expressions
- L1 fallback means you never get stuck
- Agents can define new tokens inline with `~def`
