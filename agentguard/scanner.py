from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from .rules import AGENT_INSTRUCTION_FILES, RULES, TEXT_EXTENSIONS


ADAPTERS = {
    "claude": {"CLAUDE.md", ".claude"},
    "codex": {"CODEX.md", ".codex"},
    "cursor": {"CURSOR.md", ".cursorrules", ".cursor"},
    "gemini": {"GEMINI.md", ".gemini"},
    "opencode": {"opencode.json", "opencode.jsonc", ".opencode"},
    "mcp": {"mcp.json", "mcp.yaml", "mcp.yml", ".mcp.json"},
}


def detect_adapters(root):
    """Return detected agent ecosystems from conventional project markers."""
    root = Path(root)
    if root.is_file():
        names = {root.name}
    else:
        names = {p.name for p in root.rglob("*") if p.is_file() or p.is_dir()}
    return sorted(name for name, markers in ADAPTERS.items() if names & markers)


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str
    line: int
    evidence: str

    def to_dict(self):
        return asdict(self)


def finding(rule_id, path, line, evidence):
    rule = RULES[rule_id]
    return Finding(rule_id, rule["severity"], rule["message"], str(path), line, evidence[:180])


def scan_text(text, path):
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for rule_id, rule in RULES.items():
            if not rule["pattern"].search(line):
                continue
            if rule_id == "AG-EXEC-001" and not any(
                word in line.lower()
                for word in ("tool", "permission", "allow", "command", "exec", "shell", "terminal")
            ):
                continue
            findings.append(finding(rule_id, path, number, line.strip()))
    return findings


def scan_config(text, path):
    findings = scan_text(text, path)
    data = None
    try:
        data = yaml.safe_load(text) if yaml else json.loads(text)
    except Exception:
        pass
    if isinstance(data, dict):
        raw = json.dumps(data)
        if re.search(r"(filesystem|file.?access|workspace|allowed.?paths?)", raw, re.I):
            if re.search(r'["\']/', raw) or re.search(r'["\']~["\']', raw):
                findings.append(
                    finding("AG-FS-001", path, 1, raw)
                )
    return findings


def scan_context_bloat(text, path, max_lines=500):
    if Path(path).name not in AGENT_INSTRUCTION_FILES:
        return []
    line_count = len(text.splitlines())
    if line_count <= max_lines:
        return []
    return [finding("AG-CONTEXT-001", path, max_lines + 1,
                     f"Instruction file contains {line_count} lines; recommended maximum is {max_lines}.")]


def scan_path(root):
    root = Path(root)
    if root.is_file():
        text = root.read_text(errors="replace")
        findings = scan_config(text, root) if root.suffix.lower() in {".json", ".yaml", ".yml"} else scan_text(text, root)
        findings.extend(scan_context_bloat(text, root))
        return findings

    findings = []
    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts) or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        if path.suffix.lower() in {".json", ".yaml", ".yml"} or path.name in AGENT_INSTRUCTION_FILES:
            findings.extend(scan_config(text, path))
            findings.extend(scan_context_bloat(text, path))
        elif path.suffix.lower() in TEXT_EXTENSIONS:
            findings.extend(scan_text(text, path))
    return findings


def score(findings):
    weights = {"critical": 35, "high": 20, "medium": 10, "low": 4}
    return max(0, 100 - min(100, sum(weights.get(f.severity, 4) for f in findings)))


def estimate_tokens(text):
    """Estimate token count conservatively using roughly four characters per token."""
    return max(1, (len(text) + 3) // 4)


def context_stats(root):
    """Return estimated context usage for supported agent instruction files."""
    root = Path(root)
    paths = [root] if root.is_file() else list(root.rglob("*"))
    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
    stats = []
    for path in paths:
        if (
            not path.is_file()
            or path.name not in AGENT_INSTRUCTION_FILES
            or any(part in ignored for part in path.parts)
            or path.stat().st_size > 2_000_000
        ):
            continue
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        stats.append(
            {
                "path": str(path),
                "lines": len(text.splitlines()),
                "characters": len(text),
                "estimated_tokens": estimate_tokens(text),
            }
        )
    return sorted(stats, key=lambda item: item["estimated_tokens"], reverse=True)


def finding_key(item):
    """Return a stable fingerprint for baseline comparisons."""
    return (item.rule_id, item.path, item.evidence)


def filter_baseline(findings, baseline):
    """Return only findings that are not already present in a baseline."""
    known = {
        (item.get("rule_id"), item.get("path"), item.get("evidence"))
        for item in baseline
        if isinstance(item, dict)
    }
    return [item for item in findings if finding_key(item) not in known]
