import axios from "axios";
import store from "../store/index";
import { upstreamUrl, SCHOOL_NEWS_URLS } from "./endpoints";

const FETCH_INTERVAL = 2 * 60 * 1000; // 2 minutes

export default {
  startBackgroundFetch() {
    this.fetchNews();
    setInterval(() => this.fetchNews(), FETCH_INTERVAL);
  },

  async fetchNews() {

    try {
      const promises = SCHOOL_NEWS_URLS.map((url) =>
        axios.get(upstreamUrl(url))
      );

      const responses = await Promise.all(promises);
      let allNews = [];

      responses.forEach((response) => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(response.data, "text/xml");
        const items = Array.from(xml.querySelectorAll("item"));
        const newsData = items.map((item) => ({
          title: item.querySelector("title").textContent,
          pubDate: new Date(item.querySelector("pubDate").textContent),
          link: item.querySelector("link").textContent,
        }));
        allNews = allNews.concat(newsData);
      });

      allNews.sort((a, b) => b.pubDate - a.pubDate);

      store.dispatch("setFetchedNews", allNews);
      store.dispatch("setLastFetchTime", new Date());
    } catch (error) {
      console.error("Error fetching news:", error);
    }
  },
};
