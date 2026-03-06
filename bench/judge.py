"""Hybrid scorer: structural checks + LLM-as-judge."""

import re
import json


# ── Layer 1: Structural checks (deterministic) ──

VALID_SIGILS = {"?", "!", ">", "#", "~", "^"}
VALID_TOKENS = {
    "fnd", "mk", "del", "mod", "rd", "wr", "run", "cpy", "mv", "mrg",
    "tst", "vfy", "prs", "fmt", "snd", "rcv",
    "fs", "sh", "git", "net", "db", "mem", "env", "usr", "proc", "pkg",
    "rec", "par", "seq", "dry", "frc", "tmp", "vrb", "sil", "lmt", "dep",
    "pri", "unq", "neg",
    "rcn", "lrg", "sml", "chg", "stl", "nw", "old", "act", "idl", "fld",
    "hlt", "hot", "cld",
    "str", "int", "bln", "lst", "map", "fn", "pth", "rgx", "err", "nul",
    "ok", "fl", "prt", "pnd", "skp", "blk",
    "if", "el", "lp", "ea", "wt", "rt", "br", "ct",
    "frk", "jn", "lk", "ulk", "ch", "tx", "rx", "tmo",
    "L1", "L2", "L3", "ack", "hello", "unk", "def", "retry", "sess",
    "feat", "rej", "openlang",
}


def check_balanced(text: str) -> list[str]:
    """Check balanced delimiters."""
    errors = []
    pairs = {"{": "}", "[": "]"}
    stack = []
    # Check << >> separately
    opens = text.count("<<")
    closes = text.count(">>")
    if opens != closes:
        errors.append(f"unbalanced << >>: {opens} opens, {closes} closes")
    for ch in text:
        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in pairs.values():
            if not stack or stack[-1] != ch:
                errors.append(f"unbalanced '{ch}'")
                break
            stack.pop()
    if stack:
        errors.append(f"unclosed delimiters: {''.join(stack)}")
    return errors


def check_sigil_start(text: str) -> list[str]:
    """Check that statements start with valid sigils."""
    errors = []
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines:
        # Skip lines that are continuations, comments, or inside blocks
        if not line or line.startswith("--") or line.startswith(">>"):
            continue
        # Skip lines starting with known structural tokens
        if line[0] in ("{", "}", "[", "]", "(", ")", "|", "&", "$"):
            continue
        # Skip L1 text content
        if "~L1:" in text and not any(line.startswith(s) for s in VALID_SIGILS):
            continue
        first_char = line[0]
        if first_char not in VALID_SIGILS and first_char not in {"<", "-", '"', "'"}:
            errors.append(f"line doesn't start with sigil: '{line[:40]}'")
    return errors


def structural_score(response: str) -> dict:
    """Run structural checks on an OpenLang response.

    Returns {"valid": bool, "errors": [...], "checks": {...}}
    """
    checks = {
        "balanced": check_balanced(response),
        "sigil_start": check_sigil_start(response),
    }
    all_errors = []
    for errs in checks.values():
        all_errors.extend(errs)
    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "checks": {k: len(v) == 0 for k, v in checks.items()},
    }


# ── Layer 2: LLM-as-judge ──

JUDGE_PROMPT = """You are an expert judge evaluating responses in OpenLang, a compact AI-to-AI communication protocol.

You will be given:
- test_type: "comprehension", "generation", or "roundtrip"
- input: the prompt given to the model
- expected: what a correct response looks like (description or example)
- response: the model's actual response

Score the response:
- 2 = correct (meaning fully preserved, syntax valid if OpenLang output)
- 1 = partially correct (gist is right but details wrong, or minor syntax issues)
- 0 = wrong (misunderstood, invalid, or nonsensical)

Respond with ONLY a JSON object: {"score": N, "reason": "brief explanation"}"""


async def llm_judge(adapter, test: dict, response: str) -> dict:
    """Use an LLM to judge semantic correctness."""
    prompt = json.dumps({
        "test_type": test["type"],
        "input": test["prompt"],
        "expected": test["expected"],
        "response": response,
    }, indent=2)

    try:
        result = await adapter.complete(JUDGE_PROMPT, prompt)
        # Extract JSON from response
        match = re.search(r'\{[^}]+\}', result)
        if match:
            return json.loads(match.group())
        return {"score": 0, "reason": "judge returned invalid format"}
    except Exception as e:
        return {"score": 0, "reason": f"judge error: {str(e)}"}


async def score_test(judge_adapter, test: dict, response: str) -> dict:
    """Full hybrid scoring pipeline."""
    result = {
        "test_id": test["id"],
        "type": test["type"],
        "response": response,
    }

    # For generation and roundtrip, run structural checks first
    if test["type"] in ("generation", "roundtrip"):
        struct = structural_score(response)
        result["structural"] = struct
        if not struct["valid"]:
            result["score"] = 0
            result["reason"] = f"structural errors: {struct['errors']}"
            return result

    # LLM judge for semantic correctness
    judgment = await llm_judge(judge_adapter, test, response)
    result["score"] = judgment.get("score", 0)
    result["reason"] = judgment.get("reason", "no reason given")
    return result
