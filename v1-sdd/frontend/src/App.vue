<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="brand" to="/">
        <span class="brand-dot" aria-hidden="true"></span>
        <span class="brand-word">智能日报</span>
        <span class="brand-sub">团队日报自动化</span>
      </RouterLink>
      <nav class="app-nav" aria-label="主导航">
        <RouterLink to="/">首页</RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <span>FastAPI + Vue 3 · v1 (SDD)</span>
    </footer>
  </div>
</template>
