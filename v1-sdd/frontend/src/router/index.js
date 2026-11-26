import { createRouter, createWebHistory } from 'vue-router'

import AttendanceView from '../views/AttendanceView.vue'
import HomeView from '../views/HomeView.vue'
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
    { path: '/', name: 'home', component: HomeView, meta: { title: '工作台' } },
    { path: '/sources', name: 'sources', component: SourcesView, meta: { title: '数据源' } },
    { path: '/records', name: 'records', component: RecordsView, meta: { title: '工作数据' } },
    { path: '/reports', name: 'reports', component: ReportsView, meta: { title: '日报' } },
    {
      path: '/reports/:id',
      name: 'report-detail',
      component: ReportDetailView,
      props: true,
      meta: { title: '日报详情' },
    },
    { path: '/members', name: 'members', component: MembersView, meta: { title: '成员' } },
    { path: '/push', name: 'push', component: PushView, meta: { title: '推送' } },
    { path: '/runs', name: 'runs', component: RunsView, meta: { title: '运行日志' } },
    {
      path: '/attendance',
      name: 'attendance',
      component: AttendanceView,
      meta: { title: '考勤' },
    },
    { path: '/settings', name: 'settings', component: SettingsView, meta: { title: '设置' } },
  ],
})

export default router
