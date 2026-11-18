# Deploying AnkiNote with Docker

Published images (multi-arch `amd64` + `arm64`), tags `latest`, `<major>.<minor>`,
`<version>`:

- `ghcr.io/ankinote-ai/ankinote`
- `ignity21/ankinote-ai` (Docker Hub, same image)

Two ready-made stacks:

| Directory | Use it when |
| --- | --- |
| [`headless/`](headless/) (recommended) | You want a self-contained stack: no Anki desktop app, no AnkiConnect. AnkiNote keeps its own Anki collection and syncs it straight with AnkiWeb. |
| [`standard/`](standard/) | You already run AnkiConnect — the Anki desktop app on the host, or one elsewhere. |

Each directory is standalone:

```bash
cd deploy/headless        # or deploy/standard
cp .env.example .env      # optional: AnkiWeb login (headless), port, image tag
docker compose up -d      # http://localhost:8080
```

Open the address and the setup wizard walks you through the rest: an AI key
(one Google AI Studio key covers text, pictures and audio), Anki, languages
and a palette. **API keys are entered in the app, not in `.env`**; they
persist in the `ankinote-config` volume.

## Before you open it to other devices

AnkiNote has **no login of its own**. Anyone who can reach the port can make
cards with your API keys and write to your Anki collection. That's why both
stacks publish on `127.0.0.1:8080` by default.

To use it from your phone or another computer, pick one:

- **A private network** such as Tailscale or WireGuard: set
  `ANKINOTE_PUBLISH` to the machine's address on that network
  (e.g. `100.64.0.5:8080`).
- **A reverse proxy with a login**, keeping AnkiNote on `127.0.0.1`. With
  Caddy, which also gets the HTTPS certificate:

  ```
  ankinote.example.com {
      basic_auth {
          you <hash from `caddy hash-password`>
      }
      reverse_proxy 127.0.0.1:8080
  }
  ```

Avoid `ANKINOTE_PUBLISH=8080` (all interfaces) on a machine reachable from
the internet.

AnkiNote answers only to `localhost` and IP addresses, so that a web page can't
reach it through a DNS name it controls. If you open it by name (the proxy's
`ankinote.example.com`, a Tailscale MagicDNS name, `mybox.local`), add that
name to `ANKINOTE_ALLOWED_HOSTS`; otherwise every request gets a
"does not answer to the host name" error.

## `headless/`

One `ankinote` service. It runs with `ANKI_BACKEND=collection`, opens an Anki
collection at `/data/collection.anki2` in-process, and synchronizes it directly
with AnkiWeb — at startup, after every card save, and every five minutes. The
collection, its media, the credential-free sync state, and the backups taken
before a full sync all live in the `anki-data` volume.

Set `ANKIWEB_USERNAME` / `ANKIWEB_PASSWORD` in `.env` to sign in from the
deployment environment; the password is passed through the environment and never
written to disk. They are optional — leave them blank and sign in to AnkiWeb in
the app instead. Either way, a brand-new collection cannot save cards until its
first AnkiWeb sync completes; if AnkiWeb already has data you will be asked once
whether to upload or download.

To use an existing collection directory instead of the named volume, see the
commented bind mount in `headless/compose.yaml`. Open a given collection from
only one process at a time — do not point Anki desktop at the same directory
while the stack is running.

## `standard/`

The container reaches your AnkiConnect via `ANKI_CONNECT_URL` (default
`http://host.docker.internal:8765`, i.e. the host). In the AnkiConnect add-on
config (Tools → Add-ons → AnkiConnect → Config) set `"webBindAddress": "0.0.0.0"`
and add the container origin to `"webCorsOriginList"` (or use `"*"`), then restart
Anki.

## Settings in `.env`

| Variable | Default | What it does |
| --- | --- | --- |
| `ANKINOTE_PUBLISH` | `127.0.0.1:8080` | Address and port on the host. Read the section above before changing the address. |
| `ANKINOTE_ALLOWED_HOSTS` | unset | Comma-separated host names AnkiNote answers to besides `localhost` and IP addresses, e.g. `ankinote.example.com`. |
| `ANKINOTE_IMAGE` | `ghcr.io/ankinote-ai/ankinote:latest` | Image and tag. Pin a minor version (`…:1.1`) to get fixes but not new features. |
| `ANKIWEB_USERNAME` / `ANKIWEB_PASSWORD` | unset | `headless/` only. Signs in to AnkiWeb; overrides a login made in the app; the password is never written to disk. |
| `ANKI_CONNECT_URL` | `http://host.docker.internal:8765` | `standard/` only. Where AnkiConnect listens. |

## Upgrading

```bash
docker compose pull && docker compose up -d
```

Your settings and collection are in the volumes and survive the new
container. With a pinned `ANKINOTE_IMAGE`, change the tag first. From 1.1 the
images are published as `ghcr.io/ankinote-ai/ankinote`; if your `.env` still
names `ghcr.io/ignity21/ankinote-ai`, switch to the new name — the old one is
no longer updated.

## Customizing beyond `.env`

For structural changes — an extra volume, another service, a different network —
drop a `compose.override.yaml` next to the stack's `compose.yaml`. Compose loads
and merges it automatically on `docker compose up`; it is gitignored.

```yaml
# deploy/headless/compose.override.yaml
services:
  ankinote:
    volumes:
      - ./media:/media
```

Note list merges *append* (e.g. a `ports:` entry in the override is added, not
replaced) — for the published port use `ANKINOTE_PUBLISH` instead.

## Building locally

The image installs a released version straight from PyPI:

```bash
docker build --build-arg ANKINOTE_VERSION=1.1.0 -t ankinote ../..
```

(run from either stack directory; the build context is the repo root). Each
`compose.yaml` has a commented `build:` block for `docker compose build`.

## Moving from AnkiConnect to `headless/`

Moving from an AnkiConnect deployment (`standard/`, or an old headless stack
that ran `glechic/anki-connect-server`) to the in-process backend:

1. **Sync the source collection to AnkiWeb** so nothing is only local. In Anki
   desktop press `Y`; a bundled AnkiConnect server syncs on its own.
2. **Stop the old stack** (`docker compose down`). Leave its volumes in place
   until the new stack is verified.
3. **Start `headless/`** with `ANKIWEB_USERNAME` / `ANKIWEB_PASSWORD` set, or
   sign in to AnkiWeb in the app. The empty `anki-data` volume pulls the whole
   collection from AnkiWeb on first sync; when asked for a data source, choose
   **download**.
4. **Check** that the first full sync completed, then open Note types and
   confirm your decks and note types are there.
5. Only then remove the old stack's volumes.

Rehearse against a copy first: `docker run --rm -v OLD_VOLUME:/from -v $PWD:/to
alpine cp /from/collection.anki2 /to/` gives you a throwaway collection file to
bind-mount into a scratch `headless/` stack (`- ./collection.anki2:/data/collection.anki2`).
The migration never deletes cards; a full download replaces the local
collection with AnkiWeb's copy, and `headless/` takes a backup into
`anki-data/collection.anki2.backups/` before it does.
