<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const reports = ref([])
const typeFilter = ref('all')
const dateFilter = ref('')

const filtered = computed(() =>
  reports.value.filter((report) => {
    if (typeFilter.value !== 'all' && report.report_type !== typeFilter.value) return false
    if (dateFilter.value && report.report_date !== dateFilter.value) return false
    return true
  }),
)

const typeLabel = (type) => (type === 'team' ? '团队日报' : '个人日报')
const statusLabel = (status) =>
  ({ generated: '已生成', published: '已发布', draft: '草稿' })[status] ?? status

function summaryLine(report) {
  const summary = report.summary ?? {}
  if (report.report_type === 'team') {
    return `${summary.members ?? 0} 人 · ${summary.commits ?? 0} 提交 · ${summary.tasks ?? 0} 任务`
  }
  return `${summary.commits ?? 0} 提交 · ${summary.tasks ?? 0} 任务 · ${summary.messages ?? 0} 消息`
}

async function loadReports() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/reports')
    reports.value = data
  } catch {
    error.value = '无法加载日报，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}

onMounted(loadReports)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>日报</p>
      <h1 class="page-title">日报记录</h1>
      <p class="page-sub">按日期查看团队与成员日报</p>
    </header>

    <section class="card report-card" aria-labelledby="reports-title">
      <header class="card-head">
        <div>
          <h2 id="reports-title" class="card-title">全部日报</h2>
          <p class="card-sub">{{ filtered.length }} 份</p>
        </div>
        <div class="filters">
          <select v-model="typeFilter" class="select" aria-label="按类型筛选">
            <option value="all">全部类型</option>
            <option value="team">团队日报</option>
            <option value="personal">个人日报</option>
          </select>
          <input v-model="dateFilter" class="select" type="date" aria-label="按日期筛选" />
        </div>
      </header>

      <p v-if="loading" class="state-line">正在加载日报</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <template v-else>
        <ul v-if="filtered.length" class="report-list">
          <li v-for="report in filtered" :key="report.id" class="report-row">
            <RouterLink :to="`/reports/${report.id}`" class="report-link">
              <div class="report-main">
                <span class="report-date mono">{{ report.report_date }}</span>
                <span class="report-title">
                  {{ report.member_name ? `${report.member_name} · ` : '' }}{{ typeLabel(report.report_type) }}
                </span>
                <span class="report-meta">{{ summaryLine(report) }}</span>
              </div>
              <div class="report-side">
                <span class="report-status">
                  <span
                    class="status-dot"
                    :class="report.status === 'draft' ? 'is-missing' : 'is-ready'"
                    aria-hidden="true"
                  ></span>
                  <span>{{ statusLabel(report.status) }}</span>
                </span>
                <span class="mono report-version">v{{ report.current_version }}</span>
              </div>
            </RouterLink>
          </li>
        </ul>
        <p v-else class="state-line">没有匹配的日报</p>
      </template>
    </section>
  </div>
</template>
