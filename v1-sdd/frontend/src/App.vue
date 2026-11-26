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
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const allRoles = ['admin', 'leader', 'member']
const managerRoles = ['admin', 'leader']

const nav = [
  { to: '/', label: '工作台', icon: LayoutDashboard, roles: allRoles },
  { to: '/sources', label: '数据源', icon: Plug, roles: managerRoles },
  { to: '/records', label: '工作数据', icon: ListTree, roles: managerRoles },
  { to: '/reports', label: '日报', icon: FileText, roles: allRoles },
  { to: '/members', label: '成员', icon: Users, roles: managerRoles },
  { to: '/push', label: '推送', icon: Send, roles: managerRoles },
  { to: '/runs', label: '运行日志', icon: ScrollText, roles: managerRoles },
  { to: '/attendance', label: '考勤', icon: Clock3, roles: allRoles },
  { to: '/settings', label: '设置', icon: SettingsIcon, roles: ['admin'] },
]

const ROLE_LABEL = { admin: '管理员', leader: '组长', member: '成员' }

const visibleNav = computed(() =>
  auth.user ? nav.filter((item) => item.roles.includes(auth.role)) : [],
)

const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to))

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <RouterView v-if="route.path === '/login'" />

  <div v-else class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">
        <span class="brand-dot" aria-hidden="true"></span>
        <span class="brand-word">智能日报</span>
      </RouterLink>
      <p class="sidebar-sub">团队日报自动化</p>
      <nav class="side-nav" aria-label="主导航">
        <RouterLink
          v-for="item in visibleNav"
          :key="item.to"
          :to="item.to"
          :class="{ 'is-active': isActive(item.to) }"
        >
          <component :is="item.icon" :size="16" :stroke-width="1.5" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="sidebar-foot">
        <div class="sidebar-user">
          {{ auth.user?.username }}
          <span class="muted">· {{ ROLE_LABEL[auth.role] || auth.role }}</span>
        </div>
        <button class="sidebar-logout" @click="logout">退出登录</button>
        <span class="sidebar-version">v1 · SDD</span>
      </div>
    </aside>

    <div class="app-content">
      <main class="app-main">
        <RouterView />
      </main>
      <footer class="app-footer">FastAPI + Vue 3 · v1 (SDD)</footer>
    </div>
  </div>
</template>
