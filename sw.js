// Service Worker — Offline-first cache for Grass Animal Tester
const CACHE_NAME = "grass-tester-v3";

// Shell files to precache on install
const PRECACHE = [
  "./index.html",
  "./manifest.json",
  "./assets/Tools.png",
  "./assets/icon-192.png",
  "./assets/icon-512.png",
  "./assets/forest/sprout_grass.png",
  "./assets/forest/sprout_water.png"
];

self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE))
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Cache-first for assets, but network-first for index.html/entry pages
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;

  const isHtml = url.pathname.endsWith("/") || url.pathname.endsWith("/index.html");

  if (isHtml) {
    // Network-first: try network first, fallback to cache if offline
    event.respondWith(
      fetch(event.request).then(response => {
        if (response && response.status === 200) {
          const toCache = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, toCache));
          return response;
        }
        return response;
      }).catch(() => {
        return caches.match(event.request).then(cached => cached || new Response("", { status: 204 }));
      })
    );
  } else {
    // Cache-first for same-origin static assets
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== "basic") return response;
          const toCache = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, toCache));
          return response;
        }).catch(() => new Response("", { status: 204 }));
      })
    );
  }
});
