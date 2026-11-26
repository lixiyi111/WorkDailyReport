<script setup>
import {
  Clock3,
  FileText,
  LayoutDashboard,
  ListTree,
  Plug,
  ScrollText,
  Send,
  Settings as SettingsIcon,
  Users,
} from '@lucide/vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const nav = [
  { to: '/', label: '工作台', icon: LayoutDashboard },
  { to: '/sources', label: '数据源', icon: Plug },
  { to: '/records', label: '工作数据', icon: ListTree },
  { to: '/reports', label: '日报', icon: FileText },
  { to: '/members', label: '成员', icon: Users },
  { to: '/push', label: '推送', icon: Send },
  { to: '/runs', label: '运行日志', icon: ScrollText },
  { to: '/attendance', label: '考勤', icon: Clock3 },
  { to: '/settings', label: '设置', icon: SettingsIcon },
]

const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to))
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">
        <span class="brand-dot" aria-hidden="true"></span>
        <span class="brand-word">智能日报</span>
      </RouterLink>
      <p class="sidebar-sub">团队日报自动化</p>
      <nav class="side-nav" aria-label="主导航">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          :class="{ 'is-active': isActive(item.to) }"
        >
          <component :is="item.icon" :size="16" :stroke-width="1.5" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="sidebar-foot">v1 · SDD</div>
    </aside>

    <div class="app-content">
      <main class="app-main">
        <RouterView />
      </main>
      <footer class="app-footer">FastAPI + Vue 3 · v1 (SDD)</footer>
    </div>
  </div>
</template>
