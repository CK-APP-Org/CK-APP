<template>
  <!-- Youbike Section -->
  <h3 class="text-h5 q-mb-md" style="font-weight: bold">
    <q-icon name="directions_bike" size="sm" class="q-mr-sm" />
    YouBike 站點
  </h3>
  <div class="row q-col-gutter-sm">
    <div v-for="(station, key) in stations" :key="key" class="col-6">
      <q-card class="station-card">
        <q-card-section class="q-pr-none q-pl-md">
          <div class="row justify-between items-center">
            <div class="header">
              {{
                (
                  stationsNickname[station.name] || station.name.substr(11)
                ).slice(0, 7)
              }}
            </div>
            <q-btn flat dense round color="primary" icon="more_vert">
              <q-menu>
                <q-list style="min-width: 100px">
                  <q-item
                    dense
                    clickable
                    v-close-popup
                    @click="openEditNicknameDialog(station.name)"
                    style="height: 40px"
                  >
                    <q-item-section>修改暱稱</q-item-section>
                  </q-item>
                  <q-item
                    dense
                    clickable
                    v-close-popup
                    @click="openDeleteStationDialog(key)"
                    style="height: 40px"
                  >
                    <q-item-section>刪除此站</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
          </div>

          <!-- Loading indicator -->
          <div
            v-if="isStationLoading(station.name)"
            class="flex flex-center"
            style="height: 33px"
          >
            <q-spinner color="primary" size="2.5em" />
          </div>

          <!-- Station information (always show when not initial loading) -->
          <template v-else>
            <div class="row q-mt-xs items-center">
              <div class="col-6">
                <q-icon name="pedal_bike" size="xs" color="primary" />
                <q-chip
                  dense
                  :color="getChipColor(station.available_rent_bikes)"
                  text-color="white"
                  class="q-ml-xs"
                >
                  <div class="text">{{ station.available_rent_bikes }}</div>
                </q-chip>
              </div>
              <div class="col-6">
                <q-icon name="local_parking" size="xs" color="primary" />
                <q-chip
                  dense
                  :color="getChipColor(station.available_return_bikes)"
                  text-color="white"
                  class="q-ml-xs"
                >
                  <div class="text">{{ station.available_return_bikes }}</div>
                </q-chip>
              </div>
            </div>
          </template>
        </q-card-section>
      </q-card>
    </div>
  </div>

  <!--對話框(新增站點)-->
  <q-dialog v-model="showAddYoubikeStationDialog" full-width>
    <q-card>
      <q-card-section>
        <div class="text-h6">選擇新增之站點</div>
      </q-card-section>
      <q-card-section>
        <q-select
          v-model="selectedCity"
          :options="cityOptions"
          label="選擇縣市"
          @update:model-value="onCityChange"
        />
        <q-select
          v-model="selectedDistrict"
          :options="districtOptions"
          label="選擇行政區"
          :disable="!selectedCity"
          @update:model-value="onDistrictChange"
        />
        <q-select
          v-model="selectedStation"
          :options="stationOptions"
          label="選擇站點"
          :disable="!selectedDistrict"
        />
        <div class="separator-or">或</div>
        <div class="row justify-center q-mt-md">
          <q-btn
            icon="search"
            color="primary"
            label="尋找最近的九個站點"
            @click="findNearestStationsFromDialog"
          />
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="取消"
          @click="showAddYoubikeStationDialog = false"
        />
        <q-btn flat label="確認" @click="addYoubikeStation" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <!--對話框(修改暱稱)-->
  <q-dialog v-model="showEditNicknameDialog">
    <q-card>
      <q-card-section>
        <div class="text-h6">編輯站點暱稱</div>
      </q-card-section>
      <q-card-section>
        <q-input
          v-model="newNickname"
          label="輸入新暱稱 (至多顯示七個字)"
          autofocus
          @keyup.enter="updateNickname"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="取消" @click="showEditNicknameDialog = false" />
        <q-btn flat label="確認" @click="updateNickname" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <!--對話框(刪除站點)-->
  <q-dialog v-model="showDeleteStationDialog">
    <q-card>
      <q-card-section>
        <div class="text-h6">確認刪除此站點?</div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="取消" @click="showDeleteStationDialog = false" />
        <q-btn
          flat
          label="確認"
          @click="deleteStation(selectedStationForDelete)"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <!--對話框(最近站點)-->
  <q-dialog v-model="showNearestStationsDialog" full-width>
    <q-card style="width: 300px">
      <q-card-section>
        <div class="text-h6">最近的站點</div>
      </q-card-section>
      <q-card-section>
        <div
          v-for="(station, index) in nearestStations"
          :key="index"
          class="q-mb-sm"
        >
          <div class="row items-center justify-between">
            <div>
              {{ index + 1 }}. {{ station.sna.substr(11) }} -
              {{ (station.distance * 1000).toFixed(0) }} m
            </div>
            <q-btn
              color="primary"
              label="Add"
              size="sm"
              @click="addNearestStation(station)"
              :disable="isStationInList(station.sna)"
            />
          </div>
        </div>
      </q-card-section>
      <q-card-section>
        <l-map
          v-if="userPosition"
          style="height: 270px; width: 100%"
          :zoom="mapZoom"
          :center="mapCenter"
          :options="mapOptions"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          ></l-tile-layer>
          <l-circle
            :lat-lng="userPosition"
            :radius="circleRadius"
            color="red"
            dashArray="10, 10"
            :opacity="0.45"
            :fill="true"
            fillColor="red"
            :fillOpacity="0.05"
          ></l-circle>
          <l-marker :lat-lng="userPosition" :icon="userIcon">
            <l-popup>您的位置</l-popup>
          </l-marker>
          <l-marker
            v-for="station in nearestStations"
            :key="station.sna"
            :lat-lng="[parseFloat(station.lat), parseFloat(station.lng)]"
            :icon="youbikeIcon"
          >
            <l-popup>
              <div class="text-bold">
                {{ station.sna.substr(11) }}
              </div>
              <div
                v-if="
                  districtOptionsTPC.some(
                    (option) => option.label === station.sarea
                  )
                "
              >
                可借車輛: {{ station.available_rent_bikes }}
              </div>
              <div v-else>可借車輛: {{ station.sbi }}</div>

              <div
                v-if="
                  districtOptionsTPC.some(
                    (option) => option.label === station.sarea
                  )
                "
              >
                可還車輛: {{ station.available_return_bikes }}
              </div>
              <div v-else>可還車輛: {{ station.bemp }}</div>
            </l-popup>
          </l-marker>
        </l-map>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="關閉" @click="showNearestStationsDialog = false" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="showLocationPickerDialog" full-width>
    <q-card style="width: 300px">
      <q-card-section>
        <div class="text-h6">選擇您的位置</div>
      </q-card-section>
      <q-card-section>
        <l-map
          style="height: 300px; width: 100%"
          :zoom="13"
          :center="mapCenter"
          @click="handleLocationSelected"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          ></l-tile-layer>
        </l-map>
        <div v-if="isLoadingNearestStations" class="text-center q-mt-md">
          <q-spinner color="primary" size="3em" />
          <div class="text-subtitle1 q-mt-sm">正在搜尋站點...</div>
        </div>
      </q-card-section>
      <q-card-section>
        <div v-if="!isLoadingNearestStations" class="text-center">
          點擊地圖上的位置來選擇您的位置
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";
import {
  upstreamUrl,
  YOUBIKE_TPC_URL,
  YOUBIKE_NTC_URLS,
} from "../../services/endpoints";
import { useStore } from "vuex";
import { useQuasar } from "quasar";
import {
  Station,
  districtOptionsTPC,
  districtOptionsNTC,
  calculateDistance,
} from "../../composables/useYoubike";

