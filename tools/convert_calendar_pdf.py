"""Convert the school 行事曆 PDF into the JSON the app's calendar reads.

The PDF is a week-per-row table:

    月份 | 週次 | 日 一 二 三 四 五 六 | 重  要  行  事 | 彈 性 學 習 / 團 體 活 動

Text is read with coordinates rather than as flowed text. The flowed form loses
the table structure: it inserts spaces where a cell wraps mid-word (幹 部訓練),
and it cannot tell which week a 彈性學習 entry belongs to, because that column
has no dates of its own. Coordinates give both back.

Two columns, parsed differently:

* 重要行事 -- every entry begins a line with its own date prefix (``8/24``,
  ``8/26-27``, ``12/31-1/8``), so entries are split on lines that start with a
  date and the rest are treated as wrapped continuations.
* 彈性學習 -- no dates, so entries are located by position. The column nests
  three levels, each vertically centred against the block it labels: week rows,
  then 第N節, then 高一/高二/高三. Each level is split at the midpoints between
  consecutive labels.

Usage:
    python tools/convert_calendar_pdf.py <calendar.pdf> -o src/data/calendar/115-1.json

Requires pypdf (pip install pypdf).
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

# --- term ------------------------------------------------------------------
# 115學年度第1學期 runs Aug 2026 -> Feb 2027, so a month implies its year.
FIRST_MONTH = 8
START_YEAR = 2026
# 日 column of the first week row in the PDF (暑9, 8/23), which anchors every
# later week: calendar weeks advance exactly 7 days.
FIRST_WEEK_SUNDAY = date(2026, 8, 23)

# --- column geometry, in PDF user units ------------------------------------
# Derived from the rendered table; see the module docstring.
X_EVENTS = 228.0   # 重要行事 text starts at x=231.5; 六 column ends by x=225
X_FLEX = 625.0     # 彈性學習 starts at the 第N節 label (x=627)
X_GRADE = 652.0    # 高一/高二/高三 labels (x=656)
X_ACTIVITY = 672.0  # activity text (x>=677)
Y_TOL = 2.0        # fragments within this many units share a line

# Legend from the PDF header.
DEPARTMENTS = {
    "★": "教務處",
    "◆": "學務處",
    "▲": "總務處",
    "■": "圖書館",
    "◎": "輔導室",
    "●": "人事室",
}
MARKERS = "".join(DEPARTMENTS)

# Staff-facing entries. A student has no use for 學生代辦費收取審議會議.
STAFF_PATTERNS = [
    "會議", "教研會", "審議", "委員會", "檢討", "查核", "檢修",
    "消毒", "清洗水塔", "研習", "工作小組", "相見歡",
    "期初學務", "期末學務", "安全檢查", "設備檢修",
]
# ...except these, which are aimed at students or families.
STUDENT_OVERRIDES = ["學校日", "說明會", "座談會", "家長代表大會", "親師", "畢業"]

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛"


def year_for(month):
    return START_YEAR if month >= FIRST_MONTH else START_YEAR + 1


def month_end(year, month):
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def make_date(month, day):
    return date(year_for(month), month, day)


# --- extraction -------------------------------------------------------------

def read_fragments(page):
    """Collect (x, y, text) for every text fragment on the page."""
    out = []

    def visit(text, cm, tm, font_dict, font_size):
        t = text.strip()
        if t:
            out.append((round(tm[4], 1), round(tm[5], 1), t))

    page.extract_text(visitor_text=visit)
    return out


def group_lines(frags):
    """Group fragments into lines keyed by y, each sorted left to right.

    Returns [(y, [(x, text), ...])] ordered top to bottom.
    """
    buckets = defaultdict(list)
    for x, y, t in frags:
        buckets[y].append((x, t))
    ys = sorted(buckets, reverse=True)

    merged, cur_y, cur = [], None, []
    for y in ys:
        if cur_y is not None and abs(cur_y - y) <= Y_TOL:
            cur += buckets[y]
        else:
            if cur:
                merged.append((cur_y, sorted(cur)))
            cur_y, cur = y, list(buckets[y])
    if cur:
        merged.append((cur_y, sorted(cur)))
    return merged


def join(cells, sep=""):
    """Join fragments of one cell.

    Prose cells use no separator, because the PDF splits fragments mid-word and
    any separator would show up inside the text. The date columns pass sep=" "
    so that adjacent day numbers stay distinct rather than fusing into one.
    """
    return sep.join(t for _x, t in cells)


def decircle(s):
    return re.sub(r"[%s]" % CIRCLED, lambda m: str(CIRCLED.index(m.group()) + 1), s)


def find_day_columns(lines):
    """x centre of each of the seven 日..六 day columns, from the header row."""
    for _y, cells in lines:
        labels = [(x, t) for x, t in cells if t in "日一二三四五六" and x < X_EVENTS]
        if len(labels) >= 7:
            # The row reads 星期 / 日 一 二 三 四 五 六, so 日 can appear twice.
            return [x for x, _t in labels[-7:]]
    return []


DAY_Y_TOL = 4.0  # 定期考 digits (①㉚) sit ~3.2 units below their row's baseline


def find_week_rows(frags, day_cols):
    """Week rows, read by bucketing fragments into the seven day columns.

    Clustered straight from the raw fragments rather than from the prose lines,
    for two reasons. Concatenating a row's text and re-splitting it cannot work,
    because the PDF emits "16" as separate "1" and "6" fragments, so digits have
    to be regrouped by the column they sit under. And the circled 定期考 days are
    typeset on a slightly lower baseline than the rest of their row, so the day
    grid needs a looser vertical tolerance than prose can tolerate.
    """
    if not day_cols:
        return []
    # The 月份 and 週次 labels sit to the left of the day grid. They must be
    # excluded, or a week number lands in the 日 column and corrupts it.
    first = day_cols[0] - 6
    grid = [(x, y, t) for x, y, t in frags if first <= x < X_EVENTS]

    clusters = []
    for x, y, t in sorted(grid, key=lambda f: -f[1]):
        if clusters and abs(clusters[-1][0] - y) <= DAY_Y_TOL:
            clusters[-1][1].append((x, t))
        else:
            clusters.append([y, [(x, t)]])
    clusters = [(y, cells) for y, cells in clusters]

    out = []
    for y, cells in clusters:
        buckets = ["" for _ in day_cols]
        for x, t in sorted(cells):
            gaps = [abs(x - cx) for cx in day_cols]
            buckets[gaps.index(min(gaps))] += t
        vals = [re.sub(r"\D", "", decircle(b)) for b in buckets]
        if not all(v.isdigit() for v in vals):
            continue
        days = [int(v) for v in vals]
        resets = sum(1 for a, b in zip(days, days[1:]) if b <= a)
        if resets <= 1 and all(1 <= d <= 31 for d in days):
            out.append((y, days))
    return out


def bands(labels, top, bottom):
    """Split [top, bottom] at midpoints between consecutive label positions.

    Each label in this table is vertically centred against the block it names,
    so a midpoint split is what recovers the block's true extent.
    """
    out = []
    for i, (y, payload) in enumerate(labels):
        hi = top if i == 0 else (labels[i - 1][0] + y) / 2
        lo = bottom if i == len(labels) - 1 else (y + labels[i + 1][0]) / 2
        out.append((hi, lo, payload))
    return out


# --- 重要行事 ---------------------------------------------------------------

DATE_TOKEN = re.compile(
    r"^("
    r"\d{1,2}/\d{1,2}-\d{1,2}/\d{1,2}"          # 12/31-1/8
    r"|\d{1,2}/\d{1,2}-\d{1,2}月底"              # 9/2-9月底
    r"|\d{1,2}/\d{1,2}-\d{1,2}"                  # 8/26-27
    r"|\d{1,2}/\d{1,2}"                          # 8/24
    r"|\d{1,2}月(?:上旬|中旬|下旬)-\d{1,2}月(?:上旬|中旬|下旬)"
    r"|\d{1,2}月(?:上旬|中旬|下旬)"
    r")"
)


def resolve_dates(token):
    """Map a date token to (start, end), or None."""
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})-(\d{1,2})/(\d{1,2})", token)
    if m:
        a, b, c, d = map(int, m.groups())
        return make_date(a, b), make_date(c, d)

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})-(\d{1,2})月底", token)
    if m:
        a, b, c = map(int, m.groups())
        return make_date(a, b), month_end(year_for(c), c)

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})-(\d{1,2})", token)
    if m:
        a, b, c = map(int, m.groups())
        return make_date(a, b), make_date(a, c)

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})", token)
    if m:
        a, b = map(int, m.groups())
        return make_date(a, b), make_date(a, b)

    m = re.fullmatch(r"(\d{1,2})月(上旬|中旬|下旬)-(\d{1,2})月(上旬|中旬|下旬)", token)
    if m:
        return _tenday(int(m.group(1)), m.group(2))[0], _tenday(int(m.group(3)), m.group(4))[1]

    m = re.fullmatch(r"(\d{1,2})月(上旬|中旬|下旬)", token)
    if m:
        return _tenday(int(m.group(1)), m.group(2))

    return None


def _tenday(month, part):
    y = year_for(month)
    if part == "上旬":
        return date(y, month, 1), date(y, month, 10)
    if part == "中旬":
        return date(y, month, 11), date(y, month, 20)
    return date(y, month, 21), month_end(y, month)


def is_staff_only(title):
    if any(k in title for k in STUDENT_OVERRIDES):
        return False
    return any(k in title for k in STAFF_PATTERNS)


def parse_events(lines):
    """Read the 重要行事 column into events, plus the 【...】 week banners."""
    groups, banners, unparsed = [], [], []
    current = None
    for y, cells in lines:
        text = join([(x, t) for x, t in cells if X_EVENTS <= x < X_FLEX]).strip()
        if not text:
            continue
        for banner in re.findall(r"【(.+?)】", text):
            banners.append((y, re.sub(r"^[%s]+" % MARKERS, "", banner)))
        text = re.sub(r"【.+?】", "", text).strip()
        if not text:
            continue

        m = DATE_TOKEN.match(text)
        if m:
            current = [m.group(1), text[m.end():]]
            groups.append(current)
        elif current:
            current[1] += text

    events = []
    for token, body in groups:
        span = resolve_dates(token)
        if not span:
            unparsed.append(token)
            continue
        start, end = span
        for title in split_entries(body):
            events.append({
                "title": title,
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "department": DEPARTMENTS.get(title[0]) if title[0] in MARKERS else None,
                "tentative": "(暫)" in title or title.endswith("暫"),
                "approximate": "旬" in token or "月底" in token,
            })
    for e in events:
        e["title"] = re.sub(r"^[%s]+" % MARKERS, "", e["title"]).strip()
    return [e for e in events if len(e["title"]) >= 2], banners, unparsed


def split_entries(body):
    """One date's run of text into separate entries, split on dept markers.

    Only markers at bracket depth zero start a new entry. A marker can also
    appear inside a parenthetical -- 第1次定期考(◆考後大掃除) -- where it
    qualifies the entry it sits in rather than beginning the next one.
    """
    body = body.strip()
    if not body:
        return []
    pieces, cur, depth = [], "", 0
    for ch in body:
        if ch in "(（":
            depth += 1
        elif ch in ")）":
            depth = max(0, depth - 1)
        if ch in MARKERS and depth == 0 and cur.strip():
            pieces.append(cur)
            cur = ""
        cur += ch
    if cur.strip():
        pieces.append(cur)
    return [p.strip() for p in pieces if p.strip()]


# --- 彈性學習 ---------------------------------------------------------------

PERIOD_RE = re.compile(r"第(\d)節")
GRADE_RE = re.compile(r"^(高[一二三])$")


def nearest(labels, y):
    """Index of the label closest to y."""
    return min(range(len(labels)), key=lambda i: abs(labels[i][0] - y))


def parse_flexible(lines, week_rows, week_start):
    """Read the 彈性學習 column, nesting week -> 第N節 -> 高X.

    Resolved by nearest label at every level, never by carving the page into
    bands. Two properties of this table defeat banding: each label is typeset
    centred against the block it names, so it sits *between* the lines it owns
    whenever an activity wraps; and table rows differ in height, so a boundary
    guessed at the midpoint between two week rows can land the wrong side of a
    line by a fraction of a unit.

    Chaining nearest-label instead -- activity to 高X, 高X to 第N節, 第N節 to
    week -- keeps every hop short and unambiguous, since the gap within a group
    is always far smaller than the gap between groups.
    """
    if not week_rows:
        return []

    # The legend and column headers sit above the table and would otherwise be
    # swept into the first week's activities.
    header_y = max(
        (y for y, cells in lines
         if "彈" in join(cells) and "團" in join(cells)),
        default=None,
    )

    periods, grades, activities = [], [], []
    for y, cells in lines:
        if header_y is not None and y >= header_y:
            continue
        label = join([(x, t) for x, t in cells if X_FLEX <= x < X_GRADE])
        m = PERIOD_RE.search(re.sub(r"\s", "", label))
        if m:
            periods.append((y, int(m.group(1))))
        grade = join([(x, t) for x, t in cells if X_GRADE <= x < X_ACTIVITY]).strip()
        if GRADE_RE.match(grade):
            grades.append((y, grade))
        text = join([(x, t) for x, t in cells if x >= X_ACTIVITY]).strip()
        if text:
            activities.append((y, text))

    if not periods or not grades:
        return []

    owners = [[] for _ in grades]
    for y, text in activities:
        owners[nearest(grades, y)].append((y, text))

    by_week = defaultdict(list)
    for gi, (gy, grade) in enumerate(grades):
        text = "".join(t for _y, t in sorted(owners[gi], key=lambda a: -a[0]))
        text = re.sub(r"^[%s]+" % MARKERS, "", text).strip()
        if not text:
            continue
        py, period = periods[nearest(periods, gy)]
        widx = nearest([(y, i) for i, (y, _d) in enumerate(week_rows)], py)
        by_week[widx].append({"period": period, "grade": grade, "activity": text})

    out = []
    for widx in sorted(by_week):
        entries = sorted(by_week[widx], key=lambda e: (e["period"], e["grade"]))
        sunday = week_start(widx)
        out.append({
            "weekStart": sunday.isoformat(),
            "weekEnd": (sunday + timedelta(days=6)).isoformat(),
            "mondayOfWeek": (sunday + timedelta(days=1)).isoformat(),
            "entries": entries,
        })
    return out


# --- driver -----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--include-staff", action="store_true",
                    help="keep staff-only entries instead of dropping them")
    ap.add_argument("--include-flexible", action="store_true",
                    help=("also emit the 彈性學習 column. OFF BY DEFAULT: that "
                          "column uses merged cells -- at 第5節 one activity is "
                          "bracketed by two grade labels -- and which grades a "
                          "merged cell covers cannot be recovered from text "
                          "coordinates alone. The output flips 社課 numbers "
                          "between 高一 and 高二, so it is not fit to show. "
                          "Resolving it needs the table's ruling lines."))
    args = ap.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("pypdf is required: pip install pypdf")

    reader = PdfReader(args.pdf)
    raw = [read_fragments(p) for p in reader.pages]
    pages = [group_lines(f) for f in raw]

    # Weeks run continuously across pages, 7 days apart.
    week_index_base, all_weeks = [], []
    for pi, lines in enumerate(pages):
        rows = find_week_rows(raw[pi], find_day_columns(lines))
        week_index_base.append(len(all_weeks))
        all_weeks += rows

    def week_start(global_idx):
        return FIRST_WEEK_SUNDAY + timedelta(days=7 * global_idx)

    # The day numbers printed in each row must match the computed chain.
    mismatches = [
        (i, days[0], week_start(i).isoformat())
        for i, (_y, days) in enumerate(all_weeks)
        if days[0] != week_start(i).day
    ]

    events, banners, unparsed, flexible = [], [], [], []
    for pi, lines in enumerate(pages):
        ev, bn, un = parse_events(lines)
        events += ev
        banners += bn
        unparsed += un
        base = week_index_base[pi]
        rows = find_week_rows(raw[pi], find_day_columns(lines))
        flexible += parse_flexible(lines, rows, lambda i, b=base: week_start(b + i))

    staff = [e for e in events if is_staff_only(e["title"])]
    kept = events if args.include_staff else [e for e in events if e not in staff]
    kept.sort(key=lambda e: (e["startDate"], e["title"]))

    payload = {
        "term": "115學年度第1學期",
        "source": args.pdf.split("/")[-1],
        "events": kept,
    }
    if args.include_flexible:
        payload["flexibleLearning"] = flexible
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"weeks      {len(all_weeks)}  ({week_start(0)} .. {week_start(len(all_weeks)-1)})")
    print(f"events     {len(events)} parsed, {len(kept)} kept, {len(staff)} staff-only dropped")
    print(f"flexible   {len(flexible)} weeks "
          f"({'emitted' if args.include_flexible else 'parsed but NOT emitted'})")
    print(f"banners    {len(banners)}")
    if mismatches:
        print(f"WARNING week-chain mismatches: {mismatches}")
    if unparsed:
        print(f"WARNING unparsed date tokens: {unparsed}")


if __name__ == "__main__":
    main()
