<script lang="ts">
  import { onMount } from "svelte";
  import { api, type Health } from "../lib/api";
  import { i18n, t } from "../lib/i18n.svelte";
  import { REPO_URL } from "../lib/settings";
  import { update } from "../lib/update.svelte";

  let health = $state<Health | null>(null);
  let failed = $state(false);

  onMount(async () => {
    try {
      health = await api.health();
    } catch {
      failed = true;
    }
  });

  /** Versions only, so it's safe to paste into a public issue. */
  const diagnostics = $derived(
    health
      ? [
          `AnkiNote ${health.version}`,
          `Python ${health.python}`,
          health.platform,
          navigator.userAgent,
          `Interface language: ${i18n.locale}`,
        ].join("\n")
      : "",
  );

  // Seeing the new version here answers the top bar's marker.
  $effect(() => {
    if (update.status?.available) update.markSeen();
  });

  const LABELS = { docker: "Docker", uv_tool: "uv tool", uvx: "uvx", pip: "pip", unknown: "" } as const;

  type Copied = "version" | "diagnostics" | `command-${number}` | "failed" | null;
  let copied = $state<Copied>(null);
  let timer: ReturnType<typeof setTimeout> | undefined;

  function textFor(what: Exclude<Copied, "failed" | null>): string {
    if (what === "version") return health?.version ?? "";
    if (what === "diagnostics") return diagnostics;
    return update.status?.commands[Number(what.slice("command-".length))]?.command ?? "";
  }

  async function copy(what: Exclude<Copied, "failed" | null>) {
    clearTimeout(timer);
    try {
      await navigator.clipboard.writeText(textFor(what));
      copied = what;
    } catch {
      copied = "failed";
    }
    timer = setTimeout(() => (copied = null), 2500);
  }

  const links = [
    { label: "about.project", href: REPO_URL },
    { label: "about.issues", href: `${REPO_URL}/issues` },
    { label: "about.releases", href: `${REPO_URL}/releases` },
    { label: "about.license", href: `${REPO_URL}/blob/main/LICENSE`, text: "MIT" },
  ] as const;
</script>

<div class="about">
  {#if failed}
    <p class="error" role="alert">{t("about.loadError")}</p>
  {:else}
    <section class="version" aria-labelledby="v-label">
      <h3 id="v-label">{t("about.version")}</h3>
      <p class="number">
        <span class="mono">{health?.version ?? "…"}</span>
        <button type="button" class="ghost" onclick={() => copy("version")} disabled={!health}>
          {copied === "version" ? t("about.copied") : t("about.copy")}
        </button>
      </p>
      {#if update.status?.available && update.status.latest}
        {@const u = update.status}
        <div class="update" role="status">
          <h3>{t(u.major ? "about.update.titleMajor" : "about.update.title", { version: u.latest ?? "" })}</h3>
          {#if u.major && u.notes_url}
            <!-- A major release may break things: its notes come before the command. -->
            <p class="major">
              {t("about.update.major")}
              <a href={u.notes_url} target="_blank" rel="noopener noreferrer">{t("about.update.readFirst")}</a>
            </p>
          {/if}
          <p class="note">{t(`about.update.how.${u.install}`)}</p>
          {#each u.commands as c, i (c.install)}
            <div class="command">
              {#if u.install === "unknown"}<span class="label">{LABELS[c.install]}</span>{/if}
              <code class="mono">{c.command}</code>
              <button type="button" class="ghost" onclick={() => copy(`command-${i}`)}>
                {copied === `command-${i}` ? t("about.copied") : t("about.copy")}
              </button>
            </div>
          {/each}
          {#if u.notes_url && !u.major}
            <a href={u.notes_url} target="_blank" rel="noopener noreferrer">{t("about.update.notes")}</a>
          {/if}
        </div>
      {:else if update.status?.enabled && update.status.latest}
        <p class="note latest">{t("about.update.latest")}</p>
      {/if}
    </section>

    <dl class="links">
      {#each links as l (l.label)}
        <div class="row">
          <dt>{t(l.label)}</dt>
          <dd>
            <a href={l.href} target="_blank" rel="noopener noreferrer">
              {"text" in l ? l.text : l.href.replace("https://", "")}
            </a>
          </dd>
        </div>
      {/each}
    </dl>

    <section class="diag" aria-labelledby="d-label">
      <h3 id="d-label">{t("about.diagnostics")}</h3>
      <p class="note">{t("about.diagnosticsNote")}</p>
      <pre class="mono">{diagnostics}</pre>
      <button type="button" onclick={() => copy("diagnostics")} disabled={!health}>
        {copied === "diagnostics" ? t("about.copied") : t("about.copyDiagnostics")}
      </button>
      <span class="status" role="status">
        {#if copied === "failed"}{t("about.copyFailed")}{/if}
      </span>
    </section>
  {/if}
</div>

<style>
  .about {
    max-width: 560px;
  }

  h3 {
    margin: 0 0 6px;
    font-size: 14px;
    font-weight: 600;
    color: var(--muted);
  }

  /* The one big thing on the page: the number people are asked for. */
  .number {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin: 0 0 24px;
  }

  .number .mono {
    font-size: 36px;
    line-height: 1.1;
  }

  .mono {
    font-family: var(--mono);
  }

  .ghost {
    border: 0;
    background: none;
    color: var(--accent);
    padding: 6px 4px;
    cursor: pointer;
  }

  .ghost:disabled {
    color: var(--muted);
    cursor: default;
  }

  /* A new release: boxed in the accent colour under the version number. */
  .update {
    margin: 0 0 24px;
    padding: 12px 14px;
    border: 1px solid var(--accent);
    border-radius: 6px;
  }

  .update h3 {
    color: var(--fg);
  }

  .update a {
    color: var(--accent);
  }

  .major {
    margin: 0 0 12px;
  }

  .major a {
    display: block;
    margin-top: 2px;
    font-weight: 600;
  }

  .command {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 4px 12px;
    margin: 0 0 10px;
  }

  .command .label {
    min-width: 5em;
    color: var(--muted);
  }

  .command code {
    padding: 4px 8px;
    border-radius: 4px;
    background: var(--outer);
    font-size: 13px;
    overflow-wrap: anywhere;
  }

  .latest {
    margin-top: -16px;
    margin-bottom: 24px;
  }

  .links {
    margin: 0 0 24px;
    border-top: 1px solid var(--border);
  }

  .row {
    display: grid;
    grid-template-columns: 9em minmax(0, 1fr);
    gap: 12px;
    align-items: baseline;
    min-height: 40px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }

  dt {
    color: var(--muted);
  }

  dd {
    margin: 0;
    min-width: 0;
    overflow-wrap: anywhere;
  }

  dd a {
    color: var(--accent);
  }

  .note {
    margin: 0 0 10px;
    font-size: 14px;
    color: var(--muted);
  }

  pre {
    margin: 0 0 12px;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--outer);
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    user-select: all;
  }

  .status {
    margin-left: 12px;
    font-size: 14px;
    color: var(--err);
  }

  .error {
    color: var(--err);
  }

  @container app (max-width: 600px) {
    .row {
      grid-template-columns: minmax(0, 1fr);
      gap: 0;
    }

    .number .mono {
      font-size: 30px;
    }
  }
</style>
