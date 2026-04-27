<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { routes } from '@routes/index'
const route = useRoute()
const router = useRouter()
const handleClickNavHomePage = () => {
  router.push('/')
}
</script>

<template>
  <div class="nav-title">
    <el-image src="/logo.png" fit="cover" @click="handleClickNavHomePage"></el-image>
    <el-text class="mx-1" type="primary">芙宁娜的糖果屋</el-text>
  </div>
  <el-menu :default-active="route.path" router>
    <el-menu-item
      :index="item.path"
      v-for="item in routes.filter((it) => it.path !== '/')"
      :key="item.name"
      >{{ item.name }}</el-menu-item
    >
  </el-menu>
</template>

<style lang="scss" scoped>
.nav-title {
  height: 60px;
  padding: 4px;
  padding-left: 10px;
  display: flex;

  .el-image {
    height: 60px;
    cursor: pointer;
  }
}
</style>
