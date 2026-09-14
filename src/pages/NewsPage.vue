<template>
  <q-page class="q-pa-md">
    <!-- Pinned News Table -->
    <q-table
      v-if="pinnedNews.length > 0"
      :rows="pinnedNews"
      :columns="columns"
      row-key="title"
      class="my-custom-table-2 q-mb-md"
      :wrap-cells="true"
      :dense="$q.screen.lt.md"
      :rows-per-page-options="[0]"
      hide-pagination
    >
      <template v-slot:top>
        <div class="text-h6 div-header">已釘選</div>
      </template>

      <template v-slot:header="props">
        <q-tr :props="props">
          <q-th
            v-for="col in props.cols"
            :key="col.name"
            :props="props"
            class="custom-header"
          >
            {{ col.label }}
          </q-th>
        </q-tr>
      </template>

      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-btn
              size="sm"
              color="negative"
              round
              dense
              icon="push_pin"
              @click="unpinRow(props.row)"
            />
          </q-td>
          <q-td
            v-for="col in props.cols.slice(1)"
            :key="col.name"
            :props="props"
          >
            <a
              v-if="col.name === 'title'"
              :href="props.row.link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ col.value }}
            </a>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <!-- Original News Table -->
    <q-table
      :rows="news"
      :columns="columns"
      row-key="title"
      class="my-custom-table-2"
      :wrap-cells="true"
      :dense="$q.screen.lt.md"
      :rows-per-page-options="[20, 50, 100, 0]"
      rows-per-page-label="每頁最大顯示數量:"
      v-model:pagination="pagination"
      :loading="isLoading"
    >
      <template v-slot:top>
        <div class="row items-center full-width q-px-sm">
          <div class="col-3 text-left">
            <div>
              <q-btn
                color="primary"
                icon="refresh"
                @click="refreshNews"
                dense
                class="q-mb-xs"
              />
            </div>
          </div>
          <div class="col-6 text-center">
            <div class="text-h6">未讀訊息</div>
            <div class="text-caption">
              <q-icon name="update" class="q-mr-xs" />
              <span>{{ formatTimeAgo(lastFetchTime) }}</span>
            </div>
          </div>
          <div class="col-3 text-right">
            <q-btn
              color="negative"
              icon="delete"
              @click="showDeleteDialog = true"
              dense
              class="q-mr-sm"
            />
            <q-btn
              color="green"
              icon="restore"
              @click="showRecoverDialog = true"
              dense
            />
          </div>
        </div>
      </template>

      <template v-slot:header="props">
        <q-tr :props="props">
          <q-th
            v-for="col in props.cols"
            :key="col.name"
            :props="props"
            class="custom-header"
          >
            {{ col.label }}
          </q-th>
        </q-tr>
      </template>

      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-btn
              size="sm"
              color="primary"
              round
              dense
              icon="push_pin"
              @click="pinRow(props.row)"
            />
          </q-td>
          <q-td
            v-for="col in props.cols.slice(1)"
            :key="col.name"
            :props="props"
          >
            <a
              v-if="col.name === 'title'"
              :href="props.row.link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ col.value }}
            </a>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>

      <template v-slot:loading>
        <q-inner-loading showing color="primary" />
      </template>

      <template v-slot:no-data>
        <div class="full-width row flex-center q-gutter-sm text-body1">
          沒有更新的公告
        </div>
      </template>
    </q-table>

    <!--對話框(已讀所有訊息)-->
    <q-dialog v-model="showDeleteDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">確認已讀所有訊息?</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="取消" @click="showDeleteDialog = false" />
          <q-btn flat label="確認" @click="deleteAllNews" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showRecoverDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">確認恢復所有已讀訊息?</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="取消" @click="showRecoverDialog = false" />
          <q-btn flat label="確認" @click="revertDeletedNews" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { upstreamUrl, SCHOOL_NEWS_URLS } from "../services/endpoints";
import { format, register } from "timeago.js";
import zh_TW from "timeago.js/lib/lang/zh_TW";
import store from "../store/index";
import newsService from "../services/newsService";

