# CK APP 校園行動應用程式

**語言 / Language：** 中文（本頁） ｜ [English](README.en.md)

> 當前版本：**3.1**（`src-capacitor/android/app/build.gradle` 的 `versionName`）　｜　文件最後更新：2026-07
>
> ⚠️ 注意：`package.json` 的 `version` 欄位目前仍是 `3.0.1`，與實際版本不同步。版本的真正來源是 Android 的 `build.gradle` 與 iOS 的 `project.pbxproj`（見[開發說明](#開發說明)）。

## 目錄
1. [CK APP是什麼？](#ck-app是什麼)
2. [CK APP架構介紹](#ck-app架構介紹)
3. [頁面/功能介紹](#頁面功能介紹)
4. [Store 與其他基礎建設](#store-與其他基礎建設)
5. [已知問題與待辦](#已知問題與待辦)
6. [開發說明](#開發說明)
7. [貢獻](#貢獻)

## CK APP是什麼？
CK APP是建中第77屆學生彭可翰和楊晨諺於2024年暑假所開發的應用程式，目的是幫助所有建中生解決生活中遇到的大小困難。CK APP自從2024年9月在iOS和Android雙平台上架至2025年9月共累積2080次下載。我們期許CK APP能夠持續幫助未來的所有建中生。

## CK APP架構介紹
CK APP的主要程式和資料皆位於GitHub，其共有兩個repo——CK_app和Data (其實有第三個repo Proxy，但他現在是廢棄狀態，為過去Heroku之程式)。這個repo（`CK_app`）本身就是Quasar專案的根目錄——`package.json`、`src/`等都直接在repo根目錄下，clone下來後不需要再往下一層資料夾。

### Data
Data為存放需動態改動之資料，讓CK APP可以直接讀取。目前實際使用中的只剩：
- menus: 存放熱食部菜單的資料夾（見下方 [MenuPage](#menupage-熱食部) 說明）

> 課表資料（原本的 `ClassesSchedule.json`）過去也放在這裡，但校方一度基於隱私權停止提供資料來源，導致這個機制停擺了一段時間。後來取得新的班級課表資料後，我們改成直接把資料打包進 `CK_app` 這個repo本身（`src/data/schedules/`），不再依賴 Data repo或外部網路請求——細節見下方 [SchedulePage](#schedulepage-課表) 說明。

### CK_app
CK_app為CK APP的主體程式，語言是Quasar Framework，本質上為HTML、CSS和JavaScript。當初選用Quasar是因為可以輸出成Android和iOS的app，不需寫兩個不同版本。

以下列出常用檔案/資料夾說明
- **public**
	- food: FoodPage的圖標
	- metro: TransportPage中各路線的圖標
	- promo: PromoPage 的 logo
- **src**
	- **boot**: App 啟動時載入的初始化程式
		- axios.js: 設定 axios（HTTP 請求）
		- i18n.js: 初始化多語系（vue-i18n）
	- **data**
		- metroData.js: 北捷站點和路線資訊
		- restaurantData.json: FoodPage餐廳資料 (有想過丟到Data，才可以動態改動，但這樣Android版不知道為什麼無法讀取資料\==)
		- schedules/: 全校班級課表（高一/高二/高三三個原始 JSON + 一個 `index.js` 把它們轉成頁面要的格式），見 [SchedulePage](#schedulepage-課表)
	- **i18n**: 多語系字串（目前僅有 `en-US`，尚未真正全面使用）
	- **pages**: CK APP的核心，大部分的開發工作會在這裡進行（共 12 個頁面，見[頁面/功能介紹](#頁面功能介紹)）
	- **components / layouts**: 共用元件（如 `EssentialLink.vue`）與版型（`MainLayout.vue`）
	- **router**
		- routes.js: 如果有新增頁面要去這裡登記，才可以從其他頁面連結過去
	- **services**
		- newsService.js: 讓NewsPage每隔2分鐘自動刷新資料
	- **store**: 頁面會透過這裡更動本機資料，非常重要（見 [Store 章節](#store-與其他基礎建設)）
	- **utils**
		- xmlUtils.js: 解析校網 XML 的工具
- **tools**（位於 repo 根目錄，與 `src/` 同層，非 Vite 專案的一部分）
	- Convert_xlsx_to_json.py: 把教務處課表檔(.xls)轉成json，使用說明在檔案裡（⚠️ 輸出格式目前跟 `src/data/schedules/` 用的格式不一致，見[已知問題](#已知問題與待辦)）
	- menu_scraper.py / menu_visualizer.py: 舊版手動菜單轉圖工具，現已由 Data repo 的 Action 取代（見 MenuPage 說明）

除了GitHub外，我們也有[官方網站](https://ckapp-tw.web.app/) (由 78屆的Ian Wen開發管理)、官方gmail(ckappofficial@gmail.com)和[官方IG帳號](https://www.instagram.com/ckappofficial/)。（過去也曾用Firebase儲存登入使用者的資料，但登入功能與Firebase已完全移除，見[已知問題與待辦](#已知問題與待辦)。）

## 頁面/功能介紹
CK APP目前共有 **12 個頁面**（皆於 `src/router/routes.js` 登記），皆由Quasar Framework寫成。Quasar的檔案(.vue)分為三個部分——\<template>、\<script>、\<style>，即HTML、Javascript和CSS。

### HomePage (首頁)
除了六個頁面的按鈕外，首頁還包含三個動態資訊：目前課程、今日待辦事項、釘選校網內容。

### SchedulePage (課表)
建中的課表（含高一、高二、高三共81個班級、每天8節課）打包成三個 JSON 檔放在 `src/data/schedules/`（`gaoyi_schedules.json`、`gaoer_schedules.json`、`gaosan_schedules.json`），由同資料夾的 `index.js` 轉成頁面要的格式，並提供班級清單（`CLASS_OPTIONS`）與「目前是第幾節課」的判斷（`getCurrentPeriodName`，會對照各節課真實的上下課時間，包含午休空檔）。

頁面上「設定班級」和重新整理按鈕會直接切換/重讀本機資料，不需要網路連線。使用者自訂的科目、顏色、備註仍會存在 `localStorage`（見 [Store 章節](#store-與其他基礎建設)），不會被內建課表資料覆蓋，除非手動點重新整理。

> 這個機制在2025年10月一度因校方隱私考量而停用（改成「請自行輸入」），2026年7月才恢復——詳細原因與決策過程見 [`docs/decisions/feature-schedule-data-import/`](docs/decisions/feature-schedule-data-import/restore-schedule-data-import.md)。

### TodoPage (行事曆)
行事曆頁面分為兩個部分：月曆&待辦。詳細運作方式有點複雜，但應該不用改所以就不解釋了:D

### TransportPage (交通)
這是CK APP最龐大的頁面，程式分為YouBike和北捷兩部分。

YouBike部分，我們分別讀取[台北市](https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json)和[新北市](https://data.ntpc.gov.tw/openapi/swagger-ui/index.html?configUrl=%2Fapi%2Fv1%2Fopenapi%2Fswagger%2Fconfig&urls.primaryName=%E6%96%B0%E5%8C%97%E5%B8%82%E6%94%BF%E5%BA%9C%E4%BA%A4%E9%80%9A%E5%B1%80%2863%29#/)YouBike的API。新北市的API比較毒瘤一點，資料分成兩個頁面，所以需要分兩次API call。\
另外，新增站點有一個搜尋離使用者最近的九個站點的功能。我們本來想直接偵測使用者位置，但這會需要使用者開啟權限才行，然後這東西有點難寫，所以我們暫時放棄。

北捷部分，我們有向北捷公司申請才能拿到他們的API。然後其實使用條款包含下列兩項：
- 會員需於開發完成後主動通知本公司應用成果資訊,並依本公司需求回饋加值應用內容、用戶數及其他可了解加值應用成效之統計數字作為本公司 API 發展管理之參考。
- 會員用戶若您超過三個月未使用本公司 API 服務,本公司將有權終止會員帳號,取消會員資格。

但我們沒有鳥他就是了。

### MenuPage (熱食部)
熱食部通常會在月底把下個月的菜單放到[雲端](https://drive.google.com/drive/folders/1jZTQNkQVCoDVmMPQaG2Ov_Zwu4o4cmQQ)（依學期分資料夾，例如 `115-1`，每週一個 xlsx 檔）。

**菜單現在由 Data repo 的 GitHub Action 自動更新**（`.github/workflows/update-menu.yml`）：每天台灣時間 02:00，Action 會透過 Google Drive API 讀取最新兩個學期資料夾內的 xlsx，用 `scripts/` 裡的 scraper/visualizer 產生本週及之後的每日菜單 png，有變更才 commit 到 `menus/`。平日若本週菜單仍缺檔，workflow 會失敗並寄信通知。
- 需要的設定：在 GCP 啟用 Google Drive API 並建立 API key，存成 Data repo 的 secret `GOOGLE_DRIVE_API_KEY`。
- 想立刻更新：到 Data repo 的 Actions → Update cafeteria menu → Run workflow。
- 本機手動執行：`pip install -r scripts/requirements.txt` 後 `GOOGLE_DRIVE_API_KEY=... python scripts/update_menu.py`（可加 `--dry-run` 只解析不輸出）。
- xlsx 的日期是從表格裡的「週一日期」讀取，不看檔名，所以檔名亂取也沒關係。

`tools/` 裡的 `menu_scraper.py`、`menu_visualizer.py` 是舊版手動流程，正式版本在 Data repo 的 `scripts/`。

圖片檔名說明：菜單的圖片的檔名命名準則為當週週一之日期以及星期幾。例如2025/9/11為該週之星期四，該週週一為9/8，故9/11的菜單檔名為```2025-09-08_4.png```。然而因為程式有bug，所以目前上架版本中，有時候MenuPage會把週一的日期往前算一天（`toISOString()` 轉成 UTC，台灣時間 08:00 前會變成前一天）。所以 visualizer 同時會輸出一份週日日期的檔名，以9/11的例子就是```2025-09-07_4.png```。

### FoodPage (美食)
我們的地圖是用leaflet插件，餐廳資料來源是restaurantData.json。有些店家的營業時間會顯示超過24點，那是因為我們為了讓圖標顏色顯示正常(否則23:30後圖標會變淺綠色，因為程式會以為24點就要關門了，但實際上店家營業時間可能到凌晨2點)。以後可以修正。\
前面有講過我們有想把restaurantData.json丟到Data repo，方便動態修正資料，但Android版不知道是什麼bug，抓得到GitHub的資料但創建圖標的時候就會顯示不出來。可以再試試看。

### NewsPage (校網)
校網頁面的資料來源是[建中校網](https://www.ck.tp.edu.tw/nss/p/index)重要公告和最新消息的欄位中長得像Wi-Fi符號的按鈕，點下去會有XML檔可以讀。\
前面提過，newsService.js每隔兩分鐘會在背景自動抓校網資料。

### PromoPage (建北特約)
「建北特約」目錄頁。內含特約使用準則，並以分區按鈕（建中、北車、西門、其他）連結到外部網站 [`cktfgpromo.cksc.tw`](https://cktfgpromo.cksc.tw)。

### SouvenirPage (紀念品)
以 iframe 內嵌外部紀念品商店 [`souvenir.cksc.tw/auth`](https://souvenir.cksc.tw/auth)，本身幾乎沒有自己的邏輯，主要當作 App 內的入口。

### HelpPage (選擇障礙小幫手)
小工具頁：使用者每行輸入一個選項，按下按鈕後隨機幫你選一個。純前端、無外部資料。

### SettingsPage
滿直觀的。可以切換班級（會連動 SchedulePage）、調整首頁要顯示哪些區塊、自訂工具列。

### AboutPage
顯示版本資訊（目前為 3.1）。版本要記得改（見[開發說明](#開發說明)）。之後應該要增加開發者介紹。

> 另外還有 `ErrorNotFound.vue` 作為找不到路由時的 404 頁（不算在 12 個功能頁面內）。

## Store 與其他基礎建設

### Store（Vuex）
`src/store/` 是 App 的本機狀態中心，**非常重要**。各頁面透過它讀寫資料，並由 `localStoragePlugin.js` 自動同步到瀏覽器 / 裝置的 `localStorage`，所以資料在重開 App 後仍會保留。

目前共有 7 個模組（`src/store/modules/`）：

| 模組 | 對應功能 |
| --- | --- |
| `youbike` | YouBike 站點資料與我的最愛站點（TransportPage） |
| `metro` | 北捷站點/路線狀態（TransportPage） |
| `news` | 校網公告快取（搭配 newsService 每 2 分鐘更新，NewsPage） |
| `schedule` | 班級課表與目前設定的班級（SchedulePage） |
| `todo` | 行事曆與待辦事項（TodoPage） |
| `food` | FoodPage 餐廳相關狀態 |
| `settings` | App 設定（SettingsPage） |

其他：
- `localStoragePlugin.js`：把 store 內容持久化到 `localStorage`。
- `clearALL` action / `CLEAR_DATA` mutation：清除所有本機資料、把各模組重設為預設值。

### i18n（多語系）
專案有用 `vue-i18n` 搭好多語系骨架（`src/boot/i18n.js`、`src/i18n/`），預設語系為 `en-US`。但目前實際上只有 `en-US` 一份字串、且大部分介面文字仍直接寫死成中文，所以多語系還沒真正派上用場——未來若要做中英切換，這裡是起點。

## 已知問題與待辦
把散落在各頁說明裡的 TODO / 已知 bug 集中如下，方便接手的人一眼看到：

- [ ] **版本號不同步**：`package.json` 為 `3.0.1`，實際上架版本為 `3.1`。可考慮統一來源。
- [ ] **課表轉檔工具與新資料格式不一致**：`tools/Convert_xlsx_to_json.py` 輸出的是舊格式（單一 `ProcessedClassesSchedule.json`，原本是要手動貼到 Data repo），但 SchedulePage 現在讀的是 `src/data/schedules/` 底下三份依年級分開、形狀也不同的 JSON。未來要換學期課表時，這個工具需要先更新（或重寫）才能直接產生新格式的檔案。
- [ ] **MenuPage 日期 off-by-one**：MenuPage 有時把週一日期往前算一天；目前靠 `menu_visualizer` 多輸出一份檔名迴避，根因尚未修。
- [ ] **FoodPage 營業時間 hack**：為了圖標顏色正常，部分店家時間寫成超過 24 點，未來應正規化處理跨夜營業。
- [ ] **restaurantData 無法動態化**：想搬到 Data repo 動態更新，但 Android 版抓得到資料卻畫不出圖標，待查。
- [ ] **TransportPage 定位功能**：原本想自動偵測使用者位置找最近站點，因權限與實作成本暫時放棄。
- [ ] **i18n 尚未落實**：骨架已有但介面文字多為寫死中文。
- [ ] **AboutPage**：可加入開發者介紹。

> 登入功能與 Firebase 已經在 [Phase 3 重構](docs/decisions/phase-3-remove-login/) 中整個移除了，不再是待辦事項。想了解過去重構的細節（含安全性修正、程式碼整理），可以看 [`docs/refactoring-plan.md`](docs/refactoring-plan.md) 與 [`docs/decisions/`](docs/decisions/) 底下各任務的說明文件。

## 開發說明
### 在電腦以網頁模擬
1. 下載Node.js (https://nodejs.org/en/download/)
2. 下載Git (https://git-scm.com/downloads)
3. 開啟終端機(Terminal)並輸入 `git clone https://github.com/CK-APP-Org/CK_app.git`
4. 進入資料夾 `cd CK_app`
5. 安裝Quasar CLI `npm install -g @quasar/cli`
6. 安裝套件 `yarn install`
7. 啟動網頁模擬 `quasar dev`
8. 在瀏覽器開啟 `http://localhost:9000`

### 上架 (Android)
[![Build (& Deploy to Google Play) Android APP](https://github.com/CK-APP-Org/CK_app/actions/workflows/build_android.yml/badge.svg)](https://github.com/CK-APP-Org/CK_app/actions/workflows/build_android.yml)
1. 在 `src-capacitor\android\app\build.gradle` 改版本 (`versionCode` & `versionName`)
2. (a) 執行 Github Action - Deploy Android APP to Google Play；或 (b) 在commit時commit message前加入`[deploy] `，將自動嘗試上傳&上架

### 上架 (iOS)
[![Build (& Deploy to TestFlight) iOS APP](https://github.com/CK-APP-Org/CK_app/actions/workflows/build_ios.yml/badge.svg)](https://github.com/CK-APP-Org/CK_app/actions/workflows/build_ios.yml)
1. 在 `src-capacitor\ios\App\App.xcodeproj\project.pbxproj` 改版本 (`CURRENT_PROJECT_VERSION` & `MARKETING_VERSION`) (debug & release 都要)
2. (a) 執行 Github Action - Deploy iOS App to TestFlight；或 (b) 在commit時commit message前加入`[deploy] `，將自動嘗試上傳&上架

> ⚠️ 這兩個 GitHub Action 都會在push到 `main` 且改到程式碼時自動**build**（但不會上架）。真正觸發**上架**（送到 Google Play / TestFlight）需要滿足其中一個條件：手動在 GitHub Actions 頁面點「Run workflow」，或是讓push到 `main` 的那個commit（例如merge PR時的merge commit）訊息開頭是`[deploy] `。合併PR時GitHub預設不會這樣命名merge commit，所以一般merge PR不會不小心觸發上架。

## 貢獻
歡迎接手與貢獻！提交 PR 前請先閱讀 [貢獻指南 (CONTRIBUTING.md)](CONTRIBUTING.md)。
