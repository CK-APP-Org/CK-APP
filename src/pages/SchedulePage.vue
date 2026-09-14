<template>
  <div v-if="loading" class="loading-spinner">
    <q-spinner size="3em" color="primary" />
  </div>
  <div v-else class="q-pa-md">
    <div class="custom-banner q-mb-md">
      <q-icon name="info" color="info" size="sm" class="q-mr-sm" />
      點擊課表格子可自訂科目、顏色和備註
    </div>
    <q-table
      flat
      bordered
      :title="userClass + ' 課表'"
      :rows="scheduleData"
      :columns="columns"
      row-key="name"
      :visible-columns="visibleColumns"
      class="my-custom-table"
      separator="cell"
      :rows-per-page-options="[0]"
      hide-pagination
      hide-bottom
    >
      <template v-slot:top>
        <div class="sch-head">
          <div class="row items-center">
            <q-btn
              flat
              dense
              round
              icon="edit"
              color="primary"
              class="q-mr-sm"
              @click="confirmClassChangeDialog = true"
            />
            <div class="sch-title">{{ userClass }} 課表 &thinsp;</div>
            <q-btn
              round
              size="sm"
              color="primary"
              outline
              icon="refresh"
              @click="confirmRegenerate"
            />
            <q-dialog v-model="confirmClassChangeDialog">
              <q-card style="min-width: 300px; max-width: 400px">
                <q-card-section class="row items-center q-pb-none">
                  <div class="text-h6 text-bold">設定班級</div>
                  <q-space />
                  <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-card-section class="q-pt-md">
                  <q-select
                    filled
                    v-model="selectedClass"
                    :options="classOptions"
                    @update:model-value="confirmClassChange"
                    label="選擇班級"
                    use-input
                    input-debounce="0"
                    behavior="menu"
                  >
                    <template v-slot:prepend>
                      <q-icon name="school" color="primary" />
                    </template>
                  </q-select>
                </q-card-section>

                <q-card-section class="text-caption text-grey-8">
                  更改班級將重置當前的課表。
                </q-card-section>

                <q-card-actions align="right">
                  <q-btn
                    flat
                    label="取消"
                    color="primary"
                    @click="confirmClassChangeDialog = false"
                  />
                  <q-btn
                    flat
                    label="確認"
                    color="primary"
                    @click="updateUserClass"
                    :disable="!selectedClass"
                  />
                </q-card-actions>
              </q-card>
            </q-dialog>
          </div>
          <div class="sch-context">{{ semesterLine }}</div>
          <div class="row q-gutter-sm">
            <q-btn
              v-for="day in days"
              :key="day"
              :label="getDayLabel(day)"
              :color="visibleColumns.includes(day) ? 'primary' : 'grey-7'"
              @click="changeVisibleColumn(day)"
              dense
              outline
              no-caps
            />
          </div>
        </div>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td
          :props="props"
          class="rail"
          :class="{
            'rail--afternoon': isAfternoon(props.row.name),
            'rail--lunch': props.row.name === '五',
            'rail--now': isCurrentPeriod(props.row.name),
          }"
        >
          <div v-if="bandLabel(props.row.name)" class="rail-band">
            {{ bandLabel(props.row.name) }}
          </div>
          <div class="rail-main">
            <span class="rail-num">{{ props.row.name }}</span>
            <span class="rail-time">{{ periodStart(props.row.name) }}</span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell="props">
        <q-td
          :props="props"
          :class="[
            { 'split-cell': props.col.name !== 'name' },
            { 'lunch-break': props.row.name === '五' },
            { 'current-class': isCurrentClass(props.row, props.col.name) },
          ]"
        >
          <template v-if="props.col.name !== 'name'">
            <div
              class="cell-content"
              :style="{
                backgroundColor: getLabelValue(
                  getCellColor(props.row, props.col.name)
                ),
              }"
            >
              <div class="subject-slot">
                <div
                  v-if="getCellAlternating(props.row, props.col.name)"
                  class="alt-stack"
                >
                  <div
                    v-for="week in ['odd', 'even']"
                    :key="week"
                    class="alt-row"
                    :class="{ 'alt-row--active': weekParity === week }"
                  >
                    <span class="alt-tag">{{
                      week === "odd" ? "單" : "雙"
                    }}</span>
                    <span class="alt-subject">{{
                      getCellAlternating(props.row, props.col.name)[week]
                    }}</span>
                  </div>
                </div>
                <template v-else>
                  {{ getCellSubject(props.row, props.col.name) }}
                </template>
              </div>
              <div class="note-slot">
                {{ getCellNote(props.row, props.col.name) }}
              </div>
            </div>
            <q-popup-edit v-model="props.row[props.col.name]" v-slot="scope">
              <div class="text-h6 q-mb-md">自訂課表</div>
              <q-input
                v-model="scope.value.subject"
                label="科目"
                dense
                class="q-mb-sm"
              />
              <q-input
                v-if="scope.value.subject === '自訂'"
                v-model="scope.value.customSubject"
                label="自訂科目名稱"
                dense
                class="q-mb-sm"
              />
              <q-input
                v-model="scope.value.note"
                label="備註"
                dense
                class="q-mb-sm"
              />
              <q-select
                :options="colorOptions"
                v-model="scope.value.color"
                label="顏色"
                dense
                options-dense
              >
                <template v-slot:option="{ itemProps, opt }">
                  <q-item v-bind="itemProps">
                    <q-item-section side>
                      <q-chip
                        :style="{ backgroundColor: opt.value }"
                        square
                        dense
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ opt.label }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <div class="row justify-end q-mt-md">
                <q-btn
                  label="儲存"
                  color="primary"
                  @click="saveCell(props.row, props.col.name, scope.value)"
                  v-close-popup
                />
              </div>
            </q-popup-edit>
          </template>
          <template v-else>
            {{ props.row[props.col.name] }}
          </template>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="regenerateConfirm" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm"
            >重新載入將會清除所有您對課表的修改。確定要繼續嗎？</span
          >
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn
            flat
            label="確定"
            color="primary"
            @click="regenerateSchedule"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { onMounted, ref, computed } from "vue";
