import path from "path"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig, type Plugin } from "vite"

import { cloudflare } from "@cloudflare/vite-plugin";

function inlineCss(): Plugin {
  return {
    name: "inline-css",
    apply: "build",
    enforce: "post",
    generateBundle(_options, bundle) {
      const html = Object.values(bundle).find(
        (file) => file.type === "asset" && file.fileName.endsWith(".html")
      )
      if (!html || html.type !== "asset") return

      let source = String(html.source)
      for (const [fileName, file] of Object.entries(bundle)) {
        if (file.type !== "asset" || !fileName.endsWith(".css")) continue
        const href = fileName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
        const link = new RegExp(`<link[^>]*href="[^"]*${href}"[^>]*>`)
        if (!link.test(source)) continue
        source = source.replace(link, `<style>${String(file.source)}</style>`)
        delete bundle[fileName]
      }
      html.source = source
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), inlineCss(), cloudflare()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
})