# Publishing AgentGuard

## Current status

AgentGuard is published on PyPI as `agentconfigguard`; the CLI command remains `agentguard`.

The current public release is `0.2.1`. The historical GitHub repository remains `atilaamorim/agentguard`.

## Release process

1. Update the project version consistently in `pyproject.toml`, `agentguard/__init__.py`, and `CITATION.cff`.
2. Update `CHANGELOG.md` and release documentation.
3. Run the full test, package, and security-audit workflows.
4. Confirm that the target version matches the tag you plan to create.
5. Create and publish the GitHub release with a tag such as `v0.2.2`.
6. The release workflow builds and publishes the distributions to PyPI through Trusted Publishing.
7. Verify the new package version from PyPI with a clean installation.

## Trusted Publishing

PyPI supports GitHub Actions Trusted Publishing through GitHub's OIDC identity. The publisher workflow uses `id-token: write` and the `pypi` GitHub environment; no long-lived PyPI API token is stored in GitHub Secrets. The official PyPA publishing action is used in `.github/workflows/release.yml`.

## Reproducible release check

Before creating a release tag:

```bash
python -m pip install --upgrade build
python -m build
python -m pip install dist/*.whl
agentguard --version
agentguard demo
```

The package workflow also builds the distributions and runs an installed-CLI smoke test.

## Post-release check

After publication:

```bash
python -m pip install --upgrade --force-reinstall agentconfigguard
agentguard --version
agentguard demo
```

The published version should match the GitHub release tag.
