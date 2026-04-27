<script setup lang="ts">
import { Picture, Download } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
const router = useRouter();
const navigateToalbums = (url: string) => {
  router.push(url);
};
</script>

<template>
  <el-divider />
  <div class="Pardofelis_button_group">
    <el-button
      type="primary"
      :icon="Picture"
      @Click="navigateToalbums('/albums')"
      >本地相册</el-button
    >
    <el-button
      type="primary"
      :icon="Download"
      @Click="navigateToalbums('/crawler')"
      >下载图片</el-button
    >
    <el-button type="primary">本地相册</el-button>
    <el-button type="primary">本地相册</el-button>
  </div>
</template>

<style lang="scss" scoped></style>
