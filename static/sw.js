const CACHE_NAME = 'resume-builder-pwa-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// 서비스 워커 설치: 정적 자원 사전 캐싱
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// 활성화: 이전 버전 캐시 정리
self.addEventListener('activate', (event) => {
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

// 네트워크 요청 가로채기 (Network First with Cache Fallback for dynamic, Cache First for static)
self.addEventListener('fetch', (event) => {
  // POST 요청(/generate 등 AI 생성 API)은 캐시하지 않고 항상 네트워크로 통과
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).catch(() => {
        // 오프라인 시 기본 캐시 페이지 반환
        return caches.match('/');
      });
    })
  );
});
