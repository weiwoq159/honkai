<template>
  <div class="fnn-baidu-photo-container">
    <el-row :gutter="20">
      <!-- <el-input type="primary" :disabled="true" v-model="crawlerState.baidu_bdstoken">
          {{ crawlerState.baidu_bdstoken }}
        </el-input> -->
      <el-button @click="dialogFormVisible = true" type="primary">设置</el-button>
      <el-button type="primary" @click="handleClickDownloadAll" :icon="Download">
        下载全部
      </el-button>
      <el-button @click="handleClickFixMedia">
        无下载链接 {{ imageList.filter((item) => !item.download_url).length }}
      </el-button>
    </el-row>
  </div>

  <ImageViewer
    ref="childRef"
    :imageList="imageList"
    :userName="'baidu'"
    :originUrl="originUrl"
    @removeFile="removeFile"
  >
  </ImageViewer>
  <el-drawer v-model="dialogFormVisible" :direction="'rtl'">
    <template #header>
      <h4>设置一刻相册参数</h4>
    </template>
    <template #default>
      <el-form :model="form">
        <el-form-item label="Baidu_bdstoken" label-width="120">
          <el-input v-model="form.baidu_bdstoken" type="primary"> </el-input>
        </el-form-item>
        <el-form-item label="Cookies" label-width="120">
          <el-input v-model="form.cookies" type="primary"> </el-input>
        </el-form-item>
      </el-form>
    </template>
    <template #footer>
      <div style="flex: auto">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleClickConfirm" :disabled="!form.baidu_bdstoken">
          确定
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { useCrawlerState } from '@stores/user'
import { ref, reactive, onMounted } from 'vue'
import { crawlerService } from '@src/services/CrawlerService'
import type { IMediaItem, ISafeAny } from '@src/types'
import { ElLoading } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
const dialogFormVisible = ref(false)
const imageList = ref<IMediaItem[]>([])
const originUrl = ref('originUrl')
const crawlerState = useCrawlerState()
const form = reactive({
  baidu_bdstoken: '',
  cookies: '',
})
onMounted(() => {
  if (!form.baidu_bdstoken) {
    form.baidu_bdstoken = crawlerState.baidu_bdstoken
    form.cookies = crawlerState.baidu_cookie
  }
})
const handleClickFixMedia = async () => {
  const res = await crawlerService.resolve_media_list(crawlerState.baidu_bdstoken)
  console.log(res)
}
const handleClickConfirm = () => {
  crawlerState.setBaiduBdstoken(form.baidu_bdstoken)
  crawlerState.setBaiduCookie(form.cookies)
  dialogFormVisible.value = false
}
onMounted(() => {
  if (!crawlerState.baidu_bdstoken) {
    dialogFormVisible.value = true
  } else {
    getImageList()
  }
})
const getImageList = async () => {
  let res = await crawlerService.fetch_baidu_image_list(
    crawlerState.baidu_bdstoken,
    crawlerState.baidu_cookie,
  )
  console.log(res)
  imageList.value = res.imageList
}
const removeFile = async (filePath: string) => {
  const res = await crawlerService.remove_image_db(filePath)
  imageList.value = imageList.value.filter((item) => item.url !== filePath)
  console.log('删除成功:', res)
}
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
      fileType: item.format as string,
      downloadFileUrl: [item.download_url as string],
      origin: 'baidu',
    })
  }

  loadingInstance.close()
}
</script>

<style scoped lang="scss">
.fnn-baidu-photo-container {
  margin-bottom: 16px;
}
</style>
