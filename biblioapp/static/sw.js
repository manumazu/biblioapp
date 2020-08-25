// Le nom du cache est important.
// On peut invalider un cache en changeant son nom
const CACHE_ASSETS = 'assets-wyb878klq8';
const CACHE_CONTENT = 'content-wnjsn19vjn';

const assetsList = [
  "/static/img/three-books_white.svg",
  "/static/img/presentation_2_1852x1040.jpg",
  "/static/app.css",
  "/static/index.css",
  "/static/app.js",
];

const contentList = [
    "/",
    "/offline",
];

self.addEventListener('install', function(event) {
  // Installation du service worker
  event.waitUntil(
    // On utillise le cache des assets
    caches.open(CACHE_ASSETS)
      .then(function(cache) {
        return cache.addAll(assetsList);
      })
  );

  event.waitUntil(
    // On utillise le cache des contenus
    caches.open(CACHE_CONTENT)
      .then(function(cache) {
        return cache.addAll(contentList);
      })
  );
});

self.addEventListener('activate', function(event) {

  // Définition des clés de conteneurs de cache à jour
  var cacheWhitelist = [CACHE_ASSETS, CACHE_CONTENT];

  event.waitUntil(
    // Récupération de tous les conteneurs de cache existants sur le périmètre
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          // Si le conteneur de cache ne fait pas partie de la liste à jour, on le purge
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', function(event) {
  const requestUrl = new URL(
    event.request.url
  );

  if (requestUrl.pathname.startsWith("/static")) {
    // On ouvre le cache des assets
    const promiseResponse = caches.open(CACHE_ASSETS)
      .then(function(cache) {
        // On cherche si la requête existe dans le cache
        return cache.match(event.request)
          .then(function(response) {
            if (response) {
              // Si la requête existe dans le cache, on renvoie la réponse trouvée
              return response;
            } else {
              // Sinon on va chercher la ressource sur le serveur
              return fetch(event.request)
                .then(function(response) {
                  // Une fois qu'on a reçu la réponse, on met en cache pour la prochaine fois.
                  // On n'oublie pas de cloner la réponse pour pouvoir la mettre en cache.
                  // Une réponse ne peut être lue qu'une seule fois, d'où le clone.
                  cache.put(
                    event.request,
                    response.clone()
                  );

                  // Et on retourne la réponse
                  return response;
                });
            }
          });

    });

    // Une fois que la promesse a fini de s'exécuter, on envoie la réponse
    event.respondWith(promiseResponse);
  } else {
    event.respondWith(
      caches.open(CACHE_CONTENT).then((cache) => {
        return fetch(event.request)
          .then((response) => {
            // Si la réponse est ok on la stocke en cache et l'envoie.
            if (response.status === 200) {
              cache.put(event.request.url, response.clone());
            }
            return response;
          })
          .catch((err) => {
            // Si on a perdu le réseau on va chercher la requête dans le cache ou on renvoie le fallback offline.
            return cache.match(event.request)
              .then((response) => {
                return response || cache.match('/offline');
              });
          });
    }));
  }
});
