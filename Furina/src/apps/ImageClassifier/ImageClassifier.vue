<template>
  <div class="fnn-folder-browser-header">
    <el-button type="primary" @click="handleSelectFolder">选择文件夹</el-button>
    <el-divider direction="vertical" />
    <el-text
      >当前文件夹：<el-text type="primary">{{ crawlerState.current_page }}</el-text></el-text
    >
  </div>
  <div class="fnn-imageClassifier-container" v-if="imageList.length > 0">
    <el-image :src="imageList[0].preview_url"></el-image>
    <el-text>{{ imageList[0].preview_url }}</el-text>
    <el-text>{{ imageList.length }}</el-text>
  </div>
  <div class="fnn-imageClassifier-footer">
    <el-button
      v-for="item in folder_list"
      :key="item.folder_path"
      color="#626aef"
      @click="handleClickMoveFile(item.folder_path)"
      >{{ item.folder_name }}</el-button
    >
    <el-button :icon="Plus" type="primary" @click="open"></el-button>
    <el-button type="primary" @click="jump">remove</el-button>
  </div>
</template>

<script setup lang="ts">
import { folderService } from '@src/services/FolderService'
import { useCrawlerState } from '@stores/user'
import { ref, onMounted, watch } from 'vue'
import type { IMediaItem } from '@src/types'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const crawlerState = useCrawlerState()
const isLoading = ref(false)
const imageList = ref<IMediaItem[]>([])
const folder_list = ref<{ folder_path: string; folder_name: string }[]>([])
onMounted(() => {
  if (crawlerState.current_page) {
    getFolderImage()
    getFolderList()
  }
})

watch(
  () => crawlerState.current_page,
  async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      await getFolderImage()
      await getFolderList()
    }
  },
)
const jump = () => {
  imageList.value.shift()
}
const getFolderList = async () => {
  const res = await folderService.get_all_folder(crawlerState.current_page)
  folder_list.value = res.data.folder_list
}
const handleSelectFolder = async () => {
  const res = await folderService.openFileDialog()
  if (res?.data?.current_page) {
    crawlerState.set_current_page(res.data.current_page)
  }
}
const handleClickMoveFile = async (targe_folder: string) => {
  const res = await folderService.move_file(imageList.value[0].preview_url, targe_folder)
  if (res) {
    imageList.value.shift()
  }
}
const getFolderImage = async () => {
  if (!crawlerState.current_page) return
  try {
    isLoading.value = true
    const resp = await folderService.getFolderImage(crawlerState.current_page)
    if (resp?.data) {
      crawlerState.set_current_page(resp.data.folder_path) // 修正路径
      imageList.value = resp.data.image_urls
    }
  } finally {
    isLoading.value = false
  }
}
const make_folder = async (folderName: string) => {
  try {
    const res = await folderService.make_folder(crawlerState.current_page, folderName)
    if (res) getFolderList()
  } catch (e) {
    ElMessage({
      type: 'info',
      message: e as string,
    })
  }
}
const open = () => {
  ElMessageBox.prompt('请输入文件夹名', 'Tip', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    inputErrorMessage: '文件夹名',
  })
    .then(({ value }) => {
      make_folder(value)
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Input canceled',
      })
    })
}
</script>

<style scoped lang="scss">
.fnn-folder-browser-header {
  margin-bottom: 12px;
}
.fnn-imageClassifier-container {
  display: flex;
  justify-content: center;
  height: 80%;
  flex-direction: column;
  align-items: center;
}
.fnn-imageClassifier-footer {
  display: flex;
  margin-top: 16px;
  justify-content: center;
}
</style>
