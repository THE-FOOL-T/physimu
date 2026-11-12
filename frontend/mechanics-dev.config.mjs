import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";

// Isolated lab entry: local fixtures outside frontend/, no backend proxy.
export default defineConfig({
  server: {
    host: "127.0.0.1",
    strictPort: true,
    fs: { allow: [fileURLToPath(new URL("../", import.meta.url))] },
  },
});
