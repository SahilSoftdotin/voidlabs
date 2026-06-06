import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

// VITE_DEMO=1 produces a single self-contained index.html (real UI + in-memory
// mock backend) that opens from file:// with no server — used for previews.
const DEMO = process.env.VITE_DEMO === "1";

export default defineConfig({
  base: DEMO ? "./" : "/",
  plugins: [react(), ...(DEMO ? [viteSingleFile()] : [])],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
