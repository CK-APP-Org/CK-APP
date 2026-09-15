<template>
  <div>
    <q-page class="flex column relative-position">
      <!-- Loading overlay -->
      <div v-if="isLoading" class="loading-overlay flex flex-center">
        <q-spinner size="70px" color="primary" />
        <div class="q-mt-sm text-primary">讀取資料中...</div>
      </div>

      <div v-else-if="error" class="error-message q-pa-md">{{ error }}</div>

      <div v-else>
        <div class="map-controls-1 q-pa-md">
          <q-btn
            color="primary"
            label="畫面顯示列表"
            @click="showRestaurantList = true"
            class="q-mr-sm"
          />
          <q-checkbox
            v-model="hideClosedRestaurants"
            label="正在營業"
            class="q-mr-md"
          />
          <q-checkbox v-model="showOnlyFavorites" label="我的最愛" />
        </div>

        <div class="map-controls-2 q-pa-md">
          <q-btn color="primary" icon="info" @click="showLegend = true" />
          <q-btn
            color="primary"
            label="隨機選擇餐廳"
            outline
            @click="selectRandomRestaurant"
            class="q-ml-sm"
          />
        </div>

        <l-map
          ref="mapRef"
          style="height: 90vh; width: 100%"
          :zoom="16"
          :center="[25.031204, 121.515496]"
          :options="mapOptions"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          ></l-tile-layer>
          <l-marker :lat-lng="[25.03079, 121.51227]" :icon="ckIcon">
            <l-popup><div class="text-h6">建中</div></l-popup>
          </l-marker>
          <l-marker
            v-for="marker in markers"
            :key="marker.name"
            :lat-lng="marker.position"
            :icon="getMarkerIcon(marker)"
            @click="showSidebarAndDisplayIconType(marker)"
          >
            <l-popup :options="{ offset: new Point(0, -10) }">
              <div class="text-h6">{{ marker.name }}</div>
              <div class="today-hours">
                今日時間&nbsp;
                <template
                  v-for="(section, index) in marker.openingHours[
                    getCurrentDay()
                  ].split(',')"
                  :key="index"
                >
                  <span v-if="index === 0">{{ section.trim() }}</span>
                  <div v-else class="additional-hours-popup">
                    {{ section.trim() }}
                  </div>
                </template>
              </div>
            </l-popup>
          </l-marker>
        </l-map>

        <restaurant-sidebar v-model="sidebarOpen" :marker="selectedMarker" />

        <map-legend v-model="showLegend" />

        <restaurant-list
          v-model="showRestaurantList"
          :markers="markers"
          @show-detail="showSidebarFromList"
        />
      </div>
    </q-page>
  </div>
</template>

<script setup>
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { onMounted, computed, ref } from "vue";
import { Icon, Point } from "leaflet";
import L from "leaflet";
import { useQuasar } from "quasar";
import { useStore } from "vuex";
import { fetchData } from "../services/remoteData";
import MapLegend from "../components/food/MapLegend.vue";
import RestaurantSidebar from "../components/food/RestaurantSidebar.vue";
import RestaurantList from "../components/food/RestaurantList.vue";
import {
  getMarkerIcon,
  getIconType,
  isOpen as isRestaurantOpen,
  getCurrentDay,
} from "../composables/useRestaurantHours";

const $q = useQuasar();
const store = useStore();

const mapRef = ref(null);
const hideClosedRestaurants = ref(false);
const showLegend = ref(false);
const mapOptions = {
  zoomControl: false,
};

const favoriteRestaurants = computed(
  () => store.getters.getFavoriteRestaurants
);

const showOnlyFavorites = ref(false);
const showRestaurantList = ref(false);

const ckIcon = new Icon({
  iconUrl:
    "https://raw.githubusercontent.com/CK-APP-Org/Data/main/FoodPage/CK_Logo.png",
  iconSize: [41, 41],
  iconAnchor: [20, 20],
});

