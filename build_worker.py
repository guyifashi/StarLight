import json

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

manifest_dict = {
    "name": "星光少女成长打卡站",
    "short_name": "星光打卡",
    "description": "每日习惯任务打卡、早鸟工整加成与积分商城",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0f172a",
    "theme_color": "#6366f1",
    "icons": [
        {
            "src": "/icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}

manifest_json_str = json.dumps(manifest_dict, ensure_ascii=False, indent=2)

sw_content = """const CACHE_NAME = 'starlight-pwa-v2';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. KV API 请求：Network-first，断网返回离线标记
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ ok: false, offline: true, message: '离线模式' }), {
          headers: { 'Content-Type': 'application/json' },
        });
      })
    );
    return;
  }

  // 2. 静态页面与 CDN 资源：Stale-While-Revalidate + Cache fallback
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse && (networkResponse.status === 200 || networkResponse.type === 'opaque')) {
          const resClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, resClone));
        }
        return networkResponse;
      }).catch(() => null);

      if (cachedResponse) {
        return cachedResponse;
      }

      return fetchPromise.then((networkResponse) => {
        if (networkResponse) return networkResponse;
        return caches.match('/');
      });
    })
  );
});
"""

icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="starlightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5" />
      <stop offset="50%" stop-color="#6366f1" />
      <stop offset="100%" stop-color="#ec4899" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <rect width="512" height="512" rx="128" fill="url(#starlightGrad)" />
  <path d="M256 64 L310 185 L440 200 L342 290 L370 420 L256 352 L142 420 L170 290 L72 200 L202 185 Z" fill="#ffffff" filter="url(#glow)" />
  <circle cx="395" cy="115" r="32" fill="#fef08a" />
</svg>"""

worker_code = f"""export default {{
  async fetch(request, env, ctx) {{
    const url = new URL(request.url);

    // CORS 预检支持
    if (request.method === 'OPTIONS') {{
      return new Response(null, {{
        headers: {{
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        }},
      }});
    }}

    // ========================================================================
    // 路由 1：PWA Manifest (/manifest.json)
    // ========================================================================
    if (url.pathname === '/manifest.json' || url.pathname === '/manifest.webmanifest') {{
      return new Response(MANIFEST_JSON, {{
        headers: {{
          'Content-Type': 'application/manifest+json; charset=UTF-8',
          'Cache-Control': 'public, max-age=86400',
          'X-Content-Type-Options': 'nosniff',
        }},
      }});
    }}

    // ========================================================================
    // 路由 2：PWA Service Worker (/sw.js)
    // ========================================================================
    if (url.pathname === '/sw.js') {{
      return new Response(SERVICE_WORKER_JS, {{
        headers: {{
          'Content-Type': 'application/javascript; charset=UTF-8',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Service-Worker-Allowed': '/',
          'X-Content-Type-Options': 'nosniff',
        }},
      }});
    }}

    // ========================================================================
    // 路由 3：高清 App 图标 (/icon.svg)
    // ========================================================================
    if (url.pathname === '/icon.svg') {{
      return new Response(ICON_SVG, {{
        headers: {{
          'Content-Type': 'image/svg+xml; charset=UTF-8',
          'Cache-Control': 'public, max-age=604800',
        }},
      }});
    }}

    // ========================================================================
    // 路由 4：KV 云端状态读写 API (/api/state?space=xxx)
    // ========================================================================
    if (url.pathname === '/api/state') {{
      const rawSpace = (url.searchParams.get('space') || 'default').trim().toLowerCase();
      const spaceId = /^[a-z0-9_-]{{1,24}}$/.test(rawSpace) ? rawSpace : 'default';
      const kvKey = `STARLIGHT_SPACE_V3_${{spaceId}}`;

      const kvStore = env.STARLIGHT_KV || env.KV || env.starlight_kv || env.kv || env.STARLIGHT || env.STORAGE;
      if (!kvStore) {{
        return jsonResponse({{
          ok: false,
          kvBound: false,
          message: '未检测到 STARLIGHT_KV 绑定，当前仅使用浏览器本地存储'
        }}, 200);
      }}

      if (request.method === 'GET') {{
        try {{
          const data = await kvStore.get(kvKey, {{ type: 'json' }});
          return jsonResponse({{
            ok: true,
            kvBound: true,
            space: spaceId,
            data: data || null
          }});
        }} catch (err) {{
          return jsonResponse({{ ok: false, error: err.message }}, 500);
        }}
      }}

      if (request.method === 'POST') {{
        try {{
          // 限制单次 Payload 大小（最大 512KB）
          const contentLength = parseInt(request.headers.get('content-length') || '0', 10);
          if (contentLength > 524288) {{
            return jsonResponse({{ ok: false, error: 'Payload too large (max 512KB)' }}, 413);
          }}

          const body = await request.json();
          if (!body || typeof body !== 'object') {{
            return jsonResponse({{ ok: false, error: 'Invalid payload' }}, 400);
          }}
          body.updatedAt = Date.now();
          await kvStore.put(kvKey, JSON.stringify(body));
          return jsonResponse({{
            ok: true,
            kvBound: true,
            space: spaceId,
            updatedAt: body.updatedAt
          }});
        }} catch (err) {{
          return jsonResponse({{ ok: false, error: err.message }}, 500);
        }}
      }}
    }}

    // ========================================================================
    // 路由 5：返回内嵌完整前端单页 HTML
    // ========================================================================
    return new Response(HTML_PAGE, {{
      headers: {{
        'Content-Type': 'text/html; charset=UTF-8',
        'Cache-Control': 'no-cache',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
      }},
    }});
  }},
}};

function jsonResponse(obj, status = 200) {{
  return new Response(JSON.stringify(obj), {{
    status,
    headers: {{
      'Content-Type': 'application/json; charset=UTF-8',
      'Cache-Control': 'no-store',
      'Access-Control-Allow-Origin': '*',
      'X-Content-Type-Options': 'nosniff',
    }},
  }});
}}

const MANIFEST_JSON = {repr(manifest_json_str)};

const SERVICE_WORKER_JS = {repr(sw_content)};

const ICON_SVG = {repr(icon_svg)};

const HTML_PAGE = {repr(html_content)};
"""

with open('worker.js', 'w', encoding='utf-8') as f:
    f.write(worker_code)

with open('cloudflare_worker.js', 'w', encoding='utf-8') as f:
    f.write(worker_code)

print("Build completed successfully!")
