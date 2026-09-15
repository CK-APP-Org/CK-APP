// Class schedules come from the Data repo, not from the bundle -- see
// src/services/remoteData.js for why. loadSchedules() is awaited by the
// appData boot file, so everything below is populated before the first
// component mounts and consumers can keep reading these as plain values.
//
// These are `let` on purpose: ES module bindings are live, so reassigning them
// here updates every importer. Do not convert them to `const`.

import { fetchData } from "../../services/remoteData";

const GRADE_FILES = [
  "schedules/gaoyi_schedules.json",
  "schedules/gaoer_schedules.json",
  "schedules/gaosan_schedules.json",
];

// Chinese numerals used as row labels in the schedule table, one per period.
const PERIOD_NAMES = ["一", "二", "三", "四", "五", "六", "七", "八"];

const WEEKDAY_KEYS = {
  monday: "Monday",
  tuesday: "Tuesday",
  wednesday: "Wednesday",
  thursday: "Thursday",
  friday: "Friday",
};

const isGradeFile = (d) => d && Array.isArray(d.classes) && Array.isArray(d.periods);

// Period time ranges (identical across all three grades' source files).
let PERIODS = [];

// Semester bounds come from the 實施日期 printed on the source timetables.
// Week 1 of the semester is 單週; parity alternates weekly from there.
let SEMESTER_START = null;

// Monday-based start of the week containing `date`.
function startOfWeek(date) {
  const d = new Date(date);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  d.setHours(0, 0, 0, 0);
  return d;
}

// Weeks elapsed since the semester began (0-based); null outside a known semester.
function weeksSinceStart(date) {
  if (!SEMESTER_START) return null;
  return Math.round(
    (startOfWeek(date) - startOfWeek(new Date(`${SEMESTER_START}T00:00:00`))) /
      (7 * 24 * 60 * 60 * 1000)
  );
}

// Returns "odd" (單週) or "even" (雙週) for the week containing `date`.
function getWeekParity(date = new Date()) {
  const weeks = weeksSinceStart(date);
  if (weeks === null) return "odd";
  return (((weeks % 2) + 2) % 2) === 0 ? "odd" : "even";
}

// 1-based teaching week, e.g. 第3週. Null before the semester starts.
function getWeekNumber(date = new Date()) {
  const weeks = weeksSinceStart(date);
  if (weeks === null || weeks < 0) return null;
  return weeks + 1;
}

let ACADEMIC_YEAR = "";

function buildScheduleRows(rawSchedule) {
  return PERIOD_NAMES.map((name, periodIndex) => {
    const row = { name };
    for (const [rawDay, colName] of Object.entries(WEEKDAY_KEYS)) {
      const raw = rawSchedule[rawDay]?.[periodIndex] ?? "";
      // A cell is either a plain subject string, or a pair that alternates
      // week to week, e.g. 物理 on 雙週 / 化學 on 單週.
      row[colName] =
        raw && typeof raw === "object"
          ? { subject: raw.odd, alternating: { odd: raw.odd, even: raw.even } }
          : { subject: raw };
    }
    return row;
  });
}

let SCHEDULE_DATA = {};
let CLASS_OPTIONS = [];

/**
 * Fetch the three grade files and populate this module.
 *
 * Awaited by the appData boot file so that it completes before any component
 * mounts. Returns false if the data could not be obtained at all, which only
 * happens on a first run with no connectivity.
 */
async function loadSchedules() {
  const files = await Promise.all(
    GRADE_FILES.map((path) => fetchData(path, isGradeFile))
  );
  const grades = files.filter(Boolean);
  if (!grades.length) return false;

  const data = {};
  for (const gradeFile of grades) {
    for (const classEntry of gradeFile.classes) {
      data[classEntry.id] = {
        schedule: buildScheduleRows(classEntry.schedule),
      };
    }
  }
  SCHEDULE_DATA = data;
  CLASS_OPTIONS = Object.keys(data)
    .map(Number)
    .sort((a, b) => a - b);

  // All three files carry the same period times and semester bounds.
  const [first] = grades;
  PERIODS = first.periods.map((p, index) => ({
    period: p.period,
    name: PERIOD_NAMES[index],
    time: p.time,
  }));
  SEMESTER_START = first.semester_start ?? null;
  ACADEMIC_YEAR = first.academic_year ?? "";

  return grades.length === GRADE_FILES.length;
}

// Parses "HH:MM-HH:MM" into comparable minute-of-day numbers.
function parseTimeRange(time) {
  const [start, end] = time.split("-");
  const toMinutes = (hhmm) => {
    const [h, m] = hhmm.split(":").map(Number);
    return h * 60 + m;
  };
  return { start: toMinutes(start), end: toMinutes(end) };
}

// Returns the Chinese-numeral name of the period covering `date`, or null
// if `date` falls outside all class periods (before/after school, lunch, etc).
function getCurrentPeriodName(date = new Date()) {
  const nowMinutes = date.getHours() * 60 + date.getMinutes();
  for (const period of PERIODS) {
    const { start, end } = parseTimeRange(period.time);
    if (nowMinutes >= start && nowMinutes <= end) {
      return period.name;
    }
  }
  return null;
}

export {
  loadSchedules,
  SCHEDULE_DATA,
  CLASS_OPTIONS,
  PERIODS,
  getCurrentPeriodName,
  getWeekParity,
  getWeekNumber,
  ACADEMIC_YEAR,
};
