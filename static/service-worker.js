self.addEventListener('install', event => {
    event.waitUntil(
        caches.open('gestantes-cache').then(cache => {
            return cache.addAll([
                '/',
                '/static/script.js',
                '/static/manifest.json',
                '/static/icon-192x192.png',
                '/static/icon-512x512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(name => name !== 'gestantes-cache')
                    .map(name => caches.delete(name))
            );
        })
    );
});