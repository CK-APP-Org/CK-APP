<template>
  <q-page>
    <q-card flat bordered class="q-pa-xl q-mx-auto shadow-2" style="max-width: 500px; width: 91%">
      <div class="column items-center">
        <q-img src="promo/promologo.png" alt="logo" fit="contain" style="max-width: 300px;"/>
        <div class="text-h4 text-center q-mt-md">
          <strong>建北特約</strong>
          <br />
          <br />
        </div>
        <div class="text-center q-mb-md">
          <div style="font-size: larger; font-weight: bold;">建北特約使用準則</div>
        </div>
        <span>1. 特約店家將於店家明顯處，張貼建北特約專用貼紙，以供辨識。</span>
        <span>2. 使用特約時，請記得出示學生證或教師證，店家得以拒絕僅穿著制服者。</span>
      </div>
    </q-card>
    <div class="icon-grid app-container">
    <div v-for="item in filteredItems" :key="item.name" class="icon-item">
      <q-btn
        stack
        class="icon-btn"
        :rounded="true"
        @click="openLink(item.link)"
      >
        <q-icon :name="item.icon" size="2.5em" />
        <div class="text-content text-capitalize">{{ item.name }}</div>
      </q-btn>
    </div>
  </div>
  </q-page>
</template>

<script>
export default {
  data() {
    return {
      search: "",
      items: [
        { name: "官方網站", icon: "store", link: "https://cktfgpromo.cksc.tw" },
        { name: "建中地區", icon: "school", link: "https://cktfgpromo.cksc.tw/ckhs" },
        { name: "北車地區", icon: "train", link: "https://cktfgpromo.cksc.tw/taipeimainstation" },
        { name: "西門地區", icon: "store", link: "https://cktfgpromo.cksc.tw/ximen" },
        { name: "公館地區", icon: "local_mall", link: "https://cktfgpromo.cksc.tw/gongguan" },
        { name: "古亭地區", icon: "shop", link: "https://cktfgpromo.cksc.tw/guting" },
        { name: "其他地區", icon: "other_houses", link: "https://cktfgpromo.cksc.tw/other" },
      ],
    };
  },
  computed: {
    filteredItems() {
      return this.items.filter((item) =>
        item.name.toLowerCase().includes(this.search.toLowerCase())
      );
    },
  },
  methods: {
    openLink(link) {
      window.open(link, '_blank');
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 25px;
  font-weight: bold;
  max-width: 600px;
  margin: 0 auto;
}

.header {
  color: white;
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  width: 100%;
  height: 125px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.current-class-section {
  margin-bottom: 20px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
}

.icon-item {
  display: flex;
  justify-content: center;
  align-items: center;
}

.icon-btn {
  width: 100%;
  height: 0;
  padding-bottom: 100%;
  position: relative;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.icon-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.icon-btn ::v-deep .q-btn__content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.icon-btn ::v-deep .q-icon {
  margin-bottom: 5px;
  color: #4a4a4a;
}

.icon-btn ::v-deep .text-content {
  font-size: 1.1em;
  line-height: 1.2;
  color: #4a4a4a;
}
.text-capitalize {
  text-transform: capitalize;
}
</style>
