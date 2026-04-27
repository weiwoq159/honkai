<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
const route = useRoute()
const breadcrumbName = computed(() => {
  return {
    title: route.meta?.title || route.name || '首页',
    url: route.fullPath,
  }
})
</script>

<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item>
      <a href="/">首页</a>
    </el-breadcrumb-item>
    <el-breadcrumb-item>
      <a :href="breadcrumbName.url">{{ breadcrumbName.title }}</a>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<style lang="scss" scoped>
.el-header {
  -webkit-app-region: drag;
}
.el-breadcrumb-item {
  cursor: pointer;
}
</style>
