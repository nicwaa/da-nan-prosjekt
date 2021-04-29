const cache_navn = 'mellomlager';

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches
            .open(cache_navn)
            .then(
                function (cache) {
                    return cache.addAll([
                        './index.html',
                        './stiler.css',
                        './Capture.png',
                        './favicon.ico',
                        './test.html'
                    ]);
                }
            )
    );
});

self.addEventListener('activate', (e) => {
    console.log('Service worker: activated')
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request).then((resp) => {
            return resp || fetch(event.request).then((response) => {
                return caches.open(cache_navn).then((cache) => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
        })
    );
});
