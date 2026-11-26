import { createRouter, createWebHistory } from 'vue-router'

import AttendanceView from '../views/AttendanceView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import MembersView from '../views/MembersView.vue'
import PushView from '../views/PushView.vue'
import RecordsView from '../views/RecordsView.vue'
import ReportDetailView from '../views/ReportDetailView.vue'
import ReportsView from '../views/ReportsView.vue'
import RunsView from '../views/RunsView.vue'
import SettingsView from '../views/SettingsView.vue'
import SourcesView from '../views/SourcesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { title: '登录' } },
    { path: '/', name: 'home', component: HomeView, meta: { title: '工作台' } },
    {
      path: '/sources',
      name: 'sources',
      component: SourcesView,
      meta: { title: '数据源', roles: ['admin', 'leader'] },
    },
    {
      path: '/records',
      name: 'records',
      component: RecordsView,
      meta: { title: '工作数据', roles: ['admin', 'leader'] },
    },
    { path: '/reports', name: 'reports', component: ReportsView, meta: { title: '日报' } },
    {
      path: '/reports/:id',
      name: 'report-detail',
      component: ReportDetailView,
      props: true,
      meta: { title: '日报详情' },
    },
    {
      path: '/members',
      name: 'members',
      component: MembersView,
      meta: { title: '成员', roles: ['admin', 'leader'] },
    },
    {
      path: '/push',
      name: 'push',
      component: PushView,
      meta: { title: '推送', roles: ['admin', 'leader'] },
    },
    {
      path: '/runs',
      name: 'runs',
      component: RunsView,
      meta: { title: '运行日志', roles: ['admin', 'leader'] },
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: AttendanceView,
      meta: { title: '考勤' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { title: '设置', roles: ['admin'] },
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('wdr_token')
  if (to.path === '/login') {
    return token ? '/' : true
  }
  if (!token) {
    return '/login'
  }
  let user = null
  try {
    user = JSON.parse(localStorage.getItem('wdr_user') || 'null')
  } catch {
    user = null
  }
  if (!user) {
    localStorage.removeItem('wdr_token')
    return '/login'
  }
  if (to.meta.roles && !to.meta.roles.includes(user.role)) {
    return '/'
  }
  return true
})

export default router
