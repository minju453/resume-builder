const CACHE_NAME = 'resume-builder-pwa-v3';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// 서비스 워커 설치: 정적 자원 사전 캐싱 및 즉시 활성화
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// 활성화: 구버전 캐시 즉시 제거 및 모든 클라이언트 제어권 획득
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

// 네트워크 요청 가로채기: Network First 전략 (항상 최신 배포 우선, 오프라인 시 캐시 활용)
self.addEventListener('fetch', (event) => {
  // POST 요청(/generate 등 AI 생성 API)은 캐시하지 않고 항상 네트워크로 통과
  if (event.request.method !== 'GET') {
    return;
  }

  // Network First 전략: 네트워크에서 최신 버전을 먼저 가져오고 백그라운드 캐시 갱신
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // 정상 응답이면 캐시에 복사본 저장
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // 오프라인 상태일 때만 캐시에서 검색
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // 오프라인 상태에서 페이지 이동인 경우 메인 캐시 페이지 반환
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
      })
  );
});
