// proxy_safe.js — фильтрующий прокси для Cloudflare Workers / других сред
// при необходимости установить за пределами заблокированного региона
// прокси прозрачно проксирует запросы к LLM ChatGPT
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetUrl = "https://api.openai.com" + url.pathname + url.search;

    // Заголовки, которые НЕЛЬЗЯ пересылать (черный список).
    const stripHeaders = new Set([
      "x-forwarded-for", "forwarded", "x-real-ip", "true-client-ip",
      "cf-connecting-ip", "cf-ipcountry", "x-country", "x-origin-country",
      "x-client-ip", "x-cluster-client-ip", "via",
      // любые кастомные заголовки, которые вы знаете содержат гео-данные
      "x-user-region", "x-user-country"
    ]);

    // Заголовки, которые разумно переписать/нормализовать
    const overrideHeaders = {
      // подставляем ваш серверный ключ (заменит ключ клиента, если был)
      "authorization": `Bearer ${env.OPENAI_API_KEY}`,
      // Установим более нейтральный User-Agent (или UA прокси)
      "user-agent": "Proxy/1.1 (+https://amazon.com)",
      // Установим безопасные значения локали
      "accept-language": "en-US,en;q=0.9",
      // явным образом укажем тип тела
      "content-type": "application/json"
    };

    // Берём исходные заголовки и фильтруем
    const incoming = Object.fromEntries(request.headers);
    const outHeaders = new Headers();

    for (const [k, v] of Object.entries(incoming)) {
      const lk = k.toLowerCase();
      if (stripHeaders.has(lk)) {
        // пропускаем
        continue;
      }
      // не копируем hop-by-hop заголовки (Transfer-Encoding и т.д.)
      if (["transfer-encoding", "connection", "keep-alive", "proxy-authorization", "proxy-authenticate", "upgrade"].includes(lk)) {
        continue;
      }
      // остальные можно копировать, но мы затем примем overrideHeaders
      outHeaders.set(k, v);
    }

    // явные переопределения (override)
    for (const [k, v] of Object.entries(overrideHeaders)) {
      outHeaders.set(k, v);
    }

    // Если тело — стрим, используем request.clone() чтобы не "съесть" оригинал
    const body = (request.method !== "GET" && request.method !== "HEAD") ? request.body : undefined;

    const response = await fetch(targetUrl, {
      method: request.method,
      headers: outHeaders,
      body: body,
    });

    // Фильтруем заголовки ответа чтобы не возвращать серверные/сервисные подсказки
    const resHeaders = new Headers();
    for (const [k, v] of response.headers) {
      const lk = k.toLowerCase();
      // удалим заголовки CDN/geo/info, и hop-by-hop
      if (["cf-ray", "server", "via", "x-powered-by", "x-request-id", "x-envoy-upstream-service-time"].includes(lk)) {
        continue;
      }
      resHeaders.set(k, v);
    }

    // Можно добавить/нормализовать заголовки ответа, например CORS, если нужно:
    resHeaders.set("Access-Control-Allow-Origin", "*");

    return new Response(response.body, {
      status: response.status,
      headers: resHeaders
    });
  }
};
