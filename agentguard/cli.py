from __future__ import annotations

import argparse
import json

from . import __version__
from .report import to_html
from .scanner import context_budget_findings, context_stats, detect_adapters, filter_baseline, scan_path, score


SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def should_fail(findings, threshold=None):
    """Return whether findings meet a configured CI failure threshold."""
    if not findings:
        return False
    if threshold is None:
        return True
    minimum = SEVERITY_RANK[threshold]
    return any(SEVERITY_RANK.get(item.severity, 1) >= minimum for item in findings)


def to_sarif(findings):
    rules = {}
    results = []
    level_map = {"critical": "error", "high": "error", "medium": "warning", "low": "note"}

    for item in findings:
        rules.setdefault(
            item.rule_id,
            {
                "id": item.rule_id,
                "shortDescription": {"text": item.message},
                "help": {"text": item.remediation, "markdown": item.remediation},
                "defaultConfiguration": {"level": level_map.get(item.severity, "warning")},
            },
        )
        results.append(
            {
                "ruleId": item.rule_id,
                "level": level_map.get(item.severity, "warning"),
                "message": {"text": item.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": item.path},
                            "region": {"startLine": item.line},
                        }
                    }
                ],
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "AgentGuard",
                        "version": __version__,
                        "informationUri": "https://github.com/atilaamorim/agentguard",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def emit_github_annotations(findings):
    level_map = {"critical": "error", "high": "error", "medium": "warning", "low": "notice"}
    for item in findings:
        level = level_map.get(item.severity, "warning")
        title = item.rule_id.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        message = item.message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        path = str(item.path).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(",", "%2C")
        print(f"::{level} file={path},line={item.line},title={title}::{message}")


def main():
    parser = argparse.ArgumentParser(
        prog="agentguard",
        description="Audit AI-agent and MCP configuration.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a directory or file")
    scan.add_argument("path", nargs="?", default=".")
    scan.add_argument("--json", action="store_true", dest="as_json")
    scan.add_argument(
        "--sarif",
        metavar="PATH",
        help="Write findings in SARIF 2.1.0 format",
    )
    scan.add_argument(
        "--html",
        metavar="PATH",
        help="Write a human-readable HTML report",
    )
    scan.add_argument(
        "--adapters",
        action="store_true",
        help="Show detected AI-agent and MCP ecosystems",
    )
    scan.add_argument(
        "--context",
        action="store_true",
        help="Show estimated token usage for agent instruction files",
    )
    scan.add_argument(
        "--max-context-tokens",
        type=int,
        metavar="N",
        help="Fail when an agent instruction file exceeds N estimated tokens",
    )
    scan.add_argument(
        "--baseline",
        metavar="PATH",
        help="Compare findings against a JSON baseline and report only new findings",
    )
    scan.add_argument(
        "--github-annotations",
        action="store_true",
        help="Emit GitHub Actions annotations for findings",
    )
    scan.add_argument(
        "--fail-on-severity",
        choices=("low", "medium", "high", "critical"),
        help="Exit with status 1 when a finding reaches this severity",
    )
    scan.add_argument(
        "--write-baseline",
        metavar="PATH",
        help="Write the current findings to a JSON baseline file",
    )

    args = parser.parse_args()
    findings = scan_path(args.path)
    findings.extend(context_budget_findings(args.path, args.max_context_tokens))

    if args.write_baseline:
        with open(args.write_baseline, "w", encoding="utf-8") as handle:
            json.dump(
                {"version": __version__, "findings": [f.to_dict() for f in findings]},
                handle,
                indent=2,
            )
            handle.write("\n")

    baseline_path = args.baseline
    baseline = []
    if baseline_path:
        with open(baseline_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        baseline = data.get("findings", []) if isinstance(data, dict) else data
        findings = filter_baseline(findings, baseline)

    security_score = score(findings)

    if args.adapters:
        adapters = detect_adapters(args.path)
        if adapters:
            print("Detected ecosystems: " + ", ".join(adapters))
        else:
            print("Detected ecosystems: none")

    if args.github_annotations:
        emit_github_annotations(findings)

    if args.context:
        stats = context_stats(args.path)
        if stats:
            print("Context usage (estimated):")
            for item in stats:
                print(
                    f"{item['estimated_tokens']:6} tokens  "
                    f"{item['lines']:5} lines  {item['path']}"
                )
        else:
            print("No supported agent instruction files found.")

    if args.sarif:
        with open(args.sarif, "w", encoding="utf-8") as handle:
            json.dump(to_sarif(findings), handle, indent=2)
            handle.write("\n")

    if args.html:
        with open(args.html, "w", encoding="utf-8") as handle:
            handle.write(to_html(findings, security_score, __version__))

    if args.as_json:
        print(
            json.dumps(
                {
                    "version": __version__,
                    "score": security_score,
                    "findings": [f.to_dict() for f in findings],
                },
                indent=2,
            )
        )
        return 1 if should_fail(findings, args.fail_on_severity) else 0

    print(f"🛡️ AgentGuard {__version__}")
    print(f"\nScanning: {args.path}\n")
    print(f"Security score: {security_score}/100")
    print(f"Findings: {len(findings)}\n")
    for item in findings:
        print(
            f"{item.severity.upper():8} {item.rule_id:15} "
            f"{item.message} — {item.path}:{item.line}"
        )
    if not findings:
        print("No findings. Your scanned configuration looks clean.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