export default {
  name: "NewsPage",
  setup() {
    const pinnedNews = computed(() => store.getters.getPinnedNews);
    const isLoading = ref(false);
    const news = computed(() => {
      const fetchedNews = store.getters.getFetchedNews;
      const lastClearedTime = store.getters.getLastClearedTime;
      const pinnedTitles = pinnedNews.value.map((item) => item.title);
      return fetchedNews.filter(
        (item) =>
          (!lastClearedTime ||
            new Date(item.pubDate) > new Date(lastClearedTime)) &&
          !pinnedTitles.includes(item.title)
      );
    });
    const lastFetchTime = computed(() => store.getters.getLastFetchTime);
    const showDeleteDialog = ref(false);
    const showRecoverDialog = ref(false);
    const columns = [
      {
        name: "pin",
        required: true,
        label: "",
        align: "left",
        field: () => null,
      },
      {
        name: "title",
        required: true,
        label: "公告標題",
        align: "left",
        field: (row) => row.title,
        format: (val) => `${val}`,
        sortable: false,
        classes: "title-cell",
      },
      {
        name: "pubDate",
        required: true,
        label: "時間",
        align: "right",
        field: (row) => row.pubDate,
        format: (val) => formatTimeAgo(val),
        sortable: true,
      },
    ];

    const pinRow = (row) => {
      const index = news.value.findIndex((item) => item.title === row.title);
      if (index !== -1) {
        const pinnedItem = news.value.splice(index, 1)[0];
        store.dispatch("pinNews", pinnedItem);
      }
    };

    const unpinRow = (row) => {
      store.dispatch("unpinNews", row.title);
      if (!news.value.some((item) => item.title === row.title)) {
        news.value.push(row);
      }
    };

    const pagination = ref({
      sortBy: "pubDate",
      descending: true,
      page: 1,
      rowsPerPage: 20,
    });

    const fetchNews = async () => {
      isLoading.value = true;

      try {
        const lastClearedTime = store.getters.getLastClearedTime;
        const promises = SCHOOL_NEWS_URLS.map((url) =>
          axios.get(upstreamUrl(url))
        );

        const responses = await Promise.all(promises);
        let allNews = [];

        responses.forEach((response) => {
          const parser = new DOMParser();
          const xml = parser.parseFromString(response.data, "text/xml");
          const items = Array.from(xml.querySelectorAll("item"));
          const newsData = items
            .map((item) => ({
              title: item.querySelector("title").textContent,
              pubDate: new Date(item.querySelector("pubDate").textContent),
              link: item.querySelector("link").textContent,
            }))
            .filter(
              (item) =>
                !lastClearedTime ||
                new Date(item.pubDate) > new Date(lastClearedTime)
            );
          allNews = allNews.concat(newsData);
        });

        allNews.sort((a, b) => b.pubDate - a.pubDate);

        news.value = allNews;
      } catch (error) {
        console.error("Error fetching news:", error);
        isLoading.value = false;
      } finally {
        isLoading.value = false;
      }
    };

    const formatTimeAgo = (date) => {
      return format(date, "zh_TW");
    };

    const deleteAllNews = () => {
      // Clear all unpinned news
      news.value = [];
      // Record the current time
      const currentTime = new Date();
      store.dispatch("setLastClearedTime", currentTime);

      showDeleteDialog.value = false;
    };

    const revertDeletedNews = () => {
      const oldDate = new Date("2010-01-01").toISOString();
      store.dispatch("setLastClearedTime", oldDate);
      showRecoverDialog.value = false;
      fetchNews(); // Refetch news to show the restored items
    };

    const refreshNews = async (manualRefresh = false) => {
      if (manualRefresh) {
        isLoading.value = true;
      }
      await newsService.fetchNews();
      lastFetchTime.value = new Date();
      isLoading.value = false;
    };

    onMounted(() => {
      register("zh_TW", zh_TW);
      if (news.value.length === 0) {
        isLoading.value = true;
        refreshNews().then(() => {
          isLoading.value = false;
          lastFetchTime.value = new Date(); // Update lastFetchTime here
        });
      } else {
        // If news is already loaded, set lastFetchTime to current time
        lastFetchTime.value = new Date();
      }
    });

    return {
      news,
      columns,
      formatTimeAgo,
      pagination,
      isLoading,
      pinnedNews,
      pinRow,
      unpinRow,
      showDeleteDialog,
      deleteAllNews,
      revertDeletedNews,
      showRecoverDialog,
      refreshNews,
      lastFetchTime,
    };
  },
};
</script>

<style scoped>
.q-pa-md {
  padding: 11px;
}
.div-header {
  display: flex;
  justify-content: center;
  width: 100%;
  text-align: center;
}
.my-custom-table-2 .custom-header {
  font-weight: bold;
  font-size: 1.1em;
  color: #1976d2;
  background-color: #e3f2fd;
  text-transform: none;
}
.my-custom-table-2 .title-cell {
  max-width: 230px;
  white-space: normal;
  word-wrap: break-word;
}
/* Make the table responsive */
.my-custom-table-2 {
  width: 100%;
  max-width: 100%;
}
/* Ensure consistent padding in header and data cells */
.my-custom-table-2 .q-td,
.my-custom-table-2 .q-th {
  padding: 12px 8px;
}
</style>
