import en from "./locales/en.json";
import zhCN from "./locales/zh-CN.json";
import zhHant from "./locales/zh-Hant.json";
import ja from "./locales/ja.json";
import ko from "./locales/ko.json";
import fr from "./locales/fr.json";
import es from "./locales/es.json";
import de from "./locales/de.json";

export type MessageKey = keyof typeof en;

/** English is the source catalog; any other may lack keys and falls back to it. */
const catalogs = {
  en,
  "zh-CN": zhCN,
  "zh-Hant": zhHant,
  ja,
  ko,
  fr,
  es,
  de,
} satisfies Record<string, Partial<Record<MessageKey, string>>>;
export type Locale = keyof typeof catalogs;

const STORAGE_KEY = "ankinote.locale";

function initial(): Locale {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && saved in catalogs) return saved as Locale;
  } catch {
    // Storage blocked: fall through to the browser language.
  }
  return fromBrowser(navigator.language);
}

/** The interface language closest to a browser language tag, or English. */
function fromBrowser(tag: string): Locale {
  const lower = tag.toLowerCase();
  if (lower.startsWith("zh")) {
    return /^zh-(hant|tw|hk|mo)/.test(lower) ? "zh-Hant" : "zh-CN";
  }
  const base = lower.split("-")[0]!;
  return base in catalogs ? (base as Locale) : "en";
}

class I18n {
  locale = $state<Locale>(initial());

  constructor() {
    $effect.root(() => {
      $effect(() => {
        document.documentElement.lang = this.locale;
        try {
          localStorage.setItem(STORAGE_KEY, this.locale);
        } catch {
          // Not persisted.
        }
      });
    });
  }

}

export const i18n = new I18n();

/** The interface languages, each named in itself so anyone can find their own. */
export const locales: { id: Locale; name: string }[] = [
  { id: "en", name: "English" },
  { id: "zh-CN", name: "简体中文" },
  { id: "zh-Hant", name: "繁體中文" },
  { id: "ja", name: "日本語" },
  { id: "ko", name: "한국어" },
  { id: "fr", name: "Français" },
  { id: "es", name: "Español" },
  { id: "de", name: "Deutsch" },
];

/** Translate `key`, replacing `{name}` placeholders from `vars`. */
export function t(key: MessageKey, vars: Record<string, string | number> = {}): string {
  // A missing key shows itself rather than crashing the page.
  const catalog: Partial<Record<MessageKey, string>> = catalogs[i18n.locale];
  const text: string = catalog[key] ?? en[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (_, name: string) => String(vars[name] ?? `{${name}}`));
}
