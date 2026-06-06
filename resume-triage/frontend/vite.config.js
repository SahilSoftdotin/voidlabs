import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// VITE_DEMO=1 produces a single self-contained index.html (real UI + in-memory
// mock backend) that opens by double-click from file:// with no server.
//
// It is inlined as a CLASSIC <script> (IIFE), not type="module": browsers block
// module scripts loaded from file://, which renders a blank page. A classic
// inline script runs everywhere.
const DEMO = process.env.VITE_DEMO === "1";

function inlineAsClassicScript() {
  return {
    name: "inline-as-classic-script",
    enforce: "post",
    transformIndexHtml(html, ctx) {
      if (!ctx.bundle) return html;
      let js = "";
      let css = "";
      for (const [name, item] of Object.entries(ctx.bundle)) {
        if (item.type === "chunk" && item.isEntry) js += item.code + "\n";
        else if (item.type === "asset" && name.endsWith(".css")) css += item.source + "\n";
      }
      // Strip the generated module/link tags, then inline as classic script + style.
      html = html
        .replace(/<script\b[^>]*><\/script>/g, "")
        .replace(/<link\b[^>]*rel="stylesheet"[^>]*>/g, "");
      // Use replacement FUNCTIONS, not strings: the bundle contains `$&&`
      // (React), and `$&`/`$1` etc. are special patterns in a string replacement.
      html = html.replace("</head>", () => `<style>${css}</style></head>`);
      html = html.replace("</body>", () => `<script>${js}</script></body>`);
      return html;
    },
  };
}

export default defineConfig({
  base: DEMO ? "./" : "/",
  plugins: [react(), ...(DEMO ? [inlineAsClassicScript()] : [])],
  build: DEMO
    ? {
        cssCodeSplit: false,
        rollupOptions: {
          output: { format: "iife", inlineDynamicImports: true },
        },
      }
    : {},
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
