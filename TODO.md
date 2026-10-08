# TODO

## Release

- Tag `v1` (and a moving `v1` major tag) so `adanmauri/coverage-badges@v1` resolves.
- Publish the action to the GitHub Marketplace.

## Verification

- Check badge rendering in the GitHub iOS app (only Android was tested).

## Hardening

- Fix the zizmor findings in `.github/workflows/` (actions not pinned to a commit SHA,
  `persist-credentials` left on where the job does not push), then extend the zizmor hook in
  `.pre-commit-config.yaml` from `action.yml` to the workflows.
