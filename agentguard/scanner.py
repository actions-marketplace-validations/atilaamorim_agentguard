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


def _walk_mcp_servers(value, prefix=""):
    """Yield (name, config) pairs from common MCP server container shapes."""
    if isinstance(value, dict):
        for key in ("mcpServers", "mcp_servers", "servers"):
            servers = value.get(key)
            if isinstance(servers, dict):
                for name, config in servers.items():
                    if isinstance(config, dict):
                        yield f"{prefix}{name}", config
                for name, config in servers.items():
                    if isinstance(config, dict):
                        yield from _walk_mcp_servers(config, f"{prefix}{name}.")
        for key, child in value.items():
            if key not in {"mcpServers", "mcp_servers", "servers"}:
                yield from _walk_mcp_servers(child, f"{prefix}{key}.")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_mcp_servers(child, f"{prefix}{index}.")



def _flatten_config(value):
    """Flatten nested config values into lowercase text for capability analysis."""
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_config(child)}" for key, child in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_flatten_config(child) for child in value).lower()
    return str(value).lower()


def _has_any(text, terms):
    return any(term in text for term in terms)

def scan_mcp_config(data, path):
    """Inspect parsed MCP configuration for high-signal security hazards."""
    if not isinstance(data, (dict, list)):
        return []

    findings = []
    seen = set()
    for name, config in _walk_mcp_servers(data):
        identity = (name, id(config))
        if identity in seen:
            continue
        seen.add(identity)

        if config.get("trust") is True:
            findings.append(
                finding(
                    "AG-MCP-001",
                    path,
                    1,
                    f"MCP server '{name}' sets trust=true, which can bypass tool-call confirmation.",
                )
            )

        for key in ("url", "httpUrl", "server_url", "serverUrl"):
            endpoint = config.get(key)
            if isinstance(endpoint, str) and endpoint.lower().startswith("http://"):
                findings.append(
                    finding(
                        "AG-MCP-002",
                        path,
                        1,
                        f"MCP server '{name}' uses unencrypted HTTP endpoint: {endpoint}",
                    )
                )
                break

        text = _flatten_config(config)
        has_untrusted = _has_any(text, ("untrusted", "external_input", "external input", "user_input", "user input", "remote_content"))
        has_private = _has_any(text, ("private_data", "private data", "sensitive_data", "sensitive data", "credentials", "secrets", "filesystem", "workspace"))
        has_outbound = _has_any(text, ("network", "http", "https", "webhook", "upload", "send", "outbound", "external_url"))
        if has_untrusted and has_private and has_outbound:
            findings.append(
                finding(
                    "AG-POLICY-001",
                    path,
                    1,
                    f"MCP server '{name}' combines untrusted input, private-data access, and outbound actions.",
                )
            )
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
        findings.extend(scan_mcp_config(data, path))
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


def context_budget_findings(root, max_tokens):
    """Return findings for agent instruction files above a configured token budget."""
    if max_tokens is None:
        return []
    findings = []
    for item in context_stats(root):
        if item["estimated_tokens"] > max_tokens:
            findings.append(
                finding(
                    "AG-CONTEXT-002",
                    item["path"],
                    1,
                    f"Estimated context is {item['estimated_tokens']} tokens; configured budget is {max_tokens}.",
                )
            )
    return findings


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
