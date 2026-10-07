from __future__ import annotations

import re

RULES = {
    "AG-SEC-001": {
        "severity": "high",
        "message": "Potential secret detected",
        "pattern": re.compile(
            r"""(api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*['"]?[A-Za-z0-9_./+=-]{12,}""",
            re.I,
        ),
    },
    "AG-PROMPT-001": {
        "severity": "medium",
        "message": "Prompt-injection pattern detected",
        "pattern": re.compile(
            r"(ignore (all|any|previous|prior) instructions|reveal (the )?system prompt|disregard (all|any|previous) instructions|do not follow (the )?rules|override (the )?system)",
            re.I,
        ),
    },
    "AG-EXEC-001": {
        "severity": "high",
        "message": "Potential command execution capability",
        "pattern": re.compile(
            r"(shell|terminal|exec|execute|command|subprocess|bash|powershell|cmd\.exe)",
            re.I,
        ),
    },
    "AG-FS-001": {
        "severity": "high",
        "message": "Broad filesystem access may expose sensitive files",
        "pattern": re.compile(r"$^"),
    },
    "AG-CONTEXT-001": {
        "severity": "low",
        "message": "Agent instruction file is unusually large and may increase context cost",
        "pattern": re.compile(r"$^"),
    },
}

AGENT_INSTRUCTION_FILES = {
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "CODEX.md",
    "CURSOR.md",
    ".cursorrules",
    ".windsurfrules",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".json",
    ".yaml",
    ".yml",
}
