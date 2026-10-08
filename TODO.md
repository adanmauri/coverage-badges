# TODO

## Features

- More badge styles: a `style` input with the shields.io styles (`flat`, `flat-square`,
  `for-the-badge`, `plastic`, `social`), keeping today's look as the default.

## Verification

- Publish a changed badge with `actions/checkout` v6 or v7, which keep the credentials in a separate
  file. Publishing was tested with v5; this repository's CI uses v7 but has not had to push a
  changed badge since.
- Check badge rendering in the GitHub iOS app (only Android was tested).
- Run the action on a macOS runner (only Ubuntu 22.04 and 24.04 were tested).
