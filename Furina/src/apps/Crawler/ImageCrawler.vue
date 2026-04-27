<script setup lang="ts">
import { ref, computed } from 'vue'
import { crawlerService } from '@src/services/CrawlerService'
import type { IMediaItem } from '@src/types'
import { useCrawlerState } from '@stores/user'
import { folderService } from '@src/services/FolderService'
import ImageViewer from '@components/ImageViewer.vue'

const crawlerState = useCrawlerState()

const unParseUrl = ref<string>('https://weibo.com/u/1009328584')
const imageList = ref<IMediaItem[]>([])
const userName = ref('')
const originUrl = ref('')
const childRef = ref<InstanceType<typeof ImageViewer> | null>(null)

// // 用于 UI 判断：是否存在图片列表
const hasImageList = computed(() => {
  return imageList.value.length > 0
})
const handleParseUrl = async () => {
  try {
    console.log('解析链接：', unParseUrl.value)
    const res = await crawlerService.parse_url(unParseUrl.value)
    userName.value = res.userName
    imageList.value = res.imageList
    originUrl.value = res.from
    childRef.value?.resetPagination()
    // TODO: 实际调用解析接口
  } catch (err) {
    console.error('解析失败:', err)
  }
}
const removeFile = async (filePath: string) => {
  imageList.value = imageList.value.filter((item) => item.url !== filePath)
}

const handleClickDownloadImage = async () => {
  crawlerState.startLoading()
  if (!crawlerState.download_path) {
    const res = await folderService.openFileDialog()
    crawlerState.setDownloadPath(res.data.current_page)
    return
  }
  let resp = await crawlerService.download_file({
    downloadFileUrl: imageList.value.map((item) => item.url),
    folderPath: crawlerState.download_path,
    userName: userName.value,
    fileType: 'png',
    origin: originUrl.value,
  })
  crawlerState.closeLoading()
  console.log(resp)
}
</script>

<template>
  <div :class="['fnn-crawler-container', { 'is-empty': !hasImageList }]">
    <div :class="['fnn-crawler-header', { 'has-image': hasImageList }]">
      <el-input v-model="unParseUrl"></el-input>
      <el-button type="primary" @click="handleParseUrl">解析</el-button>
      <el-button type="primary" @click="handleClickDownloadImage" :disabled="!imageList.length"
        >下载全部</el-button
      >
    </div>
    <ImageViewer
      v-if="imageList.length > 0"
      ref="childRef"
      :imageList="imageList"
      :userName="userName"
      :originUrl="originUrl"
      @removeFile="removeFile"
    ></ImageViewer>
  </div>
</template>

<style lang="scss" scoped>
.fnn-crawler-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;

  &.is-empty {
    justify-content: center;
  }
}

.fnn-crawler-header {
  display: flex;
  align-items: center;
  padding: 16px 20%;
  gap: 16px;

  &.has-image {
    margin-top: 16px;
  }
}
</style>
