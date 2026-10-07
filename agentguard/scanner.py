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


def scan_path(root):
    root = Path(root)
    if root.is_file():
        text = root.read_text(errors="replace")
        return scan_config(text, root) if root.suffix.lower() in {".json", ".yaml", ".yml"} else scan_text(text, root)

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
        elif path.suffix.lower() in TEXT_EXTENSIONS:
            findings.extend(scan_text(text, path))
    return findings


def score(findings):
    weights = {"critical": 35, "high": 20, "medium": 10, "low": 4}
    return max(0, 100 - min(100, sum(weights.get(f.severity, 4) for f in findings)))
