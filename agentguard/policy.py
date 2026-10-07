from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class IgnoreRule:
    rule: str | None = None
    paths: list[str] = field(default_factory=list)


@dataclass
class Policy:
    fail_on_severity: str | None = None
    max_context_tokens: int | None = None
    ignore: list[IgnoreRule] = field(default_factory=list)


def discover_policy(root) -> Path | None:
    """Find a policy file next to the scanned project root."""
    root = Path(root)
    base = root if root.is_dir() else root.parent
    for name in (".agentguard.yml", ".agentguard.yaml"):
        candidate = base / name
        if candidate.is_file():
            return candidate
    return None


def _validate_severity(value: Any) -> str | None:
    if value is None:
        return None
    if value not in {"low", "medium", "high", "critical"}:
        raise ValueError("fail_on_severity must be low, medium, high, or critical")
    return value


def load_policy(path: str | Path | None) -> Policy:
    """Load and validate a small YAML policy file."""
    if path is None:
        return Policy()
    if yaml is None:
        raise RuntimeError("PyYAML is required to load AgentGuard policy files")

    policy_path = Path(path)
    with policy_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("AgentGuard policy must be a YAML mapping")

    version = data.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported AgentGuard policy version: {version}")

    max_context = data.get("max_context_tokens")
    if max_context is not None:
        if not isinstance(max_context, int) or max_context <= 0:
            raise ValueError("max_context_tokens must be a positive integer")

    raw_ignore = data.get("ignore", [])
    if raw_ignore is None:
        raw_ignore = []
    if not isinstance(raw_ignore, list):
        raise ValueError("ignore must be a list")

    ignore: list[IgnoreRule] = []
    for entry in raw_ignore:
        if isinstance(entry, str):
            ignore.append(IgnoreRule(rule=entry))
            continue
        if not isinstance(entry, dict):
            raise ValueError("each ignore entry must be a rule string or mapping")
        rule = entry.get("rule")
        paths = entry.get("paths", [])
        if rule is not None and not isinstance(rule, str):
            raise ValueError("ignore.rule must be a string")
        if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
            raise ValueError("ignore.paths must be a list of strings")
        ignore.append(IgnoreRule(rule=rule, paths=paths))

    return Policy(
        fail_on_severity=_validate_severity(data.get("fail_on_severity")),
        max_context_tokens=max_context,
        ignore=ignore,
    )


def filter_policy_findings(findings, policy: Policy):
    """Remove findings explicitly ignored by policy rule and optional path glob."""
    result = []
    for item in findings:
        ignored = False
        path = Path(item.path).as_posix()
        for entry in policy.ignore:
            if entry.rule is not None and item.rule_id != entry.rule:
                continue
            if entry.paths and not any(fnmatch(path, pattern) for pattern in entry.paths):
                continue
            ignored = True
            break
        if not ignored:
            result.append(item)
    return result
