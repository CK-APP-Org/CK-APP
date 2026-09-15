// School 行事曆, fetched from the Data repo -- see src/services/remoteData.js.
// Generated there from the term's PDF by tools/convert_calendar_pdf.py.
//
// The stored JSON keeps plain ISO dates, faithful to the PDF. CalendarView
// compares events against `new Date(year, month, day)`, which is local
// midnight, so the dates are widened here into local-time instants: a bare
// "2026-08-31" would parse as UTC midnight and land on the wrong day anywhere
// east of Greenwich, putting every event a day late in Taipei.

import { fetchData } from "../../services/remoteData";

const TERM_FILE = "calendar/115-1.json";

// CalendarView treats events in this category as read-only.
export const SCHOOL_EVENT_CATEGORY = { name: "學校事務", color: "#00897B" };

const startOfDay = (iso) => `${iso}T00:00:00`;
const endOfDay = (iso) => `${iso}T23:59:59`;

const isCalendar = (d) => d && Array.isArray(d.events);

const toCalendarEvent = (event, index) => ({
  id: `school-${index}`,
  title: event.title,
  startDate: startOfDay(event.startDate),
  endDate: endOfDay(event.endDate),
  department: event.department,
  // 暫 in the source: the school has not fixed this one yet.
  tentative: event.tentative,
  // Dated only to a 上旬/中旬/下旬, so the span is indicative, not exact.
  approximate: event.approximate,
  category: SCHOOL_EVENT_CATEGORY,
});

// Live binding, populated by loadSchoolEvents() from the appData boot file.
export let SCHOOL_EVENTS = [];
export let CALENDAR_TERM = "";

export async function loadSchoolEvents() {
  const data = await fetchData(TERM_FILE, isCalendar);
  if (!data) return [];
  CALENDAR_TERM = data.term ?? "";
  SCHOOL_EVENTS = data.events.map(toCalendarEvent);
  return SCHOOL_EVENTS;
}
