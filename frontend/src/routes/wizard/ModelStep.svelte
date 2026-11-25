<script lang="ts">
  import { ROUTES } from "../../lib/api";
  import ConnectionResults from "../../components/ConnectionResults.svelte";
  import RouteEditor from "../../components/RouteEditor.svelte";
  import SaveBar from "../../components/SaveBar.svelte";
  import StepNav from "../../components/StepNav.svelte";
  import { t, type MessageKey } from "../../lib/i18n.svelte";
  import { ModelSetup, OFF } from "../../lib/modelSetup.svelte";
  import type { Provider } from "../../lib/api";

  /** `settings`: Settings → Models, where the footer saves instead of moving on. */
  let { onnext = () => {}, settings = false }: { onnext?: () => void; settings?: boolean } = $props();

  const setup = new ModelSetup();
  let showKey = $state(false);
  let advanced = $state(false);

  setup.load().then(() => {
    // A saved setup that isn't the one-key default opens "Advanced" so it shows.
    advanced = setup.customized;
  });

  const main = $derived(setup.mainProvider);
  const savedHint = $derived(setup.savedKeyHint(setup.main));
  const mainRoutes = $derived(ROUTES.filter((route) => setup.sameAsMain(route)));
  // Gemini's key steps (AI Studio, billing for pictures) are its own; others get the generic ones.
  const isGemini = $derived(main?.id === "gemini");

  /** What a provider can make with its one key, for its tile. */
  function abilities(p: Provider): string {
    const can = ROUTES.filter((route) => p.models[route]);
    if (can.length === ROUTES.length) return t("model.can.all");
    if (can.length === 1 && can[0] === "text") return t("model.can.textOnly");
    return can.map((route) => t(`model.route.${route}` as MessageKey)).join(", ");
  }

  function pick(id: string) {
    setup.select(id);
    showKey = false;
    refreshOptions();
  }

  /** A route not on the main key: off (and why), or the provider it uses instead. */
  function elsewhere(route: (typeof ROUTES)[number]): { text: string; model: string } {
    const r = setup.routes[route];
    if (r.provider === OFF) {
      const unsupported = !main?.models[route];
      return { text: unsupported ? t("model.plan.unsupported", { name: main?.label ?? "" }) : t("model.off"), model: "" };
    }
    return { text: setup.label(r.provider), model: r.model.replace(/^[a-z_]+\//, "") };
  }

  function refreshOptions() {
    if (advanced) for (const route of ROUTES) void setup.loadOptions(route);
  }

  function toggleAdvanced(event: Event) {
    advanced = (event.currentTarget as HTMLDetailsElement).open;
    refreshOptions();
  }

  async function next() {
    if (await setup.save()) onnext();
  }

  let justSaved = $state(false);

  async function save() {
    justSaved = await setup.save();
  }

  const hint = $derived.by(() => {
    if (setup.canContinue) return "";
    if (setup.current && setup.results?.text.status !== "ok") {
      return t(settings ? "model.textFailedSave" : "model.textFailed");
    }
    return t(settings ? "model.testToSave" : "model.testFirst");
  });

  const errorText = $derived.by(() => {
    const error = setup.draftError;
    if (error) {
      return t(`model.err.${error.code}` as MessageKey, {
        route: t(`model.route.${error.route}` as MessageKey),
      });
    }
    return setup.failed ? t("model.err.server") : "";
  });
</script>

<p class="intro">{t("model.intro")}</p>

{#if setup.loadError}
  <p class="error" role="alert">{t("model.err.load")}</p>
{:else if main}
  <fieldset class="mains">
    <legend class="label">{t("model.main")}</legend>
    <div class="grid">
      {#each setup.mainChoices as p (p.id)}
        <label class="opt">
          <input
            type="radio"
            name="main-provider"
            value={p.id}
            checked={setup.usesMain && setup.main === p.id}
            onchange={() => pick(p.id)}
          />
          <span class="name">
            {p.label}
            {#if p.recommended}<span class="tag">{t("model.recommendedTag")}</span>{/if}
          </span>
          <span class="sub">{abilities(p)}</span>
        </label>
      {/each}
    </div>
    {#if advanced}<p class="note">{t("model.resetNote")}</p>{/if}
  </fieldset>

  {#if setup.usesMain}
    <section class="howto" aria-labelledby="howto-title">
      <h2 id="howto-title" class="label">{t("model.howTo")}</h2>
      <ol>
        <li>
          {isGemini ? t("model.howTo.key") : t("model.howTo.keyOther", { name: main.label })}
          {#if main.key_url}
            <a href={main.key_url} target="_blank" rel="noreferrer">
              {isGemini ? t("model.howTo.open") : t("model.howTo.openOther", { name: main.label })} ↗
            </a>
          {/if}
        </li>
        {#if isGemini && mainRoutes.includes("image")}<li>{t("model.howTo.billing")}</li>{/if}
      </ol>
      {#if isGemini}
        <p class="note">{t("model.howTo.noApis")}</p>
        {#if mainRoutes.includes("speech")}<p class="note">{t("model.howTo.freeLimits")}</p>{/if}
      {/if}
    </section>

    <div class="field key">
      <label class="label" for="api-key">{t("model.routeKey", { name: setup.label(main.id) })}</label>
      <div class="key-row">
        <input
          id="api-key"
          class="input mono"
          type={showKey ? "text" : "password"}
          bind:value={setup.apiKey}
          autocomplete="off"
          spellcheck="false"
          autocapitalize="off"
          placeholder={savedHint ? t("model.keySaved", { hint: savedHint }) : ""}
          onchange={refreshOptions}
        />
        <button class="secondary" type="button" onclick={() => (showKey = !showKey)} aria-pressed={showKey}>
          {showKey ? t("model.hide") : t("model.show")}
        </button>
      </div>
    </div>

    <div class="plan">
      <span class="label">{t("model.plan")}</span>
      <ul>
        {#each ROUTES as route (route)}
          <li>
            <span>{t(`model.route.${route}` as MessageKey)}</span>
            {#if setup.sameAsMain(route)}
              <span class="model">{setup.routes[route].model.replace(/^[a-z]+\//, "")}</span>
            {:else}
              {@const other = elsewhere(route)}
              <span class="other">
                {other.text}
                {#if other.model}<span class="model">{other.model}</span>{/if}
              </span>
            {/if}
          </li>
        {/each}
      </ul>
    </div>
  {:else}
    <p class="note">{t("model.mainUnused")}</p>
  {/if}

  <details class="advanced" open={advanced} ontoggle={toggleAdvanced}>
    <summary>{t("model.advanced")}</summary>
    <p class="note">{t("model.advancedIntro")}</p>
    {#each ROUTES as route (route)}
      <RouteEditor {setup} {route} />
    {/each}
  </details>

  <div class="test">
    <button
      class={setup.current ? "secondary" : "primary"}
      disabled={!setup.ready || setup.testing}
      onclick={() => setup.test()}
    >
      {setup.testing ? t("model.testing") : setup.results ? t("model.retest") : t("model.test")}
    </button>
  </div>

  {#if errorText}<p class="error" role="alert">{errorText}</p>{/if}

  {#if setup.current && setup.results}
    <ConnectionResults {setup} results={setup.results} {settings} />
  {/if}
{/if}

{#if settings}
  {#if setup.saved}
    <SaveBar
      onsave={save}
      changed={!setup.unchangedSave}
      canSave={setup.canContinue}
      busy={setup.saving}
      saved={justSaved}
      {hint}
    />
  {/if}
{:else}
  <StepNav {hint} onnext={next} nextDisabled={!setup.canContinue} busy={setup.saving} />
{/if}

<style>
  .intro {
    max-width: 62ch;
    margin: 0 0 20px;
  }

  .label {
    font-size: 13px;
    font-weight: 400;
    color: var(--muted);
  }

  .mains {
    margin: 0 0 20px;
    padding: 0;
    border: 0;
    min-width: 0;
    max-width: 760px;
  }

  .mains legend {
    padding: 0;
    margin-bottom: 8px;
  }

  .mains .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 8px;
  }

  .opt {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--outer);
    cursor: pointer;
  }

  /* The radio stays focusable and announced; the tile is what shows. */
  .opt input {
    position: absolute;
    opacity: 0;
    width: 1px;
    height: 1px;
    margin: 0;
  }

  .opt:hover {
    border-color: var(--muted);
  }

  .opt:has(input:checked) {
    border-color: var(--accent);
    background: var(--sel);
  }

  .opt:has(input:focus-visible) {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .opt .name {
    font-weight: 600;
  }

  .opt .tag {
    margin-left: 6px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 400;
    color: var(--accent);
  }

  .opt .sub {
    font-size: 13px;
    color: var(--muted);
  }

  .mains > .note {
    margin: 8px 0 0;
    max-width: 62ch;
  }

  .other {
    color: var(--muted);
  }

  .other .model {
    margin-left: 8px;
  }

  .howto {
    max-width: 62ch;
    margin: 0 0 20px;
    padding: 12px 16px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--outer);
  }

  .howto h2 {
    margin: 0 0 6px;
  }

  .howto ol {
    margin: 0 0 8px;
    padding-left: 1.4em;
  }

  .howto li + li {
    margin-top: 6px;
  }

  .howto .note + .note {
    margin-top: 6px;
  }

  .howto a {
    color: var(--accent);
    white-space: nowrap;
  }

  .key {
    max-width: 620px;
  }

  .key-row {
    display: flex;
    gap: 8px;
  }

  .key-row .input {
    flex: 1;
    min-width: 0;
  }

  .plan {
    margin: 16px 0 0;
    max-width: 620px;
  }

  .plan ul {
    list-style: none;
    margin: 4px 0 0;
    padding: 0;
  }

  .plan li {
    display: grid;
    grid-template-columns: 7em minmax(0, 1fr);
    column-gap: 12px;
    padding: 2px 0;
  }

  .plan .model {
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
    overflow-wrap: anywhere;
  }

  .advanced {
    margin: 20px 0 0;
    max-width: 760px;
  }

  .advanced summary {
    display: inline-flex;
    align-items: center;
    min-height: 36px;
    color: var(--accent);
    cursor: pointer;
  }

  .advanced summary::before {
    content: "▸";
    width: 1.2em;
    font-family: var(--mono);
  }

  .advanced[open] summary::before {
    content: "▾";
  }

  .advanced > .note {
    margin: 4px 0 12px;
    max-width: 62ch;
  }

  .advanced :global(.route) {
    margin-top: 12px;
  }

  .test {
    margin: 20px 0 12px;
  }

  .test button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .error {
    margin: 0 0 12px;
    color: var(--err);
  }
</style>
