from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

SECRET_RE = re.compile(r"(api[_-]?key|secret|token|password|private[_-]?key)\\s*[:=]\\s*['\"]?[A-Za-z0-9_./+=-]{12,}", re.I)
INJECTION_RE = re.compile(r"(ignore (all|any|previous|prior) instructions|reveal (the )?system prompt|disregard (all|any|previous) instructions)", re.I)
DANGEROUS_RE = re.compile(r"(shell|terminal|exec|execute|command|subprocess|bash|powershell|cmd\\.exe)", re.I)

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

def finding(rule,severity,message,path,line,evidence):
    return Finding(rule,severity,message,str(path),line,evidence[:180])

def scan_text(text,path):
    findings=[]
    for n,line in enumerate(text.splitlines(),1):
        if SECRET_RE.search(line):
            findings.append(finding("AG-SEC-001","high","Potential secret detected",path,n,line.strip()))
        if INJECTION_RE.search(line):
            findings.append(finding("AG-PROMPT-001","medium","Prompt-injection pattern detected",path,n,line.strip()))
        if DANGEROUS_RE.search(line) and any(x in line.lower() for x in ("tool","permission","allow","command","exec","shell","terminal")):
            findings.append(finding("AG-EXEC-001","high","Potential command execution capability",path,n,line.strip()))
    return findings

def scan_config(text,path):
    findings=scan_text(text,path)
    data=None
    try:
        data=yaml.safe_load(text) if yaml else json.loads(text)
    except Exception:
        pass
    if isinstance(data,dict):
        raw=json.dumps(data)
        if re.search(r"(filesystem|file.?access|workspace|allowed.?paths?)",raw,re.I) and re.search(r'["\']/',raw):
            findings.append(finding("AG-FS-001","high","Broad filesystem access may expose sensitive files",path,1,raw))
    return findings

def scan_path(root):
    root=Path(root)
    if root.is_file():
        text=root.read_text(errors="replace")
        return scan_config(text,root) if root.suffix.lower() in {".json",".yaml",".yml"} else scan_text(text,root)
    findings=[]
    ignored={".git",".venv","venv","node_modules","__pycache__",".pytest_cache"}
    for p in root.rglob("*"):
        if not p.is_file() or any(part in ignored for part in p.parts) or p.stat().st_size>2_000_000:
            continue
        try: text=p.read_text(errors="replace")
        except Exception: continue
        if p.suffix.lower() in {".json",".yaml",".yml"} or p.name in {"CLAUDE.md","AGENTS.md","GEMINI.md","CODEX.md"}:
            findings.extend(scan_config(text,p))
        elif p.suffix.lower() in {".md",".txt",".toml",".ini",".cfg",".env"}:
            findings.extend(scan_text(text,p))
    return findings

def score(findings):
    weights={"critical":35,"high":20,"medium":10,"low":4}
    return max(0,100-min(100,sum(weights.get(f.severity,4) for f in findings)))