import { useQuasar } from "quasar";
import store from "../store/index";
import {
  CLASS_OPTIONS,
  PERIODS,
  getCurrentPeriodName,
  getWeekParity,
  getWeekNumber,
  ACADEMIC_YEAR,
} from "../data/schedules";

const classOptions = CLASS_OPTIONS;

const columns = [
  {
    name: "name",
    required: true,
    label: "節數",
    align: "left",
    field: (row) => row.name,
    classes: "smaller-column",
  },
  { name: "Monday", align: "center", label: "星期一", field: "Monday" },
  { name: "Tuesday", align: "center", label: "星期二", field: "Tuesday" },
  { name: "Wednesday", align: "center", label: "星期三", field: "Wednesday" },
  { name: "Thursday", align: "center", label: "星期四", field: "Thursday" },
  { name: "Friday", align: "center", label: "星期五", field: "Friday" },
];

const colorOptions = [
  { label: "Default", value: "#f4f4f1" },
  { label: "Red", value: "#FFCCCB" },
  { label: "Orange", value: "#f5c884" },
  { label: "Yellow", value: "#FFFFE0" },
  { label: "Green", value: "#90EE90" },
  { label: "Blue", value: "#ADD8E6" },
  { label: "Purple", value: "#e299ff" },
  { label: "Pink", value: "#ffa1e4" },
];

