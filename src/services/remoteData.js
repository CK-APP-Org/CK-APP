// Data that changes during the school year -- restaurant listings, the term
// 行事曆 -- lives in the companion Data repo rather than only in the bundle, so
// it can be corrected without shipping a new app release and waiting on review.
//
// Every fetch keeps the bundled copy as a fallback, so the app still works
// offline, on a first run with no connection, and if the remote file is missing
// or malformed.

import axios from "axios";

const DATA_BASE = "https://raw.githubusercontent.com/CKApp-Dev/Data/main";

const TIMEOUT_MS = 8000;

/**
 * Fetch a JSON file from the Data repo, falling back to the bundled copy.
 *
 * @param {string} path     path within the Data repo, e.g. "restaurantData.json"
 * @param {*} fallback      bundled value to use if the fetch fails
 * @param {(data:*) => boolean} isValid  shape check; a 404 can arrive as an
 *   HTML error page rather than an error status, so the payload is checked
 *   before it is trusted over the bundled copy.
 */
export async function fetchData(path, fallback, isValid = () => true) {
  try {
    const { data } = await axios.get(`${DATA_BASE}/${path}`, {
      timeout: TIMEOUT_MS,
    });
    if (!isValid(data)) {
      throw new Error("unexpected payload shape");
    }
    return data;
  } catch (err) {
    console.warn(`[data] using bundled ${path}: ${err.message}`);
    return fallback;
  }
}

export default fetchData;
