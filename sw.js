const CACHE_NAME = 'immolibre-v130';
const OFFLINE_URL = '/index.html';

const ASSETS_TO_CACHE = [
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
  '/data/cities.js',
  '/vendor/supabase-js-2.117.2.min.js',
];

// ⚡ v125 : au-delà de ce délai, si une version en cache existe, on l'affiche tout de suite
// (la version réseau continue de se télécharger en arrière-plan pour la prochaine fois).
// Avant, le Service Worker attendait le réseau sans limite : en 3G faible / Wi-Fi saturé,
// le site restait plusieurs secondes sur l'écran de chargement.
const NETWORK_TIMEOUT_MS = 3500;

function putInCache(request, response){
  if(response && response.ok){
    const clone = response.clone();
    caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
  }
  return response;
}

// Page HTML : réseau d'abord, mais pas plus de NETWORK_TIMEOUT_MS s'il existe une copie en cache.
function handleNavigation(e){
  const network = fetch(e.request).then(r => putInCache(e.request, r));
  e.waitUntil(network.catch(() => {}));
  const cachedPage = caches.match(e.request).then(c => c
    || (new URL(e.request.url).pathname === '/' ? caches.match(OFFLINE_URL) : undefined));
  return new Promise(resolve => {
    let done = false;
    const finish = r => { if(!done && r){ done = true; resolve(r); } };
    network.then(finish).catch(async () => {
      // Hors ligne ou erreur réseau : copie en cache, sinon l'accueil en cache.
      finish((await cachedPage) || (await caches.match(OFFLINE_URL)) || Response.error());
    });
    setTimeout(() => cachedPage.then(finish), NETWORK_TIMEOUT_MS);
  });
}

// Bibliothèques versionnées (/vendor/…) : le nom change à chaque version → le cache suffit.
function handleVendor(e){
  return caches.match(e.request).then(c => c || fetch(e.request).then(r => putInCache(e.request, r)));
}

// Autres fichiers du site (villes, icônes, manifest…) : copie en cache immédiate si elle existe,
// mise à jour en arrière-plan.
function handleStatic(e){
  const network = fetch(e.request).then(r => putInCache(e.request, r));
  e.waitUntil(network.catch(() => {}));
  return caches.match(e.request).then(c => c || network);
}

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

  const path = new URL(e.request.url).pathname;
  if(e.request.mode === 'navigate') e.respondWith(handleNavigation(e));
  else if(path.startsWith('/vendor/')) e.respondWith(handleVendor(e));
  else e.respondWith(handleStatic(e));
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