export default {
  setup() {
    const $q = useQuasar();

    const confirmClassChangeDialog = ref(false);
    const scheduleData = computed(() => store.getters.getScheduleData);
    const userClass = computed(() => store.getters.getUserClass);
    const selectedClass = ref(userClass.value);
    const loading = ref(true);

    const regenerateConfirm = ref(false);
    const confirmRegenerate = () => {
      regenerateConfirm.value = true;
    };

    const regenerateSchedule = async () => {
      try {
        await store.dispatch("loadSchedule");
        $q.notify({
          message: "已重新匯入課表",
          color: "positive",
          position: "bottom",
          timeout: 2000,
        });
      } catch (error) {
        console.error("Error regenerating schedule:", error);
        $q.notify({
          message: "重新匯入課表時發生錯誤",
          color: "negative",
          position: "bottom",
          timeout: 2000,
        });
      }
    };

    const visibleColumns = ref([
      "name",
      [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ][new Date().getDay()],
    ]);
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

    const changeVisibleColumn = (columnName) => {
      visibleColumns.value = ["name", columnName];
    };

    onMounted(async () => {
      loading.value = false;
    });

    const PERIOD_START = PERIODS.reduce((acc, p) => {
      acc[p.name] = p.time.split("-")[0];
      return acc;
    }, {});
    const periodStart = (name) => PERIOD_START[name] ?? "";
    // 上午 runs 第一節-第四節, 下午 第五節-第八節, as on the printed timetable.
    const AFTERNOON = ["五", "六", "七", "八"];
    const isAfternoon = (name) => AFTERNOON.includes(name);
    const bandLabel = (name) =>
      name === "一" ? "上午" : name === "五" ? "下午" : "";

    const currentPeriod = ref(getCurrentPeriodName());
    const isCurrentPeriod = (name) => currentPeriod.value === name;

    // Which half of the 單/雙 week cycle we are in right now.
    const weekParity = ref(getWeekParity());

    // e.g. "115學年度第1學期 · 第3週 單週" -- which week matters now that
    // some slots alternate between 單週 and 雙週.
    const semesterLine = computed(() => {
      const week = getWeekNumber();
      const parity = weekParity.value === "odd" ? "單週" : "雙週";
      const parts = [ACADEMIC_YEAR, week ? `第${week}週 ${parity}` : parity];
      return parts.filter(Boolean).join("　");
    });

    // Returns {odd, even} for an alternating slot, or null. Returns null once
    // the user has overridden the subject, so their edit is not ignored.
    const getCellAlternating = (row, colName) => {
      if (colName === "name") return null;
      const cell = row[colName];
      if (!cell || !cell.alternating) return null;
      const { odd, even } = cell.alternating;
      if (cell.subject && cell.subject !== odd && cell.subject !== even) {
        return null;
      }
      return cell.alternating;
    };

    const getCellSubject = (row, colName) => {
      if (colName === "name") return row[colName];
      const cell = row[colName];
      if (!cell) return "";
      // Alternating-week slots show whichever subject this week runs.
      if (cell.alternating) {
        return cell.alternating[getWeekParity()] || cell.subject || "";
      }
      return cell.subject || "";
    };
    const getCellColor = (row, colName) => {
      if (colName === "name") return "Default";
      return getFormattedColor(row[colName]?.color);
    };
    const getFormattedColor = (color) => {
      if (color && typeof color === "object" && color.label) {
        return color.label;
      }
      return color || "Default";
    };
    const getCellNote = (row, colName) => {
      if (colName === "name") return "";
      const cell = row[colName];
      if (!cell) return "";
      // Alternating slots render both weeks inline, so no note is needed here.
      return cell.note || "";
    };
    const getLabelValue = (label) => {
      const option = colorOptions.find((opt) => opt.label === label);
      return option ? option.value : "#f4f4f1"; // Default color if not found
    };

    const saveCell = async (row, colName, newValue) => {
      const rowIndex = scheduleData.value.indexOf(row);
      await store.dispatch("updateSchedule", { rowIndex, colName, newValue });
    };

    const confirmClassChange = (newClass) => {
      selectedClass.value = newClass;
      confirmClassChangeDialog.value = true;
    };

    const updateUserClass = async () => {
      await store.dispatch("setUserClass", selectedClass.value);
      await store.dispatch("loadSchedule");
      confirmClassChangeDialog.value = false;
      $q.notify({
        message: `已成功更改班級為 ${selectedClass.value}`,
        color: "positive",
        position: "bottom",
        timeout: 2000,
      });
    };

    const getDayLabel = (day) => {
      const labels = {
        Monday: "星期一",
        Tuesday: "星期二",
        Wednesday: "星期三",
        Thursday: "星期四",
        Friday: "星期五",
      };
      return labels[day] || day;
    };

    const isCurrentClass = (row, colName) => {
      const now = new Date();
      const currentDay = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ][now.getDay()];

      const currentPeriod = getCurrentPeriodName(now);

      return colName === currentDay && row.name === currentPeriod;
    };

    return {
      visibleColumns,
      columns,
      scheduleData,
      weekParity,
      getCellAlternating,
      semesterLine,
      periodStart,
      isAfternoon,
      bandLabel,
      isCurrentPeriod,
      userClass,
      colorOptions,
      getCellColor,
      getCellSubject,
      getCellNote,
      changeVisibleColumn,
      getDayLabel,
      getLabelValue,
      getFormattedColor,
      days,
      isCurrentClass,
      regenerateConfirm,
      confirmRegenerate,
      regenerateSchedule,
      selectedClass,
      confirmClassChange,
      classOptions,
      confirmClassChangeDialog,
      updateUserClass,
      saveCell,
      loading,
    };
  },
};
</script>

<style>
/* Structure follows the school's printed 課程表: a left spine carrying the
   period number and its start time, 上午/下午 bands, and one heavy rule at
   lunch. Rules separate periods; nothing is boxed for decoration. */