import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LCircle,
} from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { Icon } from "leaflet";

const $q = useQuasar();
const store = useStore();

const StationList = computed(() => store.getters.getStationList);
const stations = ref({});
const stationsNickname = ref({});
const isInitialLoad = ref(true);
const isLoading = ref(true);
const tpcLoading = ref({});
const ntcLoading = ref({});
const showAddYoubikeStationDialog = ref(false);
const showEditNicknameDialog = ref(false);
const showDeleteStationDialog = ref(false);
const selectedStationForEdit = ref(null);
const newNickname = ref("");
const selectedStationForDelete = ref(null);
const selectedCity = ref(null);
const selectedDistrict = ref(null);
const selectedStation = ref(null);
const cityOptions = [
  { label: "臺北市", value: "臺北市" },
  { label: "新北市", value: "新北市" },
];
const stationOptions = ref([]);
const showNearestStationsDialog = ref(false);
const nearestStations = ref(null);
const userPosition = ref(null);
const isLoadingNearestStations = ref(false);
const mapCenter = ref([25.031204, 121.515966]);
const mapZoom = ref(15);
const mapOptions = {
  zoomControl: false,
};
const youbikeIcon = new Icon({
  iconUrl: "../../food/marker-icon-open.png",
  iconSize: [25, 41],
  iconAnchor: [12, 30],
});
const userIcon = new Icon({
  iconUrl: "../../food/marker-icon-closed.png",
  iconSize: [25, 41],
  iconAnchor: [12, 30],
});
const circleRadius = ref(0);
const showLocationPickerDialog = ref(false);

