/** A picture of a STEM question, ready to send: shrunk, and as base64. */
export type Picture = {
  /** Base64, without the `data:` prefix. */
  data: string;
  mime: "image/png" | "image/jpeg" | "image/webp";
  /** What an <img> shows. */
  url: string;
};

export type PictureErrorCode = "type" | "big" | "read";

export class PictureError extends Error {
  constructor(readonly code: PictureErrorCode) {
    super(code);
  }
}

const TYPES = ["image/png", "image/jpeg", "image/webp"] as const;
/** The server takes 5 MB; a longer edge only costs tokens, not readability. */
const MAX_BYTES = 5 * 1024 * 1024;
const MAX_EDGE = 2000;
/** Left as it is when it's small and already within the edge limit. */
const KEEP_BYTES = 1.5 * 1024 * 1024;

export function isPicture(file: File): boolean {
  return (TYPES as readonly string[]).includes(file.type);
}

/** The first picture in a paste or drop, if there is one. */
export function pictureIn(files: FileList | File[] | null | undefined): File | null {
  return Array.from(files ?? []).find(isPicture) ?? null;
}

function readAsDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new PictureError("read"));
    reader.readAsDataURL(blob);
  });
}

async function shrink(file: File): Promise<Blob> {
  const bitmap = await createImageBitmap(file).catch(() => {
    throw new PictureError("read");
  });
  const scale = Math.min(1, MAX_EDGE / Math.max(bitmap.width, bitmap.height));
  if (scale === 1 && file.size <= KEEP_BYTES) {
    bitmap.close();
    return file;
  }
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  const context = canvas.getContext("2d");
  if (!context) throw new PictureError("read");
  // JPEG has no transparency: a transparent screenshot would turn black.
  context.fillStyle = "#fff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, "image/jpeg", 0.9),
  );
  if (!blob) throw new PictureError("read");
  return blob;
}

/** Shrink `file` if it's large, and encode it for the server. */
export async function readPicture(file: File): Promise<Picture> {
  if (!isPicture(file)) throw new PictureError("type");
  const blob = await shrink(file);
  if (blob.size > MAX_BYTES) throw new PictureError("big");
  const url = await readAsDataUrl(blob);
  const [head, data] = url.split(",", 2) as [string, string];
  const mime = head.slice(5, head.indexOf(";")) as Picture["mime"];
  return { data, mime, url };
}
