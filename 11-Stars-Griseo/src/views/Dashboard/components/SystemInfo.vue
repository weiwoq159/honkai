<script setup lang="ts">
import { useRoute } from "vue-router";
import { ref } from 'vue';
const route = useRoute();
const mode_env = import.meta.env.VITE_USER_NODE_ENV;
const currentPreviewFolder = ref(localStorage.getItem('Stars_currentPage') ?? '\\')
const currentSaveFolder = ref(localStorage.getItem('Stars_currentSavePage') ?? '\\')
console.log(import.meta.env);
</script>
<template>
  <div class="system_info_container">
    <el-divider />
    <el-descriptions title="系统信息" border :column="1">
      <el-descriptions-item label="语言">中文简体</el-descriptions-item>
      <el-descriptions-item label="当前页面路径">{{
        route.fullPath
      }}</el-descriptions-item>
      <el-descriptions-item label="当前页面名称">{{
        route.name
      }}</el-descriptions-item>
      <el-descriptions-item label="系统平台">win32</el-descriptions-item>
      <el-descriptions-item label="系统版本">10.0.26100</el-descriptions-item>
      <el-descriptions-item label="系统位数">x64</el-descriptions-item>
      <el-descriptions-item label="当前环境">{{
        mode_env
      }}</el-descriptions-item>
      <el-descriptions-item label="当前浏览文件夹"><a href="">{{
        currentPreviewFolder
          }}</a></el-descriptions-item>
      <el-descriptions-item label="当前保存文件夹">{{
        currentSaveFolder
      }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<style lang="scss" scoped>
.system_info_container {
  padding-left: 10%;

  .el-image {
    width: 90px;
    margin-right: 20px;
  }

  .info_content {
    margin-top: 12px;
  }
}
</style>
