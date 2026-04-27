<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useCrawlerState } from '@stores/user'
import { folderService } from '@src/services/FolderService'
import type { IMediaItem } from '@src/types'
import ImageViewer from '@components/ImageViewer.vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
const imageList = ref<IMediaItem[]>([])
const originUrl = ref('local')
const crawlerState = useCrawlerState()
const isLoading = ref(false)
const childRef = ref<InstanceType<typeof ImageViewer> | null>(null)
const router = useRouter()
const handleSelectFolder = async () => {
  const res = await folderService.openFileDialog()
  if (res?.data?.current_page) {
    crawlerState.set_current_page(res.data.current_page)
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
      childRef.value?.resetPagination()
    }
  } finally {
    isLoading.value = false
  }
}

// 初始加载
onMounted(() => {
  if (crawlerState.current_page) {
    getFolderImage()
  }
})

// 监听路径变化
watch(
  () => crawlerState.current_page,
  async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      await getFolderImage()
    }
  },
)

// 删除文件
const removeFile = async (filePath: string) => {
  const res = await folderService.removeFile(filePath)
  imageList.value = imageList.value.filter((item) => item.url !== filePath)
  console.log('删除成功:', res)
}
const handleClickRemoveSamePicture = async () => {
  crawlerState.startLoading()
  const res = await folderService.deduplicate_images(crawlerState.current_page)
  console.log(res)
  ElMessage({
    message: '任务新建成功',
    type: 'success',
  })
  // file_list.value = selectDuplicates(res.data.file_list)
  crawlerState.closeLoading()
}

const handleClickNavigateListPage = () => {
  router.push('/deduplication')
}
const handleClickReset = async () => {
  const res = await folderService.reset_folder_images(crawlerState.current_page)
  if (res?.data) {
    crawlerState.set_current_page(res.data.folder_path) // 修正路径
    imageList.value = res.data.image_urls
    childRef.value?.resetPagination()
  }
}
</script>

<template>
  <div class="fnn-folder-browser-container">
    <div class="fnn-folder-browser-header">
      <el-button type="primary" @click="handleSelectFolder">选择文件夹</el-button>
      <el-button type="primary" @click="handleClickRemoveSamePicture">图片去重</el-button>
      <el-button type="primary" @click="handleClickNavigateListPage">任务列表</el-button>
      <el-button type="primary" @click="handleClickReset">重置后缀</el-button>
      <el-divider direction="vertical" />
      <el-text
        >当前文件夹：<el-text type="primary">{{ crawlerState.current_page }}</el-text></el-text
      >
    </div>
    <ImageViewer
      ref="childRef"
      :imageList="imageList"
      :userName="crawlerState.current_page"
      :originUrl="originUrl"
      @removeFile="removeFile"
    ></ImageViewer>
  </div>
</template>

<style lang="scss" scoped>
.fnn-folder-browser-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.fnn-folder-browser-container {
  height: 100%;
}
.deduplicate-container {
  position: relative;
}
.deduplicate-checkbox {
  position: absolute;
  top: -2px;
  right: 8px;
}
.deduplicate-col {
  margin-bottom: 16px;
  .el-text {
    margin-top: 12px;
  }
}
</style>
