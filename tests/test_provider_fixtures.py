from pathlib import Path

from agentguard.scanner import scan_config, scan_path


FIXTURES = Path(__file__).parent / "fixtures" / "providers"


def ids(findings):
    return {item.rule_id for item in findings}


def test_gemini_fixture_triggers_provider_rule():
    path = FIXTURES / "gemini" / "settings.json"
    findings = scan_path(path)
    assert "AG-GEMINI-001" in ids(findings)


def test_gemini_safe_fixture_has_no_provider_finding():
    path = FIXTURES / "gemini-safe" / "settings.json"
    findings = scan_path(path)
    assert "AG-GEMINI-001" not in ids(findings)


def test_codex_fixture_triggers_full_access_rule():
    path = FIXTURES / "codex" / "config.toml"
    findings = scan_path(path)
    assert "AG-CODEX-001" in ids(findings)


def test_codex_safe_fixture_has_no_full_access_finding():
    path = FIXTURES / "codex-safe" / "config.toml"
    findings = scan_path(path)
    assert "AG-CODEX-001" not in ids(findings)


def test_benign_claude_fixture_is_clean():
    findings = scan_path(FIXTURES / "claude" / "CLAUDE.md")
    assert findings == []


def test_benign_cursor_fixture_is_clean():
    findings = scan_path(FIXTURES / "cursor" / "CURSOR.md")
    assert findings == []


def test_mcp_https_inside_provider_fixture_is_not_flagged():
    path = FIXTURES / "gemini" / "settings.json"
    findings = scan_config(path.read_text(encoding="utf-8"), str(path))
    assert "AG-MCP-002" not in ids(findings)