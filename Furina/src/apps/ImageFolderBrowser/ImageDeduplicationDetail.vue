<template>
  <div :style="{ marginBottom: '10px' }">
    <el-button :icon="Back" type="primary" @click="router.push('/ImageFolderBrowser')"></el-button>
    <el-button @click="handleClickRemove">删除</el-button>
  </div>
  <div class="detail_container">
    <div class="group-wrapper">
      <el-row v-for="(group, index) in show_list" :key="index">
        <el-col class="img_container" v-for="img in group" :key="img.file_path" :span="3">
          <el-image
            :src="`http://asset.localhost/${img.file_path}`"
            fit="cover"
            :preview-src-list="[`http://asset.localhost/${img.file_path}`]"
          ></el-image>
          <el-text type="primary">{{ img.file_path }}</el-text>
          <el-text type="primary">{{ byteToMb(img.file_size) }}</el-text>
          <!-- 绑定 is_select -->
          <el-checkbox v-model="img.is_select" />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { folderService } from '@src/services/FolderService'
import { Back } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import type { ISafeAny } from '@src/types'
import { ElMessage } from 'element-plus'
const router = useRouter()
const { id } = defineProps<{ id: string }>()
const currentItem = ref<Array<ISafeAny>>([])
const handleClickRemove = async () => {
  const arr = show_list.value
    .flat()
    .filter((item) => item.is_select)
    .map((item) => item.file_path)
  arr.forEach(async (item) => {
    const res = folderService.removeFile(item)
    console.log(res)
  })
  // router.push('/ImageFolderBrowser')
  ElMessage({
    type: 'success',
    message: '删除完成',
  })
  currentItem.value = currentItem.value.splice(10)
}
watch(
  currentItem,
  (newVal) => {
    console.log(newVal.length)
  },
  { deep: true },
)
const getList = async () => {
  const res = await folderService.select_all_task_result_list(id + '')
  currentItem.value = markImagesToDelete(JSON.parse(res[0].result))
}
const show_list = computed(() => {
  console.log(currentItem.value)

  return currentItem.value.slice(0, 10)
})

onMounted(() => {
  getList()
})
const byteToMb = (bytes: number) => {
  console.log(bytes)
  const kb = bytes / 1024

  return kb > 1024 ? `${(kb / 1024).toFixed()}Mb` : `${kb.toFixed(2)}Kb`
}
function markImagesToDelete(groups: ISafeAny[][]): ISafeAny[][] {
  for (const group of groups) {
    if (group.length <= 1) {
      // 只有一张图，默认设为不删除
      if (group[0]) group[0].is_select = false
      continue
    }

    // 找到最优保留的那一张
    const best = group.reduce((prev, curr) => {
      // 比较文件大小
      if (curr.file_size > prev.file_size) return curr
      if (curr.file_size < prev.file_size) return prev

      // 文件大小相同，比较是否 png
      const currIsPng = curr.file_path.toLowerCase().endsWith('.png')
      const prevIsPng = prev.file_path.toLowerCase().endsWith('.png')
      if (currIsPng && !prevIsPng) return curr
      if (!currIsPng && prevIsPng) return prev

      // 文件大小、扩展名都相同，比较更新时间
      if (curr.file_update_time > prev.file_update_time) return curr
      return prev
    }, group[0])

    // 遍历设置 is_select，非最佳设为 true，最佳设为 false
    for (const img of group) {
      img.is_select = img !== best
    }
  }
  return groups
}
</script>

<style scoped lang="scss">
.img_container {
  margin-right: 6px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  span {
    width: 100%;
    font-size: 14px;
    line-height: 16px;
  }
}
.el-row {
  margin-bottom: 12px;
}
.detail_container {
  height: 100%;
  overflow-y: auto;
}
.group-wrapper {
  padding-bottom: 20px;
}
.el-col .el-checkbox {
  position: absolute;
  right: 8px;
  top: 8px;
}
.el-row {
  .el-col {
    position: relative;
    .el-image {
      width: 100%;
    }
  }
}
</style>
