from __future__ import annotations
import argparse
import json
from . import __version__
from .scanner import scan_path, score

def main():
    parser=argparse.ArgumentParser(prog="agentguard",description="Audit AI-agent and MCP configuration.")
    sub=parser.add_subparsers(dest="command",required=True)
    scan=sub.add_parser("scan",help="Scan a directory or file")
    scan.add_argument("path",nargs="?",default=".")
    scan.add_argument("--json",action="store_true",dest="as_json")
    args=parser.parse_args()
    findings=scan_path(args.path)
    security_score=score(findings)
    if args.as_json:
        print(json.dumps({"version":__version__,"score":security_score,"findings":[f.to_dict() for f in findings]},indent=2))
        return 1 if findings else 0
    print(f"🛡️ AgentGuard {__version__}\n")
    print(f"Scanning: {args.path}\n")
    print(f"Security score: {security_score}/100")
    print(f"Findings: {len(findings)}\n")
    for f in findings:
        print(f"{f.severity.upper():8} {f.rule_id:15} {f.message} — {f.path}:{f.line}")
    return 1 if findings else 0

if __name__=="__main__":
    raise SystemExit(main())