const districtOptions = computed(() => {
  if (selectedCity.value) {
    return selectedCity.value.value === "臺北市"
      ? districtOptionsTPC
      : districtOptionsNTC;
  }
  return [];
});

const fetchYoubikeData = async () => {
  const stationList = StationList.value;

  if (!stationList) {
    console.error("StationList is undefined");
    isLoading.value = false;
    return;
  }

  // Initialize stations and loading states if needed
  if (Object.keys(stations.value).length === 0) {
    stations.value = Object.fromEntries(
      Object.keys(stationList).map((name) => [name, new Station(name)])
    );
    stationsNickname.value = Object.fromEntries(
      Object.entries(stationList).map(([key, value]) => [
        key,
        value.nickname,
      ])
    );

    // Initialize loading states for each station based on their city
    Object.entries(stationList).forEach(([name, data]) => {
      if (data.city === "臺北市") {
        tpcLoading.value[name] = true;
      } else if (data.city === "新北市") {
        ntcLoading.value[name] = true;
      }
    });
  }

  // Function to update station data
  const updateStationData = (stationKey, stationData, isTPCData = true) => {
    if (stationData) {
      stations.value[stationKey].available_rent_bikes = isTPCData
        ? stationData.available_rent_bikes
        : stationData.sbi;
      stations.value[stationKey].available_return_bikes = isTPCData
        ? stationData.available_return_bikes
        : stationData.bemp;
      stations.value[stationKey].infoTime = stationData.mday;
    }
  };

  try {
    // Fetch TPC data
    const tpcDataPromise = axios.get(
      upstreamUrl(YOUBIKE_TPC_URL)
    );

    // Fetch NTC data in parallel
    const ntcDataPromises = [
      axios.get(
        upstreamUrl(YOUBIKE_NTC_URLS[0])
      ),
      axios.get(
        upstreamUrl(YOUBIKE_NTC_URLS[1])
      ),
    ];

    // Handle TPC data
    const tpcResponse = await tpcDataPromise;
    const dataTPC = tpcResponse.data;

    // Update TPC stations
    for (const key in stations.value) {
      if (stationList[key].city === "臺北市") {
        const stationData = dataTPC.find(
          (station) => station.sna === stations.value[key].name
        );
        updateStationData(key, stationData, true);
        tpcLoading.value[key] = false;
      }
    }

    // Handle NTC data
    Promise.all(ntcDataPromises)
      .then(([response1, response2]) => {
        const dataNTC = [...response1.data, ...response2.data];

        // Update NTC stations
        for (const key in stations.value) {
          if (stationList[key].city === "新北市") {
            const stationData = dataNTC.find(
              (station) => station.sna === stations.value[key].name
            );
            updateStationData(key, stationData, false);
            ntcLoading.value[key] = false;
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching NTC data:", error);
        // Mark all NTC stations as not loading on error
        Object.keys(ntcLoading.value).forEach((key) => {
          ntcLoading.value[key] = false;
        });
      });
  } catch (error) {
    console.error("Error fetching TPC data:", error);
    // Mark all stations as not loading on error
    Object.keys(tpcLoading.value).forEach((key) => {
      tpcLoading.value[key] = false;
    });
    Object.keys(ntcLoading.value).forEach((key) => {
      ntcLoading.value[key] = false;
    });
  }
};

// Compute whether a station is loading based on its city
const isStationLoading = (stationName) => {
  const stationData = StationList.value[stationName];
  if (!stationData) {
    return false; // Return false if station data is not yet in StationList
  }
  if (stationData.city === "臺北市") {
    return tpcLoading.value[stationName];
  } else if (stationData.city === "新北市") {
    return ntcLoading.value[stationName];
  }
  return false;
};

const addYoubikeStation = async () => {
  if (selectedStation.value) {
    const stationName = selectedStation.value["value"];
    const city = selectedCity.value["value"];

    // Initialize the station in local state
    stations.value[stationName] = new Station(stationName);

    // Initialize loading state based on city
    if (city === "臺北市") {
      tpcLoading.value[stationName] = true;
    } else if (city === "新北市") {
      ntcLoading.value[stationName] = true;
    }

    // Update store first to ensure StationList has the data
    await store.dispatch("addStation", {
      stationName: stationName,
      stationData: {
        nickname: selectedStation.value.label,
        city: city,
      },
    });

    // Then fetch the data
    showAddYoubikeStationDialog.value = false;

    try {
      if (city === "臺北市") {
        const response = await axios.get(
          upstreamUrl(YOUBIKE_TPC_URL)
        );
        const data = response.data;
        const stationData = data.find((s) => s.sna === stationName);

        if (stationData) {
          stations.value[stationName].available_rent_bikes =
            stationData.available_rent_bikes;
          stations.value[stationName].available_return_bikes =
            stationData.available_return_bikes;
          stations.value[stationName].infoTime = stationData.mday;
        }
        tpcLoading.value[stationName] = false;
      } else if (city === "新北市") {
        const [response1, response2] = await Promise.all([
          axios.get(
            upstreamUrl(YOUBIKE_NTC_URLS[0])
          ),
          axios.get(
            upstreamUrl(YOUBIKE_NTC_URLS[1])
          ),
        ]);

        const data = [...response1.data, ...response2.data];
        const stationData = data.find((s) => s.sna === stationName);

        if (stationData) {
          stations.value[stationName].available_rent_bikes =
            stationData.sbi;
          stations.value[stationName].available_return_bikes =
            stationData.bemp;
          stations.value[stationName].infoTime = stationData.mday;
        }
        ntcLoading.value[stationName] = false;
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      if (city === "臺北市") {
        tpcLoading.value[stationName] = false;
      } else if (city === "新北市") {
        ntcLoading.value[stationName] = false;
      }
    }

    // Reset the form
    selectedCity.value = null;
    selectedDistrict.value = null;
    selectedStation.value = null;
  }
};

const onCityChange = () => {
  selectedDistrict.value = null;
  selectedStation.value = null;
  stationOptions.value = [];
};

const onDistrictChange = async () => {
  selectedStation.value = null;
  stationOptions.value = [];

  if (selectedDistrict.value) {
    let apiUrl;
    if (selectedCity.value["value"] === "臺北市") {
      apiUrl = upstreamUrl(YOUBIKE_TPC_URL);
    } else if (selectedCity.value["value"] === "新北市") {
      apiUrl = upstreamUrl(YOUBIKE_NTC_URLS[0]);
    }
    try {
      let response = await axios.get(apiUrl);
      let data = response.data;

      //Because NTC API has two pages
      if (selectedCity.value["value"] === "新北市") {
        const response2 = await axios.get(
          upstreamUrl(YOUBIKE_NTC_URLS[1])
        );
        data = [...data, ...response2.data];
      }

      // Filter stations by selected district
      const filteredStations = data.filter(
        (station) => station.sarea === selectedDistrict.value["value"]
      );
      // Map the filtered stations to station options
      stationOptions.value = filteredStations.map((station) => ({
        label: station.sna.substr(11),
        value: station.sna,
      }));
    } catch (error) {
      console.error("Error fetching data:", error);
      stationOptions.value = [];
    }
  } else {
    stationOptions.value = [];
  }
};

const openEditNicknameDialog = (stationName) => {
  selectedStationForEdit.value = stationName;
  newNickname.value = stationsNickname.value[stationName] || "";
  showEditNicknameDialog.value = true;
};

const updateNickname = () => {
  if (selectedStationForEdit.value && newNickname.value) {
    // Update local state
    stationsNickname.value = {
      ...stationsNickname.value,
      [selectedStationForEdit.value]: newNickname.value,
    };

    // Update store
    store.dispatch("updateStationNickname", {
      stationName: selectedStationForEdit.value,
      newNickname: newNickname.value,
    });
  }
  showEditNicknameDialog.value = false;
};

const openDeleteStationDialog = (stationName) => {
  selectedStationForDelete.value = stationName;
  showDeleteStationDialog.value = true;
};

const deleteStation = (key) => {
  if (stations.value[key]) {
    const stationName = stations.value[key].name;

    // Remove from local component state
    delete stationsNickname.value[stationName];

    // Use Vue's reactivity system to trigger an update
    stations.value = { ...stations.value };
    delete stations.value[key];

    // Update store
    store.dispatch("deleteStation", stationName);
  } else {
    // If the station is not in the local state, it might be directly in the store
    store.dispatch("deleteStation", key);
  }
  showDeleteStationDialog.value = false;
};

const getChipColor = (value) => {
  if (value === 0) return "red-9";
  if (value >= 1 && value <= 3) return "orange-8";
  return "green";
};

const findNearestStations = () => {
  showLocationPickerDialog.value = true;
};

const handleLocationSelected = async ({ latlng }) => {
  const userLat = latlng.lat;
  const userLng = latlng.lng;

  userPosition.value = [userLat, userLng];
  mapCenter.value = [userLat, userLng];

  isLoadingNearestStations.value = true;

  try {
    const allStations = await fetchAllStationsData();

    const stationsWithDistances = allStations.map((station) => ({
      ...station,
      distance: calculateDistance(
        userLat,
        userLng,
        station.lat,
        station.lng
      ),
    }));

    stationsWithDistances.sort((a, b) => a.distance - b.distance);

    nearestStations.value = stationsWithDistances.slice(0, 9);

    circleRadius.value = nearestStations.value[8].distance * 1100;

    showLocationPickerDialog.value = false;
    showNearestStationsDialog.value = true;
  } catch (error) {
    console.error("Error finding nearest stations:", error);
    $q.notify({
      message: "無法取得附近站點，請稍後再試",
      color: "negative",
      position: "bottom",
    });
  } finally {
    isLoadingNearestStations.value = false;
  }
};

const fetchAllStationsData = async () => {
  try {
    const tpcResponse = await axios.get(
      upstreamUrl(YOUBIKE_TPC_URL)
    );

    const tpcData = tpcResponse.data.map((station) => ({
      ...station,
      lat: station.latitude,
      lng: station.longitude,
      city: "臺北市",
    }));

    const ntcResponse1 = await axios.get(
      upstreamUrl(YOUBIKE_NTC_URLS[0])
    );

    const ntcResponse2 = await axios.get(
      upstreamUrl(YOUBIKE_NTC_URLS[1])
    );

    const ntcData = [...ntcResponse1.data, ...ntcResponse2.data].map(
      (station) => ({
        ...station,
        lat: parseFloat(station.lat),
        lng: parseFloat(station.lng),
        city: "新北市",
      })
    );

    return [...tpcData, ...ntcData];
  } catch (error) {
    console.error("Error fetching all stations data:", error);
    throw error;
  }
};

const addNearestStation = (station) => {
  const newStationName = station.sna;
  const newStationData = {
    nickname: station.sna.substr(11),
    city: station.city,
  };

  // Update local state
  stations.value = {
    ...stations.value,
    [newStationName]: new Station(newStationName),
  };

  // Update local stationsNickname
  stationsNickname.value = {
    ...stationsNickname.value,
    [newStationName]: newStationData.nickname,
  };

  // Update store
  store.dispatch("addStation", {
    stationName: newStationName,
    stationData: newStationData,
  });

  $q.notify({
    message: "站點已新增至您的清單",
    color: "positive",
    position: "bottom",
    timeout: 2000,
  });

  fetchYoubikeData();
};

const isStationInList = (stationName) => {
  return Object.keys(stations.value).includes(stationName);
};

const findNearestStationsFromDialog = () => {
  showAddYoubikeStationDialog.value = false;
  findNearestStations();
};

let intervalId = null;

onMounted(() => {
  fetchYoubikeData();
  intervalId = setInterval(() => {
    fetchYoubikeData();
  }, 10000);
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});

function openAddStationDialog() {
  showAddYoubikeStationDialog.value = true;
}

defineExpose({ openAddStationDialog });
</script>

<style scoped>
.header {
  font-weight: Bold;
  color: #03328d;
  font-size: 19px;
  margin-bottom: 2px;
}
.text {
  font-size: 15px;
  font-weight: bold;
}

.custom-card-margin {
  margin: 10px 10px;
  background-color: rgb(239, 246, 254);
}

.update-time {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
}
.update-time .q-icon {
  margin-right: 4px;
}

.separator-or {
  display: flex;
  align-items: center;
  text-align: center;
  margin-top: 32px;
}
.separator-or::before,
.separator-or::after {
  content: "";
  flex: 1;
  border-bottom: 3px double #e0e0e0;
}
.separator-or::before {
  margin-right: 0.5em;
}
.separator-or::after {
  margin-left: 0.5em;
}

.search-btn {
  margin-top: 10px;
  margin-bottom: 20px;
  height: 36px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.station-card {
  height: 100%;
  background-color: #f8f8f8;
}

.find-nearest-btn {
  margin-top: 16px;
  margin-bottom: 16px;
}
</style>
