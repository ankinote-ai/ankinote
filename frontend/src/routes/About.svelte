<script lang="ts">
  import { onMount } from "svelte";
  import { api, type Health } from "../lib/api";
  import { i18n, t } from "../lib/i18n.svelte";
  import { REPO_URL } from "../lib/settings";

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

  type Copied = "version" | "diagnostics" | "failed" | null;
  let copied = $state<Copied>(null);
  let timer: ReturnType<typeof setTimeout> | undefined;

  async function copy(what: "version" | "diagnostics") {
    clearTimeout(timer);
    try {
      await navigator.clipboard.writeText(what === "version" ? (health?.version ?? "") : diagnostics);
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
