// Upstream data sources for transport and school news.
//
// These hosts send no Access-Control-Allow-Origin header, so they used to be
// fetched through corsproxy.io. That service dropped anonymous legacy URLs and
// now answers every such request with 403 keyless_legacy_url, which took the
// whole 交通 page and 校網 down at once.
//
// The shipped app no longer proxies at all: CapacitorHttp (enabled in
// src-capacitor/capacitor.config.json) performs requests natively, where
// browser CORS rules do not apply. `quasar dev` does run in a real browser, so
// in dev the same URLs are rewritten onto the devServer proxy declared in
// quasar.config.js.

const DEV_PROXY_PREFIX = {
  "https://tcgbusfs.blob.core.windows.net": "/upstream/youbike-tpc",
  "https://data.ntpc.gov.tw": "/upstream/youbike-ntc",
  "https://api.metro.taipei": "/upstream/metro",
  "https://www.ck.tp.edu.tw": "/upstream/school",
};

export const upstreamUrl = (url) => {
  if (!process.env.DEV) return url;
  const origin = Object.keys(DEV_PROXY_PREFIX).find((o) => url.startsWith(o));
  return origin ? DEV_PROXY_PREFIX[origin] + url.slice(origin.length) : url;
};

export const YOUBIKE_TPC_URL =
  "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json";

// The New Taipei dataset is paginated, so both pages are always needed.
export const YOUBIKE_NTC_URLS = [
  "https://data.ntpc.gov.tw/api/datasets/010e5b15-3823-4b20-b401-b1cf000550c5/json?size=1000",
  "https://data.ntpc.gov.tw/api/datasets/010e5b15-3823-4b20-b401-b1cf000550c5/json?page=1&size=1000",
];

export const SCHOOL_NEWS_URLS = [
  "https://www.ck.tp.edu.tw/nss/main/feeder/5abf2d62aa93092cee58ceb4/KG5mY0d9355?f=normal&%240=hhyrNQJ0110&vector=private&static=false",
  "https://www.ck.tp.edu.tw/nss/main/feeder/5abf2d62aa93092cee58ceb4/IXZld9j7619?f=normal&%240=kpenVCJ9015&vector=private&static=false",
];
