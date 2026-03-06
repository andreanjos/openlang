"""Hybrid scorer: structural checks + LLM-as-judge."""

import re
import json


# ── Layer 1: Structural checks (deterministic) ──

VALID_SIGILS = {"?", "!", ">", "#", "~", "^"}


def _strip_strings(text: str) -> str:
    """Remove quoted string contents to avoid false positives in structural checks."""
    return re.sub(r'"[^"]*"', '""', text)


def check_balanced(text: str) -> list[str]:
    """Check balanced delimiters (ignoring content inside quoted strings)."""
    errors = []
    clean = _strip_strings(text)
    pairs = {"{": "}", "[": "]"}
    stack = []
    # Check << >> separately
    opens = clean.count("<<")
    closes = clean.count(">>")
    if opens != closes:
        errors.append(f"unbalanced << >>: {opens} opens, {closes} closes")
    for ch in clean:
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


def _strip_fences(text: str) -> str:
    """Remove markdown code fences, backtick wrapping, and surrounding prose."""
    text = text.strip()

    # Extract content from code fences if present (handles multiple blocks)
    fenced = re.findall(r"```(?:\w*)\n(.*?)```", text, re.DOTALL)
    if fenced:
        return "\n\n".join(block.strip() for block in fenced)

    # Remove single backtick wrapping: `content` -> content
    if text.startswith("`") and text.endswith("`") and text.count("`") == 2:
        return text[1:-1]

    # If there's a mix of prose and OpenLang, try to extract just the OpenLang.
    # OpenLang lines start with sigils, structural tokens, or L3 uppercase.
    lines = text.split("\n")
    ol_lines = []
    in_openlang = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_openlang:
                ol_lines.append("")
            continue
        first = stripped[0]
        is_ol = (
            first in VALID_SIGILS
            or first in ("{", "}", "[", "]", "(", ")", "|", "&", "$", "<")
            or (first == "-" and len(stripped) > 1 and stripped[1] == "-")
            or (first == "-" and len(stripped) > 1 and stripped[1] == ">")
            or (len(stripped) > 1 and first.isupper() and stripped[1] == ".")
        )
        if is_ol:
            in_openlang = True
            ol_lines.append(line)
        elif in_openlang:
            # Could be continuation inside a block — keep it
            ol_lines.append(line)
        # Skip leading prose lines

    result = "\n".join(ol_lines).strip()
    return result if result else text


# L3 sigil mapping (single uppercase letter)
L3_SIGILS = {"Q", "C", "R", "S", "D", "M"}


def check_sigil_start(text: str) -> list[str]:
    """Check that statements start with valid sigils."""
    errors = []
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    depth = 0  # nesting depth for { } and << >>
    for line in lines:
        # Track block depth (before checking so opens on this line count)
        clean = _strip_strings(line)
        depth += clean.count("{") + clean.count("<<")
        depth -= clean.count("}") + clean.count(">>")
        # Skip lines that are continuations, comments, or block closers
        if not line or line.startswith("--") or line.startswith(">>"):
            continue
        # Skip lines starting with known structural tokens
        if line[0] in ("{", "}", "[", "]", "(", ")", "|", "&", "$"):
            continue
        # Skip continuation lines inside blocks (key:value pairs, etc)
        if depth > 0:
            continue
        # Skip L1 text content
        if "~L1:" in text and not any(line.startswith(s) for s in VALID_SIGILS):
            continue
        # L3 bytecode lines start with uppercase letter + period
        if len(line) > 1 and line[0] in L3_SIGILS and line[1] == ".":
            continue
        # Backtick-quoted L3 lines
        if line.startswith("`"):
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

You MUST respond with ONLY this JSON object and nothing else:
{"score": N, "reason": "brief explanation"}"""


def _parse_judge_response(result: str) -> dict | None:
    """Try multiple strategies to extract score/reason from judge output."""
    # Strategy 1: parse a full JSON object containing "score"
    json_match = re.search(r"\{[^{}]*\"score\"[^{}]*\}", result)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return {
                "score": int(parsed.get("score", 0)),
                "reason": str(parsed.get("reason", "no reason")),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 2: flexible key:value extraction (handles single quotes, no quotes, etc)
    match = re.search(r"[\"']?score[\"']?\s*[:=]\s*(\d)", result)
    if match:
        score = int(match.group(1))
        reason_match = re.search(
            r"[\"']?reason[\"']?\s*[:=]\s*[\"'](.+?)[\"']", result
        )
        reason = reason_match.group(1) if reason_match else result[:150]
        return {"score": min(score, 2), "reason": reason}

    # Strategy 3: just a bare number on the first line
    first_line = result.strip().split("\n")[0]
    match = re.search(r"\b([012])\b", first_line)
    if match:
        return {"score": int(match.group(1)), "reason": result[:150]}

    return None


MAX_JUDGE_RETRIES = 2


async def llm_judge(adapter, test: dict, response: str) -> dict:
    """Use an LLM to judge semantic correctness, with retry on parse failure."""
    prompt = json.dumps(
        {
            "test_type": test["type"],
            "input": test["prompt"],
            "expected": test["expected"],
            "response": response,
        },
        indent=2,
    )

    last_error = ""
    for attempt in range(MAX_JUDGE_RETRIES + 1):
        try:
            result = await adapter.complete(JUDGE_PROMPT, prompt)
            parsed = _parse_judge_response(result)
            if parsed is not None:
                return parsed
            last_error = f"judge returned invalid format (attempt {attempt + 1}): {result[:100]}"
        except Exception as e:
            last_error = f"judge error: {str(e)}"

    return {"score": 0, "reason": last_error}


async def score_test(judge_adapter, test: dict, response: str) -> dict:
    """Full hybrid scoring pipeline."""
    result = {
        "test_id": test["id"],
        "type": test["type"],
        "response": response,
    }

    # Strip markdown fences from generation/roundtrip responses
    cleaned = response
    if test["type"] in ("generation", "roundtrip"):
        cleaned = _strip_fences(response)
        result["cleaned"] = cleaned

        struct = structural_score(cleaned)
        result["structural"] = struct
        if not struct["valid"]:
            result["score"] = 0
            result["reason"] = f"structural errors: {struct['errors']}"
            return result

    # LLM judge for semantic correctness
    judgment = await llm_judge(
        judge_adapter, test, cleaned if test["type"] != "comprehension" else response
    )
    result["score"] = judgment.get("score", 0)
    result["reason"] = judgment.get("reason", "no reason given")
    return result
