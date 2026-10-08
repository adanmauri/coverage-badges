# TODO

## Release

- Tag `v1` (and a moving `v1` major tag) so `adanmauri/coverage-badges@v1` resolves.
- Publish the action to the GitHub Marketplace.

## Verification

- Check badge rendering in the GitHub iOS app (only Android was tested).
- Run the action on a macOS runner (only Ubuntu 22.04 and 24.04 were tested).

## Hardening

- The Trivy job in `security.yaml` fails before it starts: the `aquasecurity/trivy-action@0.28.0`
  tag no longer exists (latest is `v0.36.0`). Pin a current release to a commit SHA.
- After the first MegaLinter run on `main`, list the linters at zero findings under
  `ENABLE_ERRORS_LINTERS` in `.mega-linter.yml`, so new linters report instead of failing.
- `MEGALINTER_CACHE` in `code-quality.yaml` is not a MegaLinter setting (not in the v9.1.0
  schema); confirm and remove it.

- Fix the zizmor findings in `.github/workflows/` (actions not pinned to a commit SHA,
  `persist-credentials` left on where the job does not push), then extend the zizmor hook in
  `.pre-commit-config.yaml` from `action.yml` to the workflows.
