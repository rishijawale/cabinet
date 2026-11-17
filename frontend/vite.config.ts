import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
  },
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        // Split rarely changing vendors from route chunks so browsers can cache
        // them across deploys. Route components are already lazy, see App.tsx.
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "query-vendor": ["@tanstack/react-query"],
          motion: ["framer-motion"],
        },
      },
    },
  },
});
