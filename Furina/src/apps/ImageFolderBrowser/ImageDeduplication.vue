<template>
  <div class="my-component">
    <div>
      <el-button :icon="Back" type="text" @click="router.push('/ImageFolderBrowser')"></el-button>
    </div>
    <el-table :data="show_list" border style="width: 100%">
      <el-table-column prop="id" label="任务ID" width="180" />
      <el-table-column prop="task_type" label="任务类型" width="180">
        <template #default="scope">
          <span>{{ taskType.get(scope.row.task_type) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="folder_path" label="文件夹路径" width="180">
        <template #default="scope">
          <el-text type="primary" @click="handleClickFolder(scope.row)">{{
            scope.row.folder_path
          }}</el-text>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="180" />
      <el-table-column prop="total" label="总数" width="180" />
      <el-table-column prop="status" label="任务状态" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column prop="updated_at" label="修改时间" />
    </el-table>
    <el-pagination
      background
      layout="prev, pager, next"
      :total="tableData.length"
      :page-size="page_size"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { folderService } from '@src/services/FolderService'
import type { ISafeAny } from '@src/types'
import { useRouter } from 'vue-router'
import { Back } from '@element-plus/icons-vue'

const router = useRouter()
const tableData = ref([])
const currentItem = ref([])
onMounted(() => {
  getList()
})
const taskType = new Map([['dedup', '去重']])
const current_page = ref(1)
const page_size = ref(20)
const getList = async () => {
  const res = await folderService.select_all_task_list()
  tableData.value = res
}
const show_list = computed(() => {
  const start_index = (current_page.value - 1) * page_size.value + 1
  const endIndex = start_index + page_size.value
  return tableData.value.slice(start_index, endIndex)
})
const handleCurrentChange = (index: number) => {
  current_page.value = index
}
const handleClickFolder = async (row: ISafeAny) => {
  console.log(row)
  const res = await folderService.select_all_task_result_list(row.id + '')
  currentItem.value = JSON.parse(res[0].result)
  router.push({ name: '任务详情', params: { id: row.id } })
}
</script>

<style scoped lang="scss">
.group-wrapper {
  margin-bottom: 20px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 20px;
}
.group-title {
  font-weight: bold;
  margin-bottom: 8px;
}
.group-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.image-thumb {
  width: 120px;
  height: auto;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #ccc;
}
.my-component {
  overflow-y: scroll;
  height: 100%;
  .el-table {
    margin-bottom: 16px;
  }
}
</style>
