const CACHE_NAME = 'immolibre-v124';
const OFFLINE_URL = '/index.html';

const ASSETS_TO_CACHE = [
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE).catch(() => cache.add('/index.html'));
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // 🛡️ v104 : NE JAMAIS intercepter les requêtes vers un autre domaine.
  // Le Service Worker hérite du Content-Security-Policy servi sur /sw.js, dont
  // connect-src n'autorise que Supabase et Nominatim. Résultat : quand le SW
  // relayait lui-même supabase-js (cdn.jsdelivr.net), Leaflet (unpkg) ou jsPDF
  // (cdnjs), le navigateur bloquait la requête → window.supabase indéfini →
  // écran de chargement infini. Symptôme : le site marchait en navigation privée
  // (pas de SW) mais pas dans l'app installée (toujours pilotée par le SW).
  // En laissant passer ces requêtes, le navigateur les charge lui-même, via
  // script-src qui, lui, autorise bien ces CDN.
  if (e.request.method !== 'GET') return;
  let sameOrigin = false;
  try { sameOrigin = new URL(e.request.url).origin === self.location.origin; } catch (err) { return; }
  if (!sameOrigin) return;

  e.respondWith(
    fetch(e.request)
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(e.request).then(cached => {
          if (cached) return cached;
          if (e.request.mode === 'navigate') return caches.match(OFFLINE_URL);
        });
      })
  );
});

self.addEventListener('push', (e) => {
  let data = { title: 'ImmoLibre 🏠', body: 'Vous avez un nouveau message !', icon: '/icon-192.png' };
  try { if (e.data) data = { ...data, ...e.data.json() }; }
  catch(err) { if (e.data) data.body = e.data.text(); }
  e.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      vibrate: [200, 100, 200],
      tag: 'immolibre-message',
      renotify: true,
    })
  );
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url.includes('immolibre.be') && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow('https://immolibre.be');
    })
  );
});
