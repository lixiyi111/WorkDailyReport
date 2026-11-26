import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import IdentitiesView from '../views/IdentitiesView.vue'
import LoginView from '../views/LoginView.vue'
import PushView from '../views/PushView.vue'
import ReportDetailView from '../views/ReportDetailView.vue'
import ReportsView from '../views/ReportsView.vue'
import SourcesView from '../views/SourcesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { title: '登录' } },
    { path: '/', name: 'home', component: HomeView, meta: { title: '工作台' } },
    { path: '/reports', name: 'reports', component: ReportsView, meta: { title: '日报' } },
    {
      path: '/reports/:id',
      name: 'report-detail',
      component: ReportDetailView,
      meta: { title: '日报详情' },
    },
    {
      path: '/sources',
      name: 'sources',
      component: SourcesView,
      meta: { title: '数据源', roles: ['admin', 'leader'] },
    },
    {
      path: '/identities',
      name: 'identities',
      component: IdentitiesView,
      meta: { title: '身份绑定', roles: ['admin', 'leader'] },
    },
    {
      path: '/push',
      name: 'push',
      component: PushView,
      meta: { title: '推送记录', roles: ['admin', 'leader'] },
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('wdr2_token')
  if (to.path === '/login') {
    return token ? '/' : true
  }
  if (!token) {
    return '/login'
  }
  let user = null
  try {
    user = JSON.parse(localStorage.getItem('wdr2_user') || 'null')
  } catch {
    user = null
  }
  if (!user) {
    localStorage.removeItem('wdr2_token')
    return '/login'
  }
  if (to.meta.roles && !to.meta.roles.includes(user.role)) {
    return '/'
  }
  return true
})

export default router
