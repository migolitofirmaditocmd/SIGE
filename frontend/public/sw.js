/**
 * SIGE Service Worker v1.0.0
 * Escuela Secundaria Mixta 5
 *
 * Reglas de seguridad mandatorias (RN-TRX-01, RN-TRX-02, SEG §1):
 * 1. NUNCA interceptar ni almacenar en caché peticiones a '/api/*'.
 * 2. Precachear únicamente el shell de la aplicación y recursos estáticos.
 */

const CACHE_NAME = "sige-shell-v1";
const STATIC_ASSETS = [
  "/",
  "/manifest.webmanifest",
  "/favicon.ico"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // REGLA CRÍTICA: La API siempre va directo a la red (sin caché)
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  // Estrategia Network First con fallback a caché para navegación y estáticos
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(event.request).then((response) => {
          return response || caches.match("/");
        });
      })
    );
    return;
  }

  // Recursos estáticos
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
