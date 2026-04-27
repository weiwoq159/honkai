<script setup lang="ts">
import { invokeRust } from "@utils/invoke";
import imagePreview from "@src/components/image-preview.vue";
import { onMounted, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

const image_list = ref<Array<{ url: string, preview_url: string }>>([]);

const currentPage = ref<string>("");
const image_preview = ref<InstanceType<typeof imagePreview>>();

onMounted(() => {
  currentPage.value = localStorage.getItem("Stars_currentPage") || "";
});

const handleClickOpenFolder = async () => {
  const res = await invokeRust('open_file_dialog', {})
  if (res.status === 200) {
    currentPage.value = res.data.current_page;
    image_preview.value?.resetPagination()
  }
};

const get_image_list = async () => {
  let res = await invokeRust("fetch_folder_image", { currentPage: currentPage.value })
  image_list.value = res.data.image_list.map(item => ({
    url: item,
    preview_url: item
  }));

};


watch(currentPage, (newVal) => {
  if (newVal) {
    get_image_list();
  }
  if (newVal && newVal !== localStorage.getItem("Stars_currentPage")) {
    localStorage.setItem("Stars_currentPage", newVal);
  }
});


const removeLocalImage = async (url: string) => {
  ElMessageBox.confirm("将永久删除该文件。是否继续？", "Warning", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      const res: string = await invokeRust("remove_file", { imageUrl: url });
      image_list.value = image_list.value.filter((item) => item.preview_url !== url);
      ElMessage({
        message: res,
        type: "success",
      });
    })
    .catch(() => { });
}

</script>
<template>
  <div class="albumlist-container">
    <div class="forder_path">
      <el-button type="primary" @click="handleClickOpenFolder">选择文件夹</el-button>
      {{ currentPage }}
    </div>
    <imagePreview :removeImage="removeLocalImage" :image_list="image_list" :currentPage="currentPage" image_type="local"
      ref="image_preview" />
  </div>
</template>

<style lang="scss" scoped>
.el-pagination {
  margin-top: 16px;
}

.albumlist-container {
  padding-left: 12px;
  height: 100%;
  overflow: hidden;
}
</style>
