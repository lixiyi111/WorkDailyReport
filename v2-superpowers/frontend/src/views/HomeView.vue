<script setup>
import { ArrowRight, FileText, RefreshCw, User, Users } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import client from '../api/client'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const canManage = computed(() => ['admin', 'leader'].includes(auth.role))

const loading = ref(true)
const error = ref('')
const health = ref(null)
const reports = ref([])
const sources = ref([])

const stats = computed(() => [
  { label: '日报总数', value: reports.value.length, icon: FileText },
  {
    label: '团队日报',
    value: reports.value.filter((item) => item.report_type === 'team').length,
    icon: Users,
  },
  {
    label: '个人日报',
    value: reports.value.filter((item) => item.report_type === 'personal').length,
    icon: User,
  },
])

const recent = computed(() => reports.value.slice(0, 6))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [healthResponse, reportsResponse] = await Promise.all([
      client.get('/health'),
      client.get('/reports'),
    ])
    health.value = healthResponse.data
    reports.value = reportsResponse.data
    if (canManage.value) {
      const { data } = await client.get('/sources/status')
      sources.value = data
    }
  } catch {
    error.value = '无法加载工作台数据，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker">
        <span class="brand-dot" aria-hidden="true"></span>
        工作台
      </p>
      <h1 class="page-title">今天的工作，已经替你整理好了</h1>
      <p class="page-sub">采集 · 生成 · 推送，一条链路完成日报</p>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="stat-row">
      <div v-for="stat in stats" :key="stat.label" class="stat-tile">
        <div class="stat-head">
          <component :is="stat.icon" :size="16" :stroke-width="1.5" />
          <span>{{ stat.label }}</span>
        </div>
        <div class="stat-value mono">{{ loading ? '—' : stat.value }}</div>
      </div>
    </div>

    <div class="home-grid">
      <section class="card">
        <header class="card-head">
          <div>
            <h2 class="card-title">最近日报</h2>
            <p class="card-sub">按日期倒序</p>
          </div>
          <RouterLink to="/reports" class="text-link">
            全部 <ArrowRight :size="14" :stroke-width="1.6" />
          </RouterLink>
        </header>

        <p v-if="loading" class="state-line">正在加载</p>
        <ul v-else-if="recent.length" class="report-list">
          <li v-for="report in recent" :key="report.id" class="report-row">
            <RouterLink :to="`/reports/${report.id}`" class="report-link">
              <div class="report-main">
                <span class="report-title">
                  {{ report.member_name ? `${report.member_name} · ` : '' }}
                  {{ report.report_type === 'team' ? '团队日报' : '个人日报' }}
                </span>
                <span class="report-meta">{{ report.report_date }}</span>
              </div>
              <ArrowRight :size="16" :stroke-width="1.5" class="report-arrow" />
            </RouterLink>
          </li>
        </ul>
        <p v-else class="state-line">还没有日报，去日报页生成一份</p>
      </section>

      <section class="card">
        <header class="card-head">
          <div>
            <h2 class="card-title">服务状态</h2>
            <p class="card-sub">凭证只显示是否就绪</p>
          </div>
          <button class="btn btn--ghost" :disabled="loading" @click="load">
            <RefreshCw :size="14" :stroke-width="1.6" />
            刷新
          </button>
        </header>

        <ul v-if="health" class="kv-list">
          <li>
            <span>运行环境</span>
            <strong class="mono">{{ health.app_env }}</strong>
          </li>
          <li v-for="(ready, name) in health.credentials" :key="name">
            <span>{{ name }}</span>
            <span class="badge" :class="ready ? 'badge--on' : 'badge--off'">
              {{ ready ? '已就绪' : '未配置' }}
            </span>
          </li>
        </ul>

        <template v-if="canManage && sources.length">
          <h3 class="aside-title">数据源同步</h3>
          <ul class="kv-list">
            <li v-for="source in sources" :key="source.id">
              <span class="mono">{{ source.source }}</span>
              <span class="badge" :class="source.status === 'success' ? 'badge--on' : 'badge--off'">
                {{ source.status }}
              </span>
            </li>
          </ul>
        </template>
      </section>
    </div>
  </div>
</template>
