import gaoyi from "./gaoyi_schedules.json";
import gaoer from "./gaoer_schedules.json";
import gaosan from "./gaosan_schedules.json";

// Chinese numerals used as row labels in the schedule table, one per period.
const PERIOD_NAMES = ["一", "二", "三", "四", "五", "六", "七", "八"];

const WEEKDAY_KEYS = {
  monday: "Monday",
  tuesday: "Tuesday",
  wednesday: "Wednesday",
  thursday: "Thursday",
  friday: "Friday",
};

// Period time ranges (identical across all three grades' source files).
const PERIODS = gaoyi.periods.map((p, index) => ({
  period: p.period,
  name: PERIOD_NAMES[index],
  time: p.time,
}));

// Semester bounds come from the 實施日期 printed on the source timetables.
// Week 1 of the semester is 單週; parity alternates weekly from there.
const SEMESTER_START = gaoyi.semester_start ?? null;

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

const ACADEMIC_YEAR = gaoyi.academic_year ?? "";

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

const SCHEDULE_DATA = {};
for (const gradeFile of [gaoyi, gaoer, gaosan]) {
  for (const classEntry of gradeFile.classes) {
    SCHEDULE_DATA[classEntry.id] = {
      schedule: buildScheduleRows(classEntry.schedule),
    };
  }
}

const CLASS_OPTIONS = Object.keys(SCHEDULE_DATA)
  .map(Number)
  .sort((a, b) => a - b);

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
  SCHEDULE_DATA,
  CLASS_OPTIONS,
  PERIODS,
  getCurrentPeriodName,
  getWeekParity,
  getWeekNumber,
  ACADEMIC_YEAR,
};
