<script setup lang="ts">
import { crawlerService } from '@src/services/CrawlerService'
import { onMounted, ref } from 'vue'
import type { IMediaItem, ISafeAny } from '@src/types'
import { ElLoading } from 'element-plus'
import { useCrawlerState } from '@stores/user'

const imageList = ref<IMediaItem[]>([])
const userName = ref('')
const originUrl = ref('')
const crawlerState = useCrawlerState()

const getImageList = async () => {
  const res = await crawlerService.fetch_yan_image()
  imageList.value = res.imageList
  userName.value = res.userName
  originUrl.value = res.from
}
const removeFile = async (url: string) => {
  const res = await crawlerService.remove_image_db(url)
  console.log(res)
  if (res.url) {
    imageList.value = imageList.value.filter((item) => item.url !== url)
  }
}

onMounted(() => {
  getImageList()
})
let loadingInstance: ISafeAny = null

const handleClickDownloadAll = async () => {
  let ind = 0
  loadingInstance = ElLoading.service({
    lock: true,
    text: `加载中... ${ind} / ${imageList.value.length}`,
    background: 'rgba(0, 0, 0, 0.7)',
  })
  const imgList = imageList.value.filter((item) => item.download_url)
  for (let i = 0; i < imgList.length; i++) {
    const item = imgList[i]
    loadingInstance.setText(`加载中... ${i + 1} / ${imgList.length}`)
    await crawlerService.download_file({
      folderPath: crawlerState.download_path,
      fileName: item.file_name as string,
      fileType: 'png',
      downloadFileUrl: [item.download_url as string],
      origin: 'yan',
    })
  }

  loadingInstance.close()
}
</script>

<template>
  <el-button @click="handleClickDownloadAll">下载全部</el-button>
  <ImageViewer
    v-if="imageList.length > 0"
    ref="childRef"
    :imageList="imageList"
    :originUrl="originUrl"
    :jumpC="true"
    @removeFile="removeFile"
  ></ImageViewer>
</template>

<style lang="scss" scoped></style>
