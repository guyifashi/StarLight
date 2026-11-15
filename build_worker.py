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

icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- 深邃梦幻夜空渐变 -->
    <linearGradient id="nightSky" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080C1B" />
      <stop offset="35%" stop-color="#111638" />
      <stop offset="70%" stop-color="#1E1B4B" />
      <stop offset="100%" stop-color="#311042" />
    </linearGradient>

    <!-- 柔金月牙渐变 -->
    <linearGradient id="moonGlowGrad" x1="20%" y1="10%" x2="90%" y2="100%">
      <stop offset="0%" stop-color="#FFFBEB" />
      <stop offset="30%" stop-color="#FEF08A" />
      <stop offset="75%" stop-color="#FBBF24" />
      <stop offset="100%" stop-color="#F59E0B" />
    </linearGradient>

    <!-- 星芒柔白渐变 -->
    <linearGradient id="starLightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="60%" stop-color="#FDE047" />
      <stop offset="100%" stop-color="#F59E0B" />
    </linearGradient>

    <!-- 梦幻星云光晕渐变 -->
    <radialGradient id="nebulaGlow" cx="50%" cy="45%" r="60%">
      <stop offset="0%" stop-color="#818CF8" stop-opacity="0.35" />
      <stop offset="50%" stop-color="#C084FC" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#1E1B4B" stop-opacity="0" />
    </radialGradient>

    <!-- 柔和发光滤镜 -->
    <filter id="glowFilter" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="10" result="blur1" />
      <feGaussianBlur stdDeviation="20" result="blur2" />
      <feMerge>
        <feMergeNode in="blur2" />
        <feMergeNode in="blur1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- 微星点滤镜 -->
    <filter id="starGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- 1. 圆角应用底座（符合 Apple iOS 与 Android Maskable 图标规范） -->
  <rect width="512" height="512" rx="118" fill="url(#nightSky)" />

  <!-- 2. 星云扩散光晕 -->
  <circle cx="260" cy="240" r="230" fill="url(#nebulaGlow)" />

  <!-- 3. 背景璀璨微星群 -->
  <g opacity="0.85">
    <circle cx="90" cy="110" r="2" fill="#FFFFFF" opacity="0.6" />
    <circle cx="140" cy="80" r="3" fill="#FDE047" opacity="0.75" filter="url(#starGlow)" />
    <circle cx="220" cy="65" r="1.8" fill="#FFFFFF" opacity="0.5" />
    <circle cx="370" cy="85" r="2.5" fill="#FDE047" opacity="0.7" />
    <circle cx="435" cy="130" r="2" fill="#FFFFFF" opacity="0.6" />
    <circle cx="440" cy="280" r="3" fill="#C084FC" opacity="0.8" filter="url(#starGlow)" />
    <circle cx="400" cy="390" r="2.2" fill="#FFFFFF" opacity="0.55" />
    <circle cx="105" cy="380" r="2" fill="#FDE047" opacity="0.6" />
    <circle cx="80" cy="260" r="2.5" fill="#C084FC" opacity="0.7" />
    <circle cx="165" cy="440" r="1.8" fill="#FFFFFF" opacity="0.45" />
    <circle cx="320" cy="445" r="2.2" fill="#FDE047" opacity="0.75" />
  </g>

  <!-- 4. 梦幻星轨弧线 -->
  <path d="M 80 340 C 140 430, 360 450, 440 310" stroke="#818CF8" stroke-width="1.5" stroke-dasharray="4 8" opacity="0.35" fill="none" />
  <path d="M 100 200 C 170 120, 340 110, 420 180" stroke="#C084FC" stroke-width="1.2" stroke-dasharray="3 7" opacity="0.28" fill="none" />

  <!-- 5. 主角：皎洁温润的月牙（采用几何布尔差集造型） -->
  <path d="M 285 105
           C 185 105, 110 185, 110 285
           C 110 375, 175 448, 260 460
           C 180 435, 145 340, 160 255
           C 175 180, 230 125, 285 105 Z"
        fill="url(#moonGlowGrad)"
        filter="url(#glowFilter)" />

  <!-- 6. 月弯怀抱中的守护四角主星 -->
  <g transform="translate(330, 225)" filter="url(#glowFilter)">
    <!-- 主星辉光四角星芒 -->
    <path d="M 0 -48 Q 0 0, -48 0 Q 0 0, 0 48 Q 0 0, 48 0 Q 0 0, 0 -48 Z" fill="url(#starLightGrad)" />
    <!-- 核心微星光核 -->
    <circle cx="0" cy="0" r="9" fill="#FFFFFF" />
  </g>

  <!-- 7. 伴星一（右上轻盈四角小星） -->
  <g transform="translate(395, 150) scale(0.48)" filter="url(#starGlow)">
    <path d="M 0 -42 Q 0 0, -42 0 Q 0 0, 0 42 Q 0 0, 42 0 Q 0 0, 0 -42 Z" fill="#FFFFFF" />
  </g>

  <!-- 8. 伴星二（左下灵动四角小星） -->
  <g transform="translate(195, 375) scale(0.38)" filter="url(#starGlow)">
    <path d="M 0 -42 Q 0 0, -42 0 Q 0 0, 0 42 Q 0 0, 42 0 Q 0 0, 0 -42 Z" fill="#FEF08A" />
  </g>

  <!-- 9. 伴星三（右下晶莹星点） -->
  <g transform="translate(365, 335) scale(0.32)" filter="url(#starGlow)">
    <path d="M 0 -42 Q 0 0, -42 0 Q 0 0, 0 42 Q 0 0, 42 0 Q 0 0, 0 -42 Z" fill="#FFFFFF" />
  </g>

  <!-- 10. 柔和星光光斑（点睛高光） -->
  <circle cx="240" cy="200" r="3.5" fill="#FFFFFF" opacity="0.9" filter="url(#starGlow)" />
  <circle cx="275" cy="310" r="2.5" fill="#FDE047" opacity="0.85" />
  <circle cx="315" cy="160" r="3" fill="#FFFFFF" opacity="0.75" />
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
