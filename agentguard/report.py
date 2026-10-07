from __future__ import annotations

from html import escape


def to_html(findings, security_score, version):
    rows = []
    for item in findings:
        rows.append(
            "<tr><td>{}</td><td><strong>{}</strong></td><td>{}</td><td>{}:{}</td></tr>".format(
                escape(item.severity.upper()),
                escape(item.rule_id),
                escape(item.message),
                escape(item.path),
                item.line,
            )
        )
    body = ''.join(rows) or '<tr><td colspan="4">No findings. Your scanned configuration looks clean.</td></tr>'
    status = 'PASS' if not findings else 'FINDINGS DETECTED'
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentGuard report</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1000px;margin:40px auto;padding:0 20px;color:#17202a}}header{{display:flex;justify-content:space-between;align-items:end;border-bottom:1px solid #ddd;padding-bottom:20px}}.score{{font-size:42px;font-weight:700}}table{{width:100%;border-collapse:collapse;margin-top:24px}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #eee}}th{{background:#f5f5f5}}.status{{font-weight:700}}.muted{{color:#667}}</style>
</head>
<body>
<header><div><h1>🛡️ AgentGuard</h1><p class="muted">Security and context audit</p></div><div><div class="score">{}/100</div><div class="status">{}</div></div></header>
<p>Version: {}</p>
<h2>Findings ({})</h2>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Message</th><th>Location</th></tr></thead><tbody>{}</tbody></table>
</body></html>'''.format(version, security_score, status, version, len(findings), body)
