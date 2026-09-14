<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6 col-md-4">
        <!-- Settings Cards -->
        <q-card class="q-mb-md">
          <q-card-section>
            <div class="text-h6 q-mb-md">設定</div>
            <q-list>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="school" />
                </q-item-section>
                <q-item-section>
                  <q-select
                    filled
                    @update:model-value="confirmClassChange"
                    :options="classOptions"
                    v-model="selectedClass"
                    label="選擇班級(用於課表資料匯入)"
                    style="padding: 8px 0"
                  />
                </q-item-section>
              </q-item>
              <q-item clickable v-ripple @click="showHomeSettings = true">
                <q-item-section avatar>
                  <q-icon name="home" />
                </q-item-section>
                <q-item-section>首頁顯示項目設定</q-item-section>
                <q-item-section side>
                  <q-icon name="chevron_right" />
                </q-item-section>
              </q-item>
              <q-item clickable v-ripple @click="showToolbarSettings = true">
                <q-item-section avatar>
                  <q-icon name="build" />
                </q-item-section>
                <q-item-section>自訂工具列</q-item-section>
                <q-item-section side>
                  <q-icon name="chevron_right" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <home-widget-settings v-model="showHomeSettings" />
    <toolbar-customiser v-model="showToolbarSettings" />

    <q-dialog v-model="confirmDialog">
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">確定清除所有本地資料?注意，此動作無法復原</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn
            flat
            label="確定"
            color="negative"
            @click="clearAllData"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="confirmClassChangeDialog">
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm" style="font-size: 1.5rem"
            >確定更改班級為 <strong>{{ selectedClass }}</strong
            >?</span
          >
          <span class="q-ml-sm"
            >(請注意，本動作會導致所有過去自訂的顏色和標籤全部消失並無法復原)</span
          >
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" @click="cancelClassChange" />
          <q-btn flat label="確定" color="primary" @click="updateUserClass" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, ref } from "vue";
import { useStore } from "vuex";
import { useQuasar } from "quasar";
import { useRouter } from "vue-router";
import { CLASS_OPTIONS } from "../data/schedules";
import HomeWidgetSettings from "../components/settings/HomeWidgetSettings.vue";
import ToolbarCustomiser from "../components/settings/ToolbarCustomiser.vue";

const classOptions = CLASS_OPTIONS;

const themeColors = [
  { label: "藍色", value: "#1976D2" },
  { label: "紅色", value: "#C10015" },
  { label: "綠色", value: "#4CAF50" },
  { label: "紫色", value: "#9C27B0" },
  { label: "橙色", value: "#FF9800" },
];

const $q = useQuasar();
const store = useStore();
const confirmDialog = ref(false);
const confirmClassChangeDialog = ref(false);
const userClass = computed(() => store.getters.getUserClass);
const selectedClass = ref(userClass.value);

const router = useRouter();

const showHomeSettings = ref(false);
const showToolbarSettings = ref(false);

// Theme color
const themeColor = ref("#1976D2"); // Default to blue

// Watch for theme color changes and apply them
/*
watch(
  themeColor,
  (newColor) => {
    $q.dark.set(false); // Ensure light mode is active
    document.body.style.setProperty("--q-primary", newColor);
  },
  { immediate: true }
);
*/

const confirmClear = () => {
  confirmDialog.value = true;
};

const clearAllData = () => {
  store.dispatch("clearALL");
  store.dispatch("loadSchedule");
  $q.notify({
    message: `已刪除所有資料`,
    color: "positive",
    position: "bottom",
    timeout: 2000,
  });
  router.push("/");
};

const confirmClassChange = (newClass) => {
  selectedClass.value = newClass;
  confirmClassChangeDialog.value = true;
};

const updateUserClass = () => {
  store.dispatch("setUserClass", selectedClass.value);
  store.dispatch("loadSchedule");
  confirmClassChangeDialog.value = false;

  $q.notify({
    message: `已成功更改班級為 ${selectedClass.value}`,
    color: "positive",
    position: "bottom",
    timeout: 2000,
  });
};

const cancelClassChange = () => {
  selectedClass.value = userClass.value;
  confirmClassChangeDialog.value = false;
};
</script>

<style scoped>
.custom-menu-item {
  padding: 8px 16px;
}
.custom-menu-item .q-item__section--side {
  padding-right: 0;
}
.custom-menu-item .q-item__section--avatar {
  min-width: 40px;
}
</style>