.my-custom-table {
  --sch-navy: #12308e;
  --sch-ink: #1d2028;
  --sch-quiet: #767b86;
  --sch-rule: #e0e2e8;
  --sch-rail: #f5f6f9;

  background-color: #fff;
  border: 1px solid var(--sch-rule);
  border-radius: 10px;
  overflow: hidden;
  font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei",
    -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.my-custom-table .q-table__top {
  display: block;
  padding: 16px 18px 12px;
  background-color: #fff;
  border-bottom: 1px solid var(--sch-rule);
}

.sch-title {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  color: var(--sch-ink);
}

.sch-head {
  display: block;
}

.sch-context {
  margin-top: 3px;
  font-size: 0.78rem;
  color: var(--sch-quiet);
  font-variant-numeric: tabular-nums;
}

/* Day switcher sits under the title, scrollable on narrow screens. */
.my-custom-table .q-table__top .row.q-gutter-sm {
  justify-content: flex-start;
  margin-top: 12px;
  flex-wrap: nowrap;
  overflow-x: auto;
}

.my-custom-table .q-table thead tr th {
  padding: 9px 12px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--sch-quiet);
  background-color: var(--sch-rail);
  border: none;
  border-bottom: 1px solid var(--sch-rule);
}

.my-custom-table .q-table tbody td {
  padding: 0;
  border: none;
  border-bottom: 1px solid var(--sch-rule);
  font-size: 1rem;
  color: var(--sch-ink);
}

.my-custom-table .q-table tbody tr:last-child td {
  border-bottom: none;
}

/* ---- period rail ---- */
.my-custom-table .q-table tbody td.rail {
  width: 1%;
  white-space: nowrap;
  padding: 8px 10px;
  background-color: var(--sch-rail);
  border-right: 1px solid var(--sch-rule);
  vertical-align: middle;
}

.rail-band {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--sch-navy);
  opacity: 0.75;
  margin-bottom: 3px;
}

.rail-main {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.rail-num {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--sch-ink);
}

.rail-time {
  font-size: 0.74rem;
  font-variant-numeric: tabular-nums;
  color: var(--sch-quiet);
}

/* Lunch: the one heavy rule, as on the paper timetable. */
.my-custom-table .q-table tbody td.rail--lunch,
.my-custom-table .q-table tbody td.lunch-break {
  border-top: 2px solid #c3c7d0;
}

/* Now: one accent, one job. */
.my-custom-table .q-table tbody td.rail--now {
  box-shadow: inset 3px 0 0 var(--sch-navy);
}

.my-custom-table .q-table tbody td.rail--now .rail-num,
.my-custom-table .q-table tbody td.rail--now .rail-time {
  color: var(--sch-navy);
}

/* ---- subject cells ---- */
.split-cell {
  padding: 0 !important;
}

.cell-content {
  display: flex;
  align-items: stretch;
  min-height: 46px;
  transition: background-color 0.2s ease;
}

.subject-slot {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 10px;
  font-weight: 600;
  /* Long names like 本土語文/臺灣手語 wrap instead of being clipped. */
  white-space: normal;
  overflow-wrap: anywhere;
  line-height: 1.3;
  text-align: center;
}

.note-slot {
  flex: 0 0 30%;
  min-width: 0;
  display: flex;
  align-items: center;
  padding: 8px 10px;
  font-size: 0.7rem;
  color: var(--sch-quiet);
  border-left: 1px dashed var(--sch-rule);
  overflow-wrap: anywhere;
}

.cell-content:hover {
  filter: brightness(0.97);
}

/* Slots that alternate week to week show both options, current one emphasised. */
.alt-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  width: 100%;
}

.alt-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  line-height: 1.25;
  color: var(--sch-quiet);
}

.alt-row--active {
  font-size: 1rem;
  font-weight: 700;
  color: var(--sch-ink);
}

.alt-tag {
  flex: none;
  border: 1px solid currentColor;
  border-radius: 3px;
  padding: 0 3px;
  font-size: 0.66rem;
  line-height: 1.5;
  opacity: 0.65;
}

.alt-row--active .alt-tag {
  color: var(--sch-navy);
  opacity: 1;
}

.alt-subject {
  min-width: 0;
  overflow-wrap: anywhere;
}

/* The current period's subject cell: quiet tint, the rail carries the accent. */
.current-class .cell-content {
  box-shadow: inset 0 0 0 2px rgba(18, 48, 142, 0.18);
}

.q-item__label.text-italic {
  font-style: italic;
  color: #666;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.custom-banner {
  background-color: #eef1f8;
  color: #3a4a7c;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
}

/* Phone is the primary target (the app also ships via Capacitor); widen up. */
@media (min-width: 600px) {
  .my-custom-table .q-table tbody td.rail {
    padding: 10px 14px;
  }
  .cell-content {
    min-height: 52px;
  }
  .subject-slot,
  .note-slot {
    padding: 9px 12px;
  }
  .note-slot {
    flex: 0 0 26%;
    font-size: 0.74rem;
  }
  .sch-title {
    font-size: 1.45rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cell-content {
    transition: none;
  }
}
</style>
