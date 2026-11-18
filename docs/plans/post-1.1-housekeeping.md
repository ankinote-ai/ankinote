# After 1.1: Release Notes for the Image Move

**Status: open.** In 1.1.0 the repository moved to `ankinote-ai/ankinote`, and
the GHCR image moved with it. The registry and PyPI cleanup is done; one item
is left for the next release. Delete this file once it ships.

## On the next release

- [ ] Say in the release notes that GHCR images moved from
  `ghcr.io/ignity21/ankinote-ai` to `ghcr.io/ankinote-ai/ankinote`, and that
  deployments must update `ANKINOTE_IMAGE` in `.env`. The Docker Hub image
  `ignity21/ankinote-ai` is unchanged. `deploy/README.md` → Upgrading already
  explains the move; link to it.
