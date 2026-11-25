<script lang="ts">
  import { api } from "../lib/api";
  import { t, type MessageKey } from "../lib/i18n.svelte";
  import { link, router } from "../lib/router.svelte";
  import { palettes, theme, type Mode } from "../lib/theme.svelte";
  import { update } from "../lib/update.svelte";
  import LanguageMenu from "./LanguageMenu.svelte";

  const workspaces: { n: number; path: string; key: MessageKey }[] = [
    { n: 1, path: "/", key: "nav.generate" },
    { n: 2, path: "/notetypes", key: "nav.notetypes" },
    { n: 3, path: "/settings", key: "nav.settings" },
  ];
  const modes: Mode[] = ["system", "light", "dark"];

  let online = $state<boolean | null>(null);
  api.health().then(
    () => (online = true),
    () => (online = false),
  );

  const paletteName = $derived(palettes.find((p) => p.id === theme.palette)?.name ?? "");

  /** A workspace's own page or one under it (/settings/anki). */
  function here(path: string): boolean {
    return router.path === path || (path !== "/" && router.path.startsWith(`${path}/`));
  }

  function onKey(event: KeyboardEvent) {
    const target = event.target as HTMLElement;
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if (target.closest("input, textarea, select, [contenteditable]")) return;
    const ws = workspaces.find((w) => String(w.n) === event.key);
    if (ws && !here(ws.path)) router.go(ws.path);
  }
</script>

<svelte:window onkeydown={onKey} />

<header class="bar">
  <span class="logo">
    <!-- The mark (scripts/brand.py): the card's front and back as two tiles. -->
    <svg viewBox="0 0 32 32" width="20" height="20" aria-hidden="true">
      <rect x="3.25" y="5.25" width="10.5" height="21.5" rx="2.75" fill="none" stroke="var(--fg)" stroke-width="2.5" />
      <rect x="6" y="10" width="5" height="2.5" rx="1.25" fill="var(--fg)" />
      <rect x="18" y="4" width="12" height="24" rx="3.5" fill="var(--accent)" />
    </svg>
    <span class="brand">AnkiNote</span>
  </span>
  <nav class="ws">
    {#each workspaces as ws (ws.path)}
      <a
        href={ws.path}
        onclick={link}
        class:on={here(ws.path)}
        aria-current={here(ws.path) ? "page" : undefined}
      >
        <span class="n">{ws.n}</span><span class="label">{t(ws.key)}</span>
      </a>
    {/each}
  </nav>
  <div class="right">
    {#if update.marked && update.status?.latest}
      <a
        class="chip update"
        href="/settings/about"
        onclick={link}
        title={t("bar.update", { version: update.status.latest })}
        aria-label={t("bar.update", { version: update.status.latest })}
      >
        <span aria-hidden="true">↑</span> {update.status.latest}
      </a>
    {/if}
    {#if online !== null}
      <span class="status" class:off={!online}>
        <span aria-hidden="true">●</span>
        <span class="status-text">{online ? t("bar.connected") : t("bar.offline")}</span>
      </span>
    {/if}
    <button class="chip" onclick={() => theme.cyclePalette()} title={t("bar.palette", { name: paletteName })}>
      {paletteName}
    </button>
    <button
      class="chip"
      onclick={() => (theme.mode = modes[(modes.indexOf(theme.mode) + 1) % modes.length]!)}
    >
      {t(`bar.mode.${theme.mode}`)}
    </button>
    <LanguageMenu />
  </div>
</header>

<style>
  .bar {
    display: flex;
    align-items: center;
    gap: 8px 16px;
    padding: 8px 14px;
    min-width: 0;
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
  }

  .logo {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .logo svg {
    flex: none;
  }

  .brand {
    font-weight: 500;
    color: var(--fg);
  }

  .ws {
    display: flex;
    gap: 6px;
  }

  .ws a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 32px;
    padding: 5px 10px;
    border-radius: 6px;
    color: var(--muted);
    text-decoration: none;
    white-space: nowrap;
  }

  .ws a:hover {
    color: var(--fg);
  }

  .ws a.on {
    background: var(--accent);
    color: var(--on-accent);
  }

  .right {
    display: flex;
    align-items: center;
    gap: 6px 12px;
    margin-left: auto;
    min-width: 0;
  }

  .status {
    color: var(--ok);
    white-space: nowrap;
  }

  .status.off {
    color: var(--err);
  }

  .status-text {
    color: var(--muted);
  }

  .chip {
    min-height: 32px;
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: none;
    font-family: var(--mono);
    font-size: 13px;
    white-space: nowrap;
    cursor: pointer;
  }

  .chip:hover {
    border-color: var(--accent);
  }

  /* A new release: the one chip that is a link, in the accent colour. */
  .update {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    border-color: var(--accent);
    color: var(--accent);
    text-decoration: none;
  }

  @container app (max-width: 1000px) {
    .brand,
    .status-text {
      display: none;
    }
  }

  @container app (max-width: 600px) {
    .bar {
      flex-wrap: wrap;
      padding: 8px 10px;
      gap: 8px;
    }

    .ws .n {
      display: none;
    }

    .right {
      gap: 6px;
    }
  }
</style>
