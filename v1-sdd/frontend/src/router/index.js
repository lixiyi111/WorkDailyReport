import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import ReportDetailView from '../views/ReportDetailView.vue'
import ReportsView from '../views/ReportsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页' },
    },
    {
      path: '/reports',
      name: 'reports',
      component: ReportsView,
      meta: { title: '日报' },
    },
    {
      path: '/reports/:id',
      name: 'report-detail',
      component: ReportDetailView,
      props: true,
      meta: { title: '日报详情' },
    },
  ],
})

export default router
