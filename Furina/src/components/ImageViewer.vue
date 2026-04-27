<script setup lang="ts">
import type { IMediaItem } from '@src/types'
import { ref, computed, watch } from 'vue'
import { Delete, Download } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useCrawlerState } from '@stores/user'
import { folderService } from '@src/services/FolderService'
import { crawlerService } from '@src/services/CrawlerService'
interface Props {
  imageList: Array<IMediaItem> | undefined
  userName: string | undefined
  originUrl: string | undefined
  jumpC?: string
}

const scrollContainer = ref<HTMLDivElement | null>(null)
const emit = defineEmits(['removeFile'])
const { imageList, userName, originUrl, jumpC } = defineProps<Props>()
const current_page_index = ref(1)
const page_size = ref(12)
const crawlerState = useCrawlerState()

const paginatedImages = computed(() => {
  const start = (current_page_index.value - 1) * page_size.value
  const end = start + page_size.value
  return imageList?.slice(start, end)
})
watch(paginatedImages, (newVal) => {
  console.log(newVal)
})
const currentPageChange = (index: number) => {
  current_page_index.value = index
  if (scrollContainer.value) {
    console.log(scrollContainer.value.scrollTop)
    scrollContainer.value.scrollTop = 0
  }
}

const handleClickRemoveImage = (filePath: string) => {
  if (jumpC) {
    emit('removeFile', filePath)
  } else {
    ElMessageBox.confirm('将永久删除该文件。是否继续？', 'Warning', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(async () => {
        emit('removeFile', filePath)
      })
      .catch(() => {})
  }
}
const handleClickDownloadImage = async (filePath: string) => {
  console.log(crawlerState.download_path)
  crawlerState.startLoading()
  if (!crawlerState.download_path) {
    const res = await folderService.openFileDialog()
    crawlerState.setDownloadPath(res.data.current_page)
  }
  let resp = await crawlerService.download_file({
    downloadFileUrl: [filePath],
    folderPath: crawlerState.download_path,
    userName: userName as string,
    fileType: 'png',
    origin: originUrl as string,
  })
  console.log(resp)
  crawlerState.closeLoading()
}
const resetPagination = () => {
  current_page_index.value = 1
}
defineExpose({
  resetPagination,
})
</script>

<template>
  <div class="fnn-image-viewer" ref="scrollContainer">
    <div class="fnn-image-scroll">
      <el-row :gutter="12" v-if="imageList">
        <el-col v-for="image in paginatedImages" :key="image.preview_url" :span="4">
          <el-image
            :src="image.preview_url"
            fit="cover"
            lazy
            :preview-src-list="imageList.map((item) => item.url)"
            :initial-index="imageList.findIndex((item) => item.preview_url === image.preview_url)"
            preview-teleported
            close-on-press-escape
            hide-on-click-modal
            :referrerpolicy="originUrl === 'weixin' ? 'no-referrer' : 'no-referrer-when-downgrade'"
          >
            <template #placeholder>
              <el-image src="/loading.jpg"></el-image>
            </template>
          </el-image>
          <div class="fnn-btn-group">
            <el-space wrap>
              <el-button
                type="primary"
                :icon="Download"
                @click="handleClickDownloadImage(image.url)"
                circle
                v-if="originUrl !== 'local'"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                @click="handleClickRemoveImage(image.url)"
              />
            </el-space>
          </div>
        </el-col>
      </el-row>
      <FurinaEmpty v-if="!imageList || imageList.length === 0"></FurinaEmpty>
    </div>
  </div>
  <el-pagination
    v-model:current-page="current_page_index"
    :page-size="page_size"
    :total="imageList?.length"
    layout="prev, pager, next"
    background
    @current-change="currentPageChange"
    hide-on-single-page
  />
</template>

<style lang="scss" scoped>
.fnn-image-viewer {
  height: calc(100% - 80px);
  overflow-y: scroll;
  overflow-x: hidden;
  margin-bottom: 12px;
}
.el-image {
  width: 100%;
  aspect-ratio: 3 / 5; // 👈 所有图片都是宽高 4:3
  border-radius: 8px; // 可选，让 UI 更精致
  overflow: hidden;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}
.fnn-btn-group {
  display: flex;
  justify-content: center;
  margin-top: 10px;
  margin-bottom: 12px;
}
.el-empty {
  height: 100%;
}
.fnn-image-scroll {
  height: 100%;
}
</style>
