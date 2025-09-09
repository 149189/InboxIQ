import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to Django backend
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            // Forward cookies properly
            if (req.headers.cookie) {
              proxyReq.setHeader("cookie", req.headers.cookie);
              console.log("[VITE PROXY] Forwarding cookies:", req.headers.cookie);
            } else {
              console.log("[VITE PROXY] No cookies to forward");
            }
          });
          proxy.on("proxyRes", (proxyRes, req, res) => {
            // Forward Set-Cookie headers from Django
            if (proxyRes.headers['set-cookie']) {
              console.log("[VITE PROXY] Forwarding Set-Cookie:", proxyRes.headers['set-cookie']);
            }
          });
        },
      },
      // Proxy OAuth requests to Django backend
      "/auth/oauth": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            // Forward cookies properly
            if (req.headers.cookie) {
              proxyReq.setHeader("cookie", req.headers.cookie);
            }
          });
        },
      },
      // Proxy auth requests to Django backend
      "/auth": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            // Forward cookies properly
            if (req.headers.cookie) {
              proxyReq.setHeader("cookie", req.headers.cookie);
            }
          });
        },
      },
    },
  },
});
