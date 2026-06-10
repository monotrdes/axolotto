// Minimal Service Worker for Axolotto PWA Installability
const CACHE_NAME = 'axolotto-cache-v1';

self.addEventListener('install', (event) => {
  // Activate immediately when installed
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Take control of all pages immediately
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Standard network-first / bypass pass-through.
  // We do not cache assets in SW to avoid cache-busting issues with Next.js updates.
  // The browser's native HTTP cache and Next.js static optimizations are sufficient.
  event.respondWith(
    fetch(event.request).catch(() => {
      // Return a basic offline response if the network fails completely
      return new Response('Red no disponible. Por favor, revisa tu conexión a internet.', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: new Headers({ 'Content-Type': 'text/plain; charset=utf-8' }),
      });
    })
  );
});
