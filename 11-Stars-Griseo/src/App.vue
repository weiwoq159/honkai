<script setup lang="ts">
</script>

<template>
  <el-container>
    <el-header>
      <PardofelisHeader></PardofelisHeader>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style scoped>
.el-container {
  width: 100%;
  height: 100%;
  background: #000;
}

.el-header {
  padding: 10px;
  padding-left: 20px;
}
</style>
