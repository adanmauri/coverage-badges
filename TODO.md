# TODO

## Release

- Tag `v1` (and a moving `v1` major tag) so `adanmauri/coverage-badges@v1` resolves.
- Publish the action to the GitHub Marketplace.

## Verification

- Check badge rendering in the GitHub iOS app (only Android was tested).
- Run the action on a macOS runner (only Ubuntu 22.04 and 24.04 were tested).

## Hardening

- Run the MegaLinter image by digest: the action pinned by commit still pulls
  `ghcr.io/oxsecurity/megalinter-python:v10.1.0` by tag (docs/adr/0009).
