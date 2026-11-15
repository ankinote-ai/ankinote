<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    title,
    area,
    fill = false,
    children,
  }: {
    title: string;
    area?: string;
    /** Lay children out as a column that fills the pane's height. */
    fill?: boolean;
    children: Snippet;
  } = $props();
</script>

<!-- The focused pane (focus anywhere inside) gets the accent border. -->
<section class="pane" class:fill style:grid-area={area} aria-label={title}>
  <h2 class="pane-title">{title}</h2>
  {@render children()}
</section>

<style>
  .pane {
    position: relative;
    min-width: 0;
    min-height: 0;
    padding: 14px 16px 16px;
    background: var(--tile);
    border: 2px solid var(--border);
    border-radius: 10px;
  }

  .pane.fill {
    display: flex;
    flex-direction: column;
  }

  .pane:focus-within {
    border-color: var(--accent);
  }

  /* The title lives inside the tile, so the border stays one unbroken line. */
  .pane-title {
    flex: none;
    margin: 0 0 12px;
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 500;
    line-height: 18px;
    color: var(--muted);
  }

  .pane:focus-within > .pane-title {
    color: var(--accent);
  }
</style>
