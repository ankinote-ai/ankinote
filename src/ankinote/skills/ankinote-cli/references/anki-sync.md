# Anki backend and AnkiWeb sync

AnkiNote saves cards through one of two backends. The CLI uses the one saved
in `settings.json` (chosen in the web app's setup wizard or the bare
`ankinote` menu); the `ANKI_BACKEND` environment variable is the fallback.

- **Built-in Anki** (`collection`): AnkiNote opens the collection file itself
  and syncs with AnkiWeb. No Anki desktop needed. Only one process can hold
  the collection, so the CLI fails with "in use by another process" while
  `ankinote-web` or Anki desktop has it open.
- **AnkiConnect** (`connect`): talks to a running Anki desktop with the
  [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on
  (`ANKI_CONNECT_URL`, default `http://localhost:8765`). Anki desktop syncs.

## AnkiWeb sync (built-in Anki only)

```
ankinote anki status   # local sync state as JSON; doesn't contact AnkiWeb
ankinote anki sync     # sync now
ankinote anki login    # prompts for credentials, or uses ANKIWEB_USERNAME/ANKIWEB_PASSWORD
ankinote anki logout   # stop syncing; keeps the cards
```

Cards added by `add`/`batch` sync on their own when the user is logged in.
Don't run `login` with credentials you weren't given; ask the user to sign in.
