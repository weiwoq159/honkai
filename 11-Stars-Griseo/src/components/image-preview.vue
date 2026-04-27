<script setup lang="ts">
import { Delete, Download } from "@element-plus/icons-vue";
import { computed, ref, watch } from "vue";
import { invokeRust } from '@utils/invoke'
import { useStarsStore } from '@stores/index'

const scrollContainer = ref<HTMLDivElement | null>(null);
const stars_state = useStarsStore()

const { image_list, removeImage } = defineProps<{
  image_list: Array<{ url: string, preview_url: string }>,
  currentPage: string,
  image_type: "local" | "network"
  removeImage: (url: string) => void
}>();


watch(() => image_list, (newVal) => {
  console.log(newVal);
})

const pagination_payload = ref({
  currentPage: 1,
  pageSize: 18,
});

const removecomponentsImage = async (url: string) => {
  removeImage(url)
};


const handleChangeCurrentPage = (page: number) => {
  pagination_payload.value.currentPage = page;
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = 0;
  }
};

const show_list = computed(() => {
  const { currentPage, pageSize } = pagination_payload.value;
  console.log(image_list);

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, image_list.length - 1);
  if (image_list.length <= pageSize) {
    return image_list
  }
  return image_list.slice(startIndex, endIndex);
});



const resetPagination = () => {
  pagination_payload.value.currentPage = 1
};

const downloadImg = async (url: string[]) => {
  if (!localStorage.getItem('Stars_currentSavePage')) {
    const res = await invokeRust('open_file_dialog', {})
    console.log(res);
    localStorage.setItem('Stars_currentSavePage', res.data.current_page)
  } else {
    const res = await invokeRust('download_file', {
      folderPath: localStorage.getItem('Stars_currentSavePage') || '',
      imageList: url,
      imageType: 'png',
      userName: stars_state.user_name || '微信',
      origin_url: 'weixin'
    });
    console.log(res);

  }
}

defineExpose({
  resetPagination,
  show_list
});

</script>

<template>
  <div class="image_list_container" ref="scrollContainer" v-if="image_list.length > 0">
    <div class="image_item" v-for="item in show_list" :key="item.url">
      <el-image fit="cover" :src="item.url" :hide-on-click-modal="true" :preview-src-list="[item.preview_url]"
        :lazy="true" loading="lazy"></el-image>
      <div class="btn_group">
        <el-button type="danger" :icon="Delete" @click="() => removecomponentsImage(item.preview_url)"></el-button>
        <el-button type="primary" :icon="Download" @click="() => downloadImg([item.preview_url])"></el-button>
      </div>
    </div>
  </div>
  <!-- <div v-for="item in image_list">
      <img :src="item"></img>
    </div> -->
  <el-pagination v-if="image_list.length > 0" size="small" background :current-page="pagination_payload.currentPage"
    layout="prev, pager, next" :total="image_list.length" :page-size="pagination_payload.pageSize"
    @current-change="(page: number) => handleChangeCurrentPage(page)" hide-on-single-page />

  <el-empty description="没有图片" v-if="image_list.length === 0" />
</template>

<style lang="scss" scoped>
.image_list_container {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(3, auto);
  grid-auto-flow: rows;
  /* 按列填充 */
  gap: 16px;
  height: calc(100% - 100px);
  overflow-y: auto;
  margin-top: 12px;

  .forder_path {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .el-button {
      margin-bottom: 0;
    }
  }

  .image_item {
    height: auto;
    max-height: 800px;
    margin-bottom: 10px;

    .btn_group {
      display: flex;
      justify-content: center;
      align-items: center;
      margin-top: 8px;
    }

    .el-image {
      width: 100%;
      height: calc(100% - 30px);
    }
  }
}

.image_list_container .el-button {
  margin-bottom: 12px;
}

.el-pagination {
  margin-top: 12px;
}
</style>