const isFavorite = (restaurant) => {
  return favoriteRestaurants.value.some((r) => r.name === restaurant.name);
};

const restaurantData = ref([]);
const isLoading = ref(true);
const error = ref(null);

const fetchRestaurantData = async () => {
  try {
    isLoading.value = true;
    error.value = null;

    restaurantData.value =
      (await fetchData("restaurantData.json", Array.isArray)) ?? [];
  } finally {
    isLoading.value = false;
  }
};

const markers = computed(() =>
  restaurantData.value
    .map((marker) => ({
      ...marker,
      isOpen: isRestaurantOpen(marker.openingHours),
    }))
    .filter(
      (marker) =>
        (!hideClosedRestaurants.value || marker.isOpen) &&
        (!showOnlyFavorites.value || isFavorite(marker))
    )
);

const sidebarOpen = ref(false);
const selectedMarker = ref(null);

const showSidebar = (marker) => {
  selectedMarker.value = marker;
  sidebarOpen.value = true;
};

const showSidebarAndDisplayIconType = (marker) => {
  const iconType = getIconType(getMarkerIcon(marker));

  // Optional: Use Quasar notify to show more details
  /*
  $q.notify({
    message: `Marker: ${marker.name}, Icon Type: ${iconType}`,
    color: "info",
    position: "bottom",
  });
  */

  showSidebar(marker);
};

const showSidebarFromList = (restaurant) => {
  showSidebar(restaurant);
  showRestaurantList.value = false;

  // Find the marker for the selected restaurant
  const marker = markers.value.find((m) => m.name === restaurant.name);

  if (marker && mapRef.value) {
    // Pan the map to the marker's position
    mapRef.value.leafletObject.panTo(marker.position);

    // Open the popup
    mapRef.value.leafletObject.eachLayer((layer) => {
      if (
        layer instanceof L.Marker &&
        layer.getLatLng().equals(marker.position)
      ) {
        layer.openPopup();
      }
    });
  }
};

const selectRandomRestaurant = () => {
  const openRestaurants = markers.value.filter((marker) => marker.isOpen);
  if (openRestaurants.length === 0) {
    $q.notify({
      color: "negative",
      message: "目前沒有營業中的餐廳",
      icon: "warning",
    });
    return;
  }

  const randomRestaurant =
    openRestaurants[Math.floor(Math.random() * openRestaurants.length)];
  showSidebar(randomRestaurant);

  if (mapRef.value) {
    mapRef.value.leafletObject.setView(randomRestaurant.position, 18);
    mapRef.value.leafletObject.eachLayer((layer) => {
      if (
        layer instanceof L.Marker &&
        layer.getLatLng().equals(randomRestaurant.position)
      ) {
        layer.openPopup();
      }
    });
  }

  $q.notify({
    color: "positive",
    message: `已為您選擇: ${randomRestaurant.name}`,
    icon: "restaurant",
  });
};

onMounted(() => {
  fetchRestaurantData();
  // delete Icon.Default.prototype._getIconUrl;
  // Icon.Default.mergeOptions({
  //   iconRetinaUrl: new URL("https://imgur.com/2bk3D5t.png", import.meta.url)
  //     .href,
  //   iconUrl: new URL("https://imgur.com/0ZsD2ff.png", import.meta.url).href,
  //   shadowUrl: new URL("https://imgur.com/qKgJSmB.png", import.meta.url).href,
  // });
});
</script>

<style scoped>
.today-hours {
  font-weight: bold;
  color: #2196f3;
}

.additional-hours-popup {
  margin-left: 4.5em;
}

.ml-4 {
  margin-left: 3.5em;
  padding-left: 0.5em;
}

.map-controls-1 {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2000;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  padding: 10px;
}

.map-controls-2 {
  position: absolute;
  bottom: 140px;
  right: 4px;
  z-index: 2000;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  padding: 10px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
  flex-direction: column;
}

.error-message {
  color: #ff5252;
  font-weight: bold;
}
</style>
