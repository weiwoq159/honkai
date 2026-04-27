<script setup lang="ts"></script>

<template>
  <div class="fnn-app-container">
    <el-container>
      <el-aside width="200px" height="100vh">
        <FurinaNav />
      </el-aside>
      <el-container>
        <el-header>
          <FurinaHeader />
        </el-header>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped lang="scss"></style>
