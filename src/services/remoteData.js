// Every data set the app reads -- class schedules, restaurant listings, the
// term 行事曆 -- lives in the companion Data repo and is fetched from there.
//
// None of it is bundled. A bundled copy is a second source of truth, and the
// two drift: restaurantData.json sat 7 months behind the app's own copy before
// anyone noticed, because nothing forces them to agree. The Data repo is now
// the only place this data exists, so correcting it never needs an app release.
//
// The cost of that is a network dependency, which the cache below covers: each
// successful fetch is stored, and a later failure falls back to the last good
// copy. Only a first-ever launch with no connectivity comes up empty.

import axios from "axios";

const DATA_BASE = "https://raw.githubusercontent.com/CKApp-Dev/Data/main";

const TIMEOUT_MS = 8000;
const CACHE_PREFIX = "dataCache:";

function readCache(path) {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + path);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(path, data) {
  try {
    localStorage.setItem(CACHE_PREFIX + path, JSON.stringify(data));
  } catch (err) {
    // A full quota shouldn't take the fetch down with it.
    console.warn(`[data] could not cache ${path}: ${err.message}`);
  }
}

/**
 * Fetch a JSON file from the Data repo, falling back to the last cached copy.
 *
 * @param {string} path  path within the Data repo, e.g. "restaurantData.json"
 * @param {(data:*) => boolean} isValid  shape check. raw.githubusercontent
 *   answers a missing path with an HTML error page rather than an error status,
 *   so the payload is checked before it is trusted or cached.
 * @returns {Promise<*|null>} the data, or null if the network failed and
 *   nothing was cached.
 */
export async function fetchData(path, isValid = () => true) {
  try {
    const { data } = await axios.get(`${DATA_BASE}/${path}`, {
      timeout: TIMEOUT_MS,
    });
    if (!isValid(data)) {
      throw new Error("unexpected payload shape");
    }
    writeCache(path, data);
    return data;
  } catch (err) {
    const cached = readCache(path);
    if (cached && isValid(cached)) {
      console.warn(`[data] ${path} unreachable, using cached copy: ${err.message}`);
      return cached;
    }
    console.error(`[data] ${path} unavailable and nothing cached: ${err.message}`);
    return null;
  }
}

export default fetchData;
