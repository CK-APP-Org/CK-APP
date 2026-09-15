// School 行事曆, generated from the term's PDF by tools/convert_calendar_pdf.py.
//
// The JSON keeps plain ISO dates, faithful to the PDF. The calendar compares
// events against `new Date(year, month, day)`, which is local midnight, so the
// dates are widened here into local-time instants: a bare "2026-08-31" would
// parse as UTC midnight and land on the wrong day everywhere east of Greenwich,
// putting every event a day late in Taiwan.

import term1 from "./115-1.json";
import { fetchData } from "../../services/remoteData";

// CalendarView treats events in this category as read-only.
export const SCHOOL_EVENT_CATEGORY = { name: "學校事務", color: "#00897B" };

const startOfDay = (iso) => `${iso}T00:00:00`;
const endOfDay = (iso) => `${iso}T23:59:59`;

export const CALENDAR_TERM = term1.term;

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

// Bundled copy, available synchronously so the calendar renders immediately.
export const SCHOOL_EVENTS = term1.events.map(toCalendarEvent);

// The school reissues the 行事曆 during the year, so prefer the copy in the
// Data repo when it can be reached.
export async function loadSchoolEvents() {
  const data = await fetchData(
    "calendar/115-1.json",
    term1,
    (d) => d && Array.isArray(d.events)
  );
  return data.events.map(toCalendarEvent);
}

export default SCHOOL_EVENTS;
