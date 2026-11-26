<script setup>
import {
  Database,
  FileText,
  Fingerprint,
  LayoutDashboard,
  LogOut,
  Send,
} from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const isLogin = computed(() => route.path === '/login')
const roleLabel = computed(
  () => ({ admin: '管理员', leader: '组长', member: '成员' })[auth.role] || auth.role,
)

const items = computed(() =>
  [
    { to: '/', label: '工作台', icon: LayoutDashboard },
    { to: '/reports', label: '日报', icon: FileText },
    { to: '/sources', label: '数据源', icon: Database, roles: ['admin', 'leader'] },
    {
      to: '/identities',
      label: '身份绑定',
      icon: Fingerprint,
      roles: ['admin', 'leader'],
    },
    { to: '/push', label: '推送记录', icon: Send, roles: ['admin', 'leader'] },
  ].filter((item) => !item.roles || item.roles.includes(auth.role)),
)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div v-if="isLogin" class="login-shell">
    <RouterView />
  </div>

  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-mark">DR</span>
        <div>
          <strong>智能日报</strong>
          <small>v2 · Superpowers</small>
        </div>
      </div>

      <nav class="sidebar-nav" aria-label="主导航">
        <RouterLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="nav-link"
        >
          <component :is="item.icon" :size="17" :stroke-width="1.6" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-user">
        <div class="user-meta">
          <strong>{{ auth.user?.username }}</strong>
          <span>{{ roleLabel }}</span>
        </div>
        <button class="icon-btn" title="退出登录" @click="logout">
          <LogOut :size="16" :stroke-width="1.6" />
        </button>
      </div>
    </aside>

    <main class="workspace">
      <RouterView />
    </main>
  </div>
</template>
