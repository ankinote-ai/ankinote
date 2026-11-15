/**
 * Everything the card preview frame shows is fetched here, by the app page,
 * and handed over inline.
 *
 * The frame is sandboxed without same-origin, so the browser sends its own
 * requests without the app's cookies. Behind a login gateway (a reverse proxy
 * or NAS portal) those requests get a 401 or a redirect, and the card shows
 * without its picture, fonts or formulas. Requests from this page carry the
 * cookies, so the frame never has to make one.
 */

const cache = new Map<string, Promise<string>>();

function once(key: string, make: () => Promise<string>): Promise<string> {
  let hit = cache.get(key);
  if (!hit) {
    hit = make().catch((error) => {
      cache.delete(key); // a failed fetch may work next time
      throw error;
    });
    cache.set(key, hit);
  }
  return hit;
}

function toDataUri(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

/** A same-origin file as a `data:` URI (its own URL when it can't be fetched). */
export function dataUri(url: string): Promise<string> {
  return once(`data:${url}`, async () => {
    try {
      const response = await fetch(url, { credentials: "same-origin" });
      if (!response.ok) return url;
      return await toDataUri(await response.blob());
    } catch {
      return url;
    }
  });
}

/** The page's own paths only: `/api/...`, not other sites or protocols. */
const APP_PATH = /^\/(?!\/)/;

async function replaceAsync(
  text: string,
  pattern: RegExp,
  make: (url: string) => Promise<string>,
  group: number,
): Promise<string> {
  const matches = [...text.matchAll(pattern)];
  const uris = await Promise.all(matches.map((m) => make(m[group]!)));
  let at = 0;
  let out = "";
  matches.forEach((m, i) => {
    const start = m.index + m[0].indexOf(m[group]!);
    out += text.slice(at, start) + uris[i];
    at = start + m[group]!.length;
  });
  return out + text.slice(at);
}

/** Card CSS with its app-served fonts and images inlined. */
export function inlineCss(css: string): Promise<string> {
  return replaceAsync(
    css,
    /url\(\s*(["']?)(\/[^"')\s]+)\1\s*\)/g,
    (url) => (APP_PATH.test(url) ? dataUri(url) : Promise.resolve(url)),
    2,
  );
}

/** Card HTML with its app-served `<img>` sources inlined. */
export function inlineImages(html: string): Promise<string> {
  return replaceAsync(
    html,
    /<img\b[^>]*?\bsrc=(["'])(\/[^"']+)\1/gi,
    (url) => (APP_PATH.test(url) ? dataUri(url) : Promise.resolve(url)),
    2,
  );
}

/** The MathJax script's text, to put in the frame's own page. */
export function mathjaxSource(url: string): Promise<string> {
  return once(`script:${url}`, async () => {
    const response = await fetch(url, { credentials: "same-origin" });
    if (!response.ok) throw new Error(`MathJax: HTTP ${response.status}`);
    // A script can't hold the end tag of the element that carries it.
    return (await response.text()).replaceAll("</script", "<\\/script");
  });
}
