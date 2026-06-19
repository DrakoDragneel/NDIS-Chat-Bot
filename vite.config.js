import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    rollupOptions: {
      output: {
        // Predictable names so the WordPress plugin can enqueue them.
        entryFileNames: "assets/ndis-chatbot.js",
        chunkFileNames: "assets/ndis-chatbot-[name].js",
        assetFileNames: "assets/ndis-chatbot.[ext]",
      },
    },
  },
});
