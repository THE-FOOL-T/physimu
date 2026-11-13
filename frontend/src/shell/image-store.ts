import type { Netlist } from "../domains/circuit/types";

/** Own only URLs created here; ordinary demo URLs are never revoked. */
export class ImageStore {
  private urls = new Set<string>();
  fromData(url: string): string {
    if (!url.startsWith("data:")) return url;
    const comma = url.indexOf(","),
      header = url.slice(0, comma),
      encoded = url.slice(comma + 1);
    const content = header.includes(";base64")
      ? Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0))
      : decodeURIComponent(encoded);
    const blob = new Blob([content], {
      type: header.match(/^data:([^;]+)/)?.[1] || "image/png",
    });
    return this.fromBlob(blob);
  }
  fromBlob(blob: Blob): string {
    const url = URL.createObjectURL(blob);
    this.urls.add(url);
    return url;
  }
  clear() {
    for (const url of this.urls) URL.revokeObjectURL(url);
    this.urls.clear();
  }
}
export function withoutImage(net: Netlist): Netlist {
  return { ...net, image: { ...net.image, path: "" } };
}
export async function selfContained(net: Netlist): Promise<Netlist> {
  if (!net.image.path.startsWith("blob:")) return net;
  const blob = await (await fetch(net.image.path)).blob();
  const data = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
  return { ...net, image: { ...net.image, path: data } };
}
