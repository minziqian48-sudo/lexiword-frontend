// LexiLearn Service Worker - PWA offline support
const CACHE_NAME = 'lexilearn-v5';
const STATIC_ASSETS = [
  './',
  './login.html',
  './Lexiword.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

// Install: cache static assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

// Activate: clean old caches (delete any cache that isn't current version)
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network-first for HTML (so updates always reach users), cache-first for assets
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API requests: always try network, don't cache
  if (url.pathname.includes('/api/')) {
    e.respondWith(fetch(e.request).catch(() => new Response('{"error":"offline"}', {headers: {'Content-Type': 'application/json'}})));
    return;
  }

  // HTML documents: network-first (always get fresh HTML, fall back to cache when offline)
  if (e.request.mode === 'navigate' || url.pathname.endsWith('.html')) {
    e.respondWith(
      fetch(e.request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return res;
      }).catch(() => caches.match(e.request).then(c => c || caches.match('./')))
    );
    return;
  }

  // Static assets (images, icons, css, js): cache-first, fallback to network
  e.respondWith(
    caches.match(e.request).then(cached => {
      return cached || fetch(e.request).then(res => {
        if (res.ok && e.request.method === 'GET') {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return res;
      }).catch(() => cached);
    })
  );
});
