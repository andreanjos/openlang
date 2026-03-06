#!/usr/bin/env python3
"""OpenLang Benchmark Runner.

Usage:
    python bench/run.py                        # Run all models
    python bench/run.py --models claude codex  # Specific models
    python bench/run.py --concurrency 5        # Limit concurrency
    python bench/run.py --judge gemini         # Use Gemini as judge
"""

import asyncio
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

from models import get_adapters, CodexAdapter, GeminiAdapter
from judge import score_test


BENCH_DIR = Path(__file__).parent
SKILL_PATH = BENCH_DIR.parent / "skills" / "openlang" / "SKILL.md"
TESTS_PATH = BENCH_DIR / "tests.json"
RESULTS_DIR = BENCH_DIR / "results"


def load_skill() -> str:
    return SKILL_PATH.read_text()


def load_tests() -> list[dict]:
    return json.loads(TESTS_PATH.read_text())


def make_prompt(test: dict) -> str:
    """Build the user prompt for a test case."""
    if test["type"] == "comprehension":
        return (
            "Translate the following OpenLang message into plain English. "
            "Be precise about every detail (action, scope, modifiers, values).\n\n"
            f"{test['prompt']}"
        )
    elif test["type"] == "generation":
        return test["prompt"]
    else:  # roundtrip
        return test["prompt"]


async def run_test(
    adapter, judge_adapter, skill: str, test: dict, sem: asyncio.Semaphore
) -> dict:
    """Run a single test against a model and score it."""
    async with sem:
        prompt = make_prompt(test)
        try:
            response = await asyncio.wait_for(
                adapter.complete(skill, prompt), timeout=90
            )
        except asyncio.TimeoutError:
            return {
                "test_id": test["id"],
                "type": test["type"],
                "score": 0,
                "reason": "timeout (90s)",
                "response": "",
            }
        except Exception as e:
            return {
                "test_id": test["id"],
                "type": test["type"],
                "score": 0,
                "reason": f"model error: {str(e)}",
                "response": "",
            }

        result = await score_test(judge_adapter, test, response)
        return result


async def run_model(
    adapter, judge_adapter, skill: str, tests: list[dict], concurrency: int
) -> dict:
    """Run all tests against a single model."""
    sem = asyncio.Semaphore(concurrency)
    print(f"\n  Running {len(tests)} tests against {adapter.name}...")

    tasks = [run_test(adapter, judge_adapter, skill, test, sem) for test in tests]
    results = await asyncio.gather(*tasks)

    # Tally scores
    by_type = {"comprehension": [], "generation": [], "roundtrip": []}
    for r in results:
        by_type[r["type"]].append(r)

    summary = {}
    total_score = 0
    total_max = 0
    for typ, items in by_type.items():
        scored = sum(1 for r in items if r["score"] == 2)
        partial = sum(1 for r in items if r["score"] == 1)
        failed = sum(1 for r in items if r["score"] == 0)
        total_score += sum(r["score"] for r in items)
        total_max += len(items) * 2
        summary[typ] = {
            "total": len(items),
            "correct": scored,
            "partial": partial,
            "failed": failed,
            "pct": round(scored / len(items) * 100, 1) if items else 0,
        }

    return {
        "model": adapter.name,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "overall_pct": round(total_score / total_max * 100, 1) if total_max else 0,
        "results": results,
    }


def print_summary(reports: list[dict]):
    """Print comparison table."""
    print("\n" + "=" * 75)
    print("BENCHMARK RESULTS")
    print("=" * 75)
    print(
        f"{'Model':<25} {'Comprehend':>12} {'Generate':>12} {'Roundtrip':>12} {'Overall':>10}"
    )
    print("-" * 75)
    for r in reports:
        s = r["summary"]
        c = s.get("comprehension", {})
        g = s.get("generation", {})
        rt = s.get("roundtrip", {})
        print(
            f"{r['model']:<25} "
            f"{c.get('correct', 0)}/{c.get('total', 0)} ({c.get('pct', 0):>4.0f}%) "
            f"{g.get('correct', 0)}/{g.get('total', 0)} ({g.get('pct', 0):>4.0f}%) "
            f"{rt.get('correct', 0)}/{rt.get('total', 0)} ({rt.get('pct', 0):>4.0f}%) "
            f"{r['overall_pct']:>6.1f}%"
        )
    print("=" * 75)


def write_results(reports: list[dict]):
    """Write per-model JSON and summary markdown."""
    RESULTS_DIR.mkdir(exist_ok=True)

    for r in reports:
        name = r["model"].replace("/", "-").replace(" ", "-")
        path = RESULTS_DIR / f"{name}.json"
        path.write_text(json.dumps(r, indent=2))
        print(f"  Written: {path}")

    # Summary markdown
    lines = [
        "# OpenLang Benchmark Results",
        "",
        f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Model | Comprehension | Generation | Round-trip | Overall |",
        "|-------|--------------|------------|------------|---------|",
    ]
    for r in reports:
        s = r["summary"]
        c = s.get("comprehension", {})
        g = s.get("generation", {})
        rt = s.get("roundtrip", {})
        lines.append(
            f"| {r['model']} "
            f"| {c.get('correct', 0)}/{c.get('total', 0)} ({c.get('pct', 0):.0f}%) "
            f"| {g.get('correct', 0)}/{g.get('total', 0)} ({g.get('pct', 0):.0f}%) "
            f"| {rt.get('correct', 0)}/{rt.get('total', 0)} ({rt.get('pct', 0):.0f}%) "
            f"| {r['overall_pct']:.1f}% |"
        )
    lines.append("")

    # Failures detail
    for r in reports:
        failures = [t for t in r["results"] if t["score"] == 0]
        if failures:
            lines.append(f"### {r['model']} — Failures ({len(failures)})")
            lines.append("")
            for f in failures:
                lines.append(
                    f"- **{f['test_id']}** ({f['type']}): {f.get('reason', 'unknown')}"
                )
            lines.append("")

    summary_path = RESULTS_DIR / "summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"  Written: {summary_path}")


async def main():
    parser = argparse.ArgumentParser(description="OpenLang Benchmark")
    parser.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Models to test (claude, codex, gemini). Default: all",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent requests per model (default: 10)",
    )
    parser.add_argument(
        "--judge",
        default="gemini",
        help="Judge model (codex, gemini). Default: gemini",
    )
    args = parser.parse_args()

    print("OpenLang Benchmark v0.2")
    print("=" * 40)

    skill = load_skill()
    tests = load_tests()
    print(f"Loaded {len(tests)} tests, skill preamble: {len(skill)} chars")

    # Set up judge
    judge_map = {
        "codex": lambda: CodexAdapter(),
        "gemini": lambda: GeminiAdapter(),
    }
    judge_adapter = judge_map[args.judge]()
    print(f"Judge: {judge_adapter.name}")

    adapters = get_adapters(args.models)
    print(f"Testing: {', '.join(a.name for a in adapters)}")

    reports = []
    start = time.time()
    for adapter in adapters:
        report = await run_model(adapter, judge_adapter, skill, tests, args.concurrency)
        reports.append(report)

    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.1f}s")

    print_summary(reports)
    write_results(reports)


if __name__ == "__main__":
    asyncio.run(main())
