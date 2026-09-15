import { boot } from "quasar/wrappers";

import { loadSchedules } from "../data/schedules";
import { loadSchoolEvents } from "../data/calendar";

// Pull the shared data sets before the first component mounts.
//
// The schedule module exposes its data as plain values that pages read during
// setup (`const classOptions = CLASS_OPTIONS`), so it has to be populated
// before any page renders -- otherwise the class picker and timetable would
// capture empty arrays and never recover. Boot files are awaited ahead of the
// root component, which is exactly that guarantee.
//
// Each loader already falls back to its cached copy and resolves to an empty
// result rather than throwing, so a failure here degrades the affected page
// instead of blocking startup.
export default boot(async () => {
  const [schedulesOk, events] = await Promise.all([
    loadSchedules(),
    loadSchoolEvents(),
  ]);

  if (!schedulesOk) {
    console.warn("[appData] class schedules are incomplete or unavailable");
  }
  if (!events.length) {
    console.warn("[appData] school calendar is unavailable");
  }
});
