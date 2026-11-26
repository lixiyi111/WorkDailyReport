<script setup>
import { RouterLink, RouterView } from 'vue-router'

const title = '智能日报生成器 · v1 · SDD'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark">DR</span>
        <div>
          <h1>{{ title }}</h1>
          <p class="muted">规范驱动开发 · 基础骨架</p>
        </div>
      </div>
      <nav class="app-nav">
        <RouterLink to="/">首页</RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <span class="muted">FastAPI + Vue 3 · 具体业务功能待按规范实现</span>
    </footer>
  </div>
</template>
