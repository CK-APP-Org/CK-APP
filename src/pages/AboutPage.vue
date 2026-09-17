<template>
  <q-page class="bg-grey-1">
    <q-carousel
      v-model="slide"
      transition-prev="slide-right"
      transition-next="slide-left"
      swipeable
      animated
      control-color="primary"
      prev-icon="chevron_left"
      next-icon="chevron_right"
      navigation-icon="lens"
      navigation
      padding
      arrows
      height="355px"
      class="bg-white text-primary shadow-3 rounded-borders q-mb-md"
    >
      <q-carousel-slide
        v-for="(slideContent, index) in carouselSlides"
        :key="index"
        :name="slideContent.name"
        class="column no-wrap flex-center"
      >
        <q-icon :name="slideContent.icon" size="56px" color="primary" />
        <div class="q-mt-md text-center text-h5 text-weight-bold">
          {{ slideContent.title }}
        </div>
        <div class="text-subtitle1 q-mt-md text-center q-px-lg">
          {{ slideContent.description }}
        </div>
      </q-carousel-slide>
    </q-carousel>

    <q-card class="q-ma-md">
      <q-card-section>
        <div class="text-h5 text-primary q-mb-md">關於這個APP</div>
        <p class="q-mb-sm">
          由兩位建中高三生於2024年所開發，CK
          APP旨在幫助所有建中生解決生活中遇到的大小困難。
        </p>
        <p class="q-mb-sm">
          我們歡迎使用者提供任何建議，若能精進CK
          APP以提升所有建中生的福祉，將是我們的一大榮幸。
        </p>
        <p class="q-mb-none">
          班聯會資訊股自2025年10月(80屆)起開始負責CK APP
          的維護與更新，如有任何問題亦歡迎與班聯會聯繫。
        </p>
      </q-card-section>
    </q-card>

    <q-card class="q-ma-md">
      <q-card-section class="row items-center">
        <div class="text-h5 text-primary q-mb-md">聯絡我們</div>
        <q-space />
        <div>
          <q-btn color="primary" icon="mail" @click="openEmailDialog = true" />
          <q-btn
            class="q-ml-sm"
            color="purple"
            icon="photo_camera"
            @click="openInstagram"
          />
          <q-btn
            class="q-ml-sm"
            color="blue"
            icon="language"
            @click="openOfficialWebsite"
          />
          <q-btn
            class="q-ml-sm"
            color="orange"
            icon="tag"
            @click="openckscinsta"
          />
        </div>
      </q-card-section>
    </q-card>

    <q-card class="q-ma-md">
      <q-card-section class="row items-center">
        <div class="text-h5 text-primary">版本資訊</div>
        <q-space />
        <q-btn
          color="primary"
          icon="info"
          label="3.1"
          @click="openVersionInfo = true"
        />
      </q-card-section>
    </q-card>

    <q-dialog v-model="openVersionInfo">
      <q-card style="min-width: 350px">
        <q-card-section class="q-pb-none">
          <div class="text-h6">CK APP 當前版本： 3.1</div>
        </q-card-section>

        <q-card-section class="q-pb-none">
          <div class="item-info-title q-mb-sm">更新項目：</div>
          <q-list dense>
            <q-item
              v-for="(item, index) in newFeatures"
              :key="index"
              class="item-info"
            >
              <q-item-section avatar>
                <q-icon name="add_circle_outline" color="primary" />
              </q-item-section>
              <q-item-section>{{ item }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="關閉" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="openEmailDialog">
      <q-card style="min-width: 300px">
        <q-card-section>
          <div class="text-h6">Email 地址</div>
        </q-card-section>
        <q-card-section>
          <p>CK APP : ckappofficial@gmail.com</p>
          <p>班聯會 : ckhssc@gl.ck.tp.edu.tw</p>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="關閉" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref } from "vue";

export default {
  setup() {
    const slide = ref("Intro");
    const openVersionInfo = ref(false);
    const openEmailDialog = ref(false);
    const newFeatures = ref([
      "新增校慶紀念品訂購功能",
      "新增特約商店功能",
      "新增北捷即時動態",
      "校網資料自動背景刷新",
      "自由設定首頁&工具列項目",
      "美食地圖隨機選擇餐廳",
      "美食地圖資訊更新",
      "暫時移除課表及註冊功能",
      "新增選擇障礙小幫手功能",
    ]);
    const carouselSlides = [
      {
        name: "Intro",
        icon: "school",
        title: "CK APP : 您專屬的校園助理",
        description: "向右滑以查看更多說明",
      },
      {
        name: "Schedule",
        icon: "book",
        title: "課表 : 輕鬆規劃，客製格式",
        description: "自訂科目名稱，加上註解並客製化每一格的顏色",
      },
      {
        name: "Calendar",
        icon: "calendar_month",
        title: "行事曆 : 輕鬆規劃每一天",
        description:
          "分成月曆和待辦兩個頁面，讓學生能夠有效掌握未來的所有活動和工作",
      },
      {
        name: "Transport",
        icon: "directions_walk",
        title: "交通：掌握臺北最新交通動態",
        description: "客製化呈現即時YouBike及北捷交通資訊，提升通勤效率",
      },
      {
        name: "Menu",
        icon: "restaurant_menu",
        title: "熱騰騰的菜單 : 輕鬆查詢，找到美味",
        description: "即時更新熱食部每月菜單與早餐部的菜單，並顯示營業時間",
      },
      {
        name: "Food",
        icon: "fastfood",
        title: "美食地圖&即時營業資訊，不再白跑一趟",
        description: "即時顯示建中附近餐廳之營業狀態及建中生之特殊優惠",
      },
      {
        name: "News",
        icon: "newspaper",
        title: "校網追蹤，即時更新",
        description:
          "追蹤校網的所有公告，自由已讀或釘選，不再漏接訊息或被不重要的訊息干擾",
      },
      {
        name: "Promo",
        icon: "store",
        title: "建北特約，節省荷包",
        description:
          "查詢建北特約相關資訊，為自己節省荷包",
      },
      {
        name: "Souvenir",
        icon: "shopping_bag",
        title: "校慶紀念品，隨時都能買",
        description:
          "今日我以建中為榮，明日建中以我為榮",
      },
    ];

    const openInstagram = () => {
      window.open(
        "https://www.instagram.com/ckappofficial?igsh=MXRtczJxZW90bjA4Nw==",
        "_blank"
      );
    };

    const openOfficialWebsite = () => {
      window.open("https://ckapp-tw.web.app/", "_blank");
    };

    const openckscinsta = () => {
      window.open("https://www.instagram.com/cksc.80th/", "_blank")
    }

    return {
      slide,
      carouselSlides,
      openVersionInfo,
      newFeatures,
      openEmailDialog,
      openInstagram,
      openOfficialWebsite,
      openckscinsta,
    };
  },
};
</script>

<style lang="scss">
.q-carousel {
  .q-carousel__slide {
    padding: 1rem;
  }
}
.item-info-title {
  font-size: 18px;
}
.item-info {
  font-size: 17px;
}
</style>
