<script lang="ts">
  import { t } from "../lib/i18n.svelte";

  let {
    onback,
    onskip,
    onnext,
    last = false,
    nextDisabled = false,
    busy = false,
    hint = "",
    nextLabel,
  }: {
    onback?: () => void;
    onskip?: () => void;
    onnext: () => void;
    last?: boolean;
    nextDisabled?: boolean;
    busy?: boolean;
    hint?: string;
    /** Instead of Next / Start using AnkiNote. */
    nextLabel?: string;
  } = $props();
</script>

<nav class="nav">
  {#if hint}<p class="hint">{hint}</p>{/if}
  <button class="secondary" disabled={!onback} onclick={() => onback?.()}>{t("wizard.back")}</button>
  {#if onskip}
    <button class="secondary" onclick={onskip}>{t("wizard.skip")}</button>
  {/if}
  <button class="primary" disabled={nextDisabled || busy} onclick={onnext}>
    {busy ? t("wizard.saving") : (nextLabel ?? (last ? t("wizard.finish") : t("wizard.next")))}
  </button>
</nav>

<style>
  /* Stays in view at the bottom of the wizard pane, however long the step. */
  .nav {
    position: sticky;
    bottom: 0;
    z-index: 1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 24px;
    padding: 12px 0 2px;
    border-top: 1px solid var(--border);
    background: var(--tile);
  }

  .hint {
    flex: 1 1 200px;
    margin: 0;
    color: var(--muted);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
