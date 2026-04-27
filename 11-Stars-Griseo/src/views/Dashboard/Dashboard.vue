<script setup lang="ts">
import { ElCol, ElRow } from "element-plus";
import SystemInfo from "./components/SystemInfo.vue";
import UtilsList from "./components/UtilsList.vue";
</script>

<template>
  <div class="dashboard-container">
    <div class="info_content">
      <ElImage src="/Stars.avif" />
      <el-text tag="b" size="large">欢迎来到空梦</el-text>
    </div>
    <ElRow :gutter="20">
      <el-col :span="12" class="dashboard_left">
        <SystemInfo></SystemInfo>
      </el-col>
      <el-col :span="12">
        <UtilsList />
      </el-col>
    </ElRow>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-container {
  height: 100%;
  overflow: hidden;
}

.el-image {
  width: 90px;
  margin-right: 20px;
}

.info_content {
  margin-top: 12px;
  margin-left: 5%;
}
</style>
