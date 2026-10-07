# Publishing AgentGuard

## Current status

AgentGuard has a package-build workflow in `.github/workflows/package.yml`, but the project should not be published to PyPI under the current distribution name until the naming issue is resolved.

The `agentguard` distribution name is already used by other projects. See GitHub issue #4 for the migration decision.

## Before the first release

1. Choose and verify a unique distribution name on PyPI.
2. Update `pyproject.toml` and the console-script name if needed.
3. Update installation commands and documentation.
4. Create a version tag such as `v0.1.0` only after the release metadata is final.

## Trusted Publishing

PyPI supports GitHub Actions Trusted Publishing through GitHub's OIDC identity. The publisher workflow needs `id-token: write`; no long-lived PyPI API token needs to be stored in GitHub Secrets.

A typical release job uses the official PyPA action:

```yaml
permissions:
  id-token: write

steps:
  - name: Publish package distributions to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
```

Configure the matching Trusted Publisher on PyPI before pushing the release tag.

## Dry-run/build validation

Before publishing, verify the local distribution:

```bash
python -m pip install build
python -m build
python -m pip install dist/*.whl
agentguard --version
```

The repository's package workflow performs the build and installed-CLI smoke test automatically.
