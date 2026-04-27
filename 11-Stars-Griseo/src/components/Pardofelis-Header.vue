<script setup lang="ts">
import { ElButton, ElImage } from "element-plus";
import { ArrowLeftBold } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
const router = useRouter();
const go_back = () => {
  router.push("/");
};
</script>

<template>
  <div class="header-container">
    <ElButton size="default" :icon="ArrowLeftBold" class="return_btn" :link="true" @click="go_back()"></ElButton>
    <ElImage src="/Stars.avif"></ElImage>
    <span class="header-title">空梦</span>
  </div>
</template>
<style lang="scss" scoped>
.header-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
}

.el-image {
  height: 100%;
  border-radius: 50%;
}

.header-title {
  margin-left: 12px;
}

.return_btn {
  margin-right: 20px;
  cursor: pointer;
  -webkit-app-region: no-drag;
}
</style>
