<script setup lang="ts">
import { ref } from "vue";
import { invokeRust } from "../../utils/invoke";
import { ElMessage, ElMessageBox } from "element-plus";
import { useStarsStore } from '@stores/index'
import imagePreview from "@src/components/image-preview.vue";


// const search = ref("https://weibo.com/u/1009328584");
const search = ref("https://mp.weixin.qq.com/s/eSikezklsJYFZoVg4gVXHA");
const images_list = ref<Array<{ url: string, preview_url: string }>>([]);
const stars_state = useStarsStore()
const image_preview = ref<InstanceType<typeof imagePreview>>();

const handleClickParseUrl = () => {
  stars_state.startLoading()
  if (search.value === "") {
    return;
  }
  invokeRust("parse_input_url", { parseUrl: search.value }).then((res) => {
    let arr: Array<{ url: string, preview_url: string }> = []
    const { url, preview_url } = res.data.image_list.Ok
    for (let i = 0; i < url.length; i++) {
      arr.push({ url: url[i], preview_url: preview_url[i] })
    }
    images_list.value = arr
    stars_state.set_user_name(res.data.user_name)
    stars_state.closeLoading()
  });
};

const removeLocalImage = (url: string) => {
  ElMessageBox.confirm("将永久删除该文件。是否继续？", "Warning", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      images_list.value = images_list.value.filter((item) => item.preview_url !== url);
      ElMessage({
        message: '删除成功',
        type: "success",
      });
    })
    .catch(() => { });
}

const downloadPicture = async (type: string) => {
  if (type === 'page') {
    const arr = image_preview.value?.show_list.map(item => item.preview_url)
    downloadImg(arr as string[])

  } else {
    const arr = images_list.value.map(item => {
      return item.preview_url
    })
    downloadImg(arr)
  }
}

const downloadImg = async (url: string[]) => {
  stars_state.startLoading()
  if (!localStorage.getItem('Stars_currentSavePage')) {
    const res = await invokeRust('open_file_dialog', {})
    console.log(res);
    localStorage.setItem('Stars_currentSavePage', res.data.current_page)
  } else {
    const res = await invokeRust('download_file', {
      folderPath: localStorage.getItem('Stars_currentSavePage') || '',
      imageList: url,
      imageType: 'png',
      userName: stars_state.user_name,
      origin_url: 'weixin'
    });
    stars_state.closeLoading()
  }
}

</script>

<template>
  <div :class="['crawler-container']">
    <el-row :gutter="20" :class="[images_list.length > 0 ? 'filled-content' : 'empty-content']">
      <el-col :span="12" :offset="6">
        <div :class="['grid-content']">
          <el-input v-model="search" />
          <el-button type="primary" @click="handleClickParseUrl">解析</el-button>
          <el-button type="primary" :disabled="images_list.length === 0"
            @click="downloadPicture('all')">下载全部</el-button>
          <el-button type="primary" :disabled="images_list.length === 0"
            @click="downloadPicture('page')">下载当前页</el-button>
        </div>
      </el-col>
    </el-row>
  </div>
  <imagePreview v-if="images_list.length > 0" :removeImage="removeLocalImage" :image_list="images_list"
    :currentPage="''" image_type="local" ref="image_preview"></imagePreview>
</template>

<style lang="scss" scoped>
.grid-content {
  display: flex;
  height: 100%;
  justify-content: center;
  align-items: center;

  .el-row {
    height: 40px;
  }

  .el-button {
    margin-left: 20px;
  }
}

.empty-content {
  margin-top: 24%;
}
</style>
