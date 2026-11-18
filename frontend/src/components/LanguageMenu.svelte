<script lang="ts">
  import { tick } from "svelte";
  import { i18n, locales, t, type Locale } from "../lib/i18n.svelte";

  let open = $state(false);
  let root = $state<HTMLElement>();
  let button = $state<HTMLButtonElement>();
  let items = $state<HTMLButtonElement[]>([]);

  async function show() {
    open = true;
    await tick();
    items[locales.findIndex((l) => l.id === i18n.locale)]?.focus();
  }

  function hide(refocus: boolean) {
    open = false;
    if (refocus) button?.focus();
  }

  function choose(id: Locale) {
    i18n.locale = id;
    hide(true);
  }

  function onMenuKey(event: KeyboardEvent) {
    const at = items.indexOf(document.activeElement as HTMLButtonElement);
    const n = locales.length;
    const move: Record<string, number> = {
      ArrowDown: (at + 1) % n,
      ArrowUp: (at - 1 + n) % n,
      Home: 0,
      End: n - 1,
    };
    if (event.key in move) {
      event.preventDefault();
      items[move[event.key]!]?.focus();
    } else if (event.key === "Escape") {
      event.preventDefault();
      hide(true);
    } else if (event.key === "Tab") {
      hide(false);
    }
  }

  function onButtonKey(event: KeyboardEvent) {
    if ((event.key === "ArrowDown" || event.key === "ArrowUp") && !open) {
      event.preventDefault();
      void show();
    }
  }

  function onWindowPointer(event: PointerEvent) {
    if (open && !root?.contains(event.target as Node)) hide(false);
  }
</script>

<svelte:window onpointerdown={onWindowPointer} />

<div class="lang" bind:this={root}>
  <button
    bind:this={button}
    class="chip"
    aria-label={t("bar.lang")}
    title={t("bar.lang")}
    aria-haspopup="menu"
    aria-expanded={open}
    onclick={() => (open ? hide(false) : show())}
    onkeydown={onButtonKey}
  >
    <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
      <g fill="none" stroke="currentColor" stroke-width="1.3">
        <circle cx="8" cy="8" r="6.25" />
        <path d="M1.75 8h12.5M8 1.75c-1.8 1.7-2.7 3.8-2.7 6.25s.9 4.55 2.7 6.25c1.8-1.7 2.7-3.8 2.7-6.25S9.8 3.45 8 1.75Z" />
      </g>
    </svg>
  </button>
  {#if open}
    <!-- svelte-ignore a11y_interactive_supports_focus -->
    <div class="menu" role="menu" aria-label={t("bar.lang")} tabindex="-1" onkeydown={onMenuKey}>
      {#each locales as l, i (l.id)}
        <button
          bind:this={items[i]}
          role="menuitemradio"
          aria-checked={l.id === i18n.locale}
          lang={l.id}
          class:on={l.id === i18n.locale}
          onclick={() => choose(l.id)}
        >
          <span class="check" aria-hidden="true">{l.id === i18n.locale ? "✓" : ""}</span>
          {l.name}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .lang {
    position: relative;
    display: flex;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    min-height: 32px;
    padding: 4px 7px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: none;
    color: var(--muted);
    cursor: pointer;
  }

  .chip:hover,
  .chip[aria-expanded="true"] {
    border-color: var(--accent);
    color: var(--fg);
  }

  .menu {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    z-index: 20;
    display: flex;
    flex-direction: column;
    min-width: 160px;
    padding: 4px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--tile);
  }

  .menu button {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 36px;
    padding: 6px 10px 6px 6px;
    border: none;
    border-radius: 6px;
    background: none;
    color: var(--fg);
    font-family: var(--sans);
    font-size: 14px;
    text-align: left;
    white-space: nowrap;
    cursor: pointer;
  }

  .menu button:hover {
    background: var(--sel);
  }

  .menu button.on {
    background: var(--sel);
  }

  .menu button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }

  .check {
    width: 14px;
    color: var(--accent);
    font-family: var(--mono);
    text-align: center;
  }
</style>
