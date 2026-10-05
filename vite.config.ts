/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// GitHub Pages serves the site from /<repo>/. Override with BASE_PATH (e.g. "/") for other hosts.
const base = process.env.BASE_PATH ?? '/bedtime-stories/';

export default defineConfig({
  base,
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false,
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        id: base,
        name: 'Storybook',
        short_name: 'Storybook',
        description: "Public-domain children's stories for bedtime.",
        start_url: base,
        scope: base,
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#f6efe1',
        theme_color: '#f6efe1',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          {
            src: 'icon-maskable-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}', 'compendium/index.json'],
        globIgnores: ['compendium/stories/**', 'compendium/images/**'],
        navigateFallback: 'index.html',
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.includes('/compendium/stories/'),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'stories',
              expiration: { maxEntries: 400 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            urlPattern: ({ url }) => url.pathname.includes('/compendium/images/'),
            handler: 'CacheFirst',
            options: {
              cacheName: 'images',
              expiration: { maxEntries: 150, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
