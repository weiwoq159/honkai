<script setup lang="ts">
import { ref } from 'vue'
const rand = Math.floor(Math.random() * 7) + 1

const bgUrl = new URL(`../../assets/images/background${rand}.jpg`, import.meta.url).href

const mode_env = import.meta.env.VITE_USER_NODE_ENV
const currentPreviewFolder = ref(localStorage.getItem('Stars_currentPage') ?? '\\')
const currentSaveFolder = ref(localStorage.getItem('Stars_currentSavePage') ?? '\\')
</script>

<template>
  <div class="fnn-banner" :style="{ backgroundImage: `url(${bgUrl})` }"></div>
  <el-descriptions class="margin-top" :column="3" :size="`default`" border>
    <el-descriptions-item>
      <template #label>
        <div class="cell-item">
          <el-icon>
            <user />
          </el-icon>
          语言
        </div>
      </template>
      中文简体
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label>
        <div class="cell-item">
          <el-icon>
            <user />
          </el-icon>
          当前环境
        </div>
      </template>
      {{ mode_env }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label>
        <div class="cell-item">
          <el-icon>
            <iphone />
          </el-icon>
          当前浏览文件夹
        </div>
      </template>
      {{ currentPreviewFolder }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label>
        <div class="cell-item">
          <el-icon>
            <location />
          </el-icon>
          当前保存文件夹
        </div>
      </template>
      {{ currentSaveFolder }}
    </el-descriptions-item>
  </el-descriptions>
</template>

<style lang="scss" scoped>
.fnn-banner {
  width: calc(100% + 48px);
  height: 800px;
  margin: -24px -24px 0 -24px;
  background-size: cover;
  background-position: 0 -80px;
  transition: background-position 0.2s ease;
  background-repeat: no-repeat;
}
.el-image {
  height: 100%;
  width: 100%;
}
.el-descriptions {
  margin-top: 20px;
}
</style>
