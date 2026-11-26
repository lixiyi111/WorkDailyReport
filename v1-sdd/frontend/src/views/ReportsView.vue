<script setup>
import { ArrowRight, FileText, Pencil, Play, User, Users } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import client from '../api/client'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const canManage = computed(() => ['admin', 'leader'].includes(auth.role))
const loading = ref(true)
const error = ref('')
const reports = ref([])
const typeFilter = ref('all')
const dateFilter = ref('')
const generateDate = ref(new Date().toISOString().slice(0, 10))
const generating = ref(false)
const notice = ref('')

const filtered = computed(() =>
  reports.value.filter((report) => {
    if (typeFilter.value !== 'all' && report.report_type !== typeFilter.value) return false
    if (dateFilter.value && report.report_date !== dateFilter.value) return false
    return true
  }),
)

const summaryStats = computed(() => [
  { label: '全部', value: reports.value.length, icon: FileText },
  {
    label: '团队',
    value: reports.value.filter((report) => report.report_type === 'team').length,
    icon: Users,
  },
  {
    label: '个人',
    value: reports.value.filter((report) => report.report_type === 'personal').length,
    icon: User,
  },
  {
    label: '草稿',
    value: reports.value.filter((report) => report.status === 'draft').length,
    icon: Pencil,
  },
])

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

async function generateReports() {
  generating.value = true
  notice.value = ''
  try {
    const { data } = await client.post('/reports/generate', {
      report_date: generateDate.value,
      demo: false,
      push: false,
    })
    notice.value = `生成完成：${data.personal_reports} 份个人日报，${data.items} 条条目`
    await loadReports()
  } catch {
    notice.value = '生成失败，请检查数据源配置'
  } finally {
    generating.value = false
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

    <div v-if="canManage" class="toolbar">
      <label class="field field--inline">
        <span>日报日期</span>
        <input v-model="generateDate" type="date" class="input" />
      </label>
      <button class="btn" :disabled="generating" @click="generateReports">
        <Play :size="14" :stroke-width="1.5" />
        {{ generating ? '生成中' : '生成日报' }}
      </button>
      <span v-if="notice" class="saved-note">{{ notice }}</span>
      <span class="muted">生成不会自动推送</span>
    </div>

    <div class="stat-row">
      <div v-for="stat in summaryStats" :key="stat.label" class="stat-tile">
        <div class="stat-head">
          <component :is="stat.icon" :size="16" :stroke-width="1.5" />
          <span>{{ stat.label }}</span>
        </div>
        <div class="stat-value mono">{{ stat.value }}</div>
      </div>
    </div>

    <section class="card report-card" aria-labelledby="reports-title">
      <header class="card-head">
        <div>
          <h2 id="reports-title" class="card-title">全部日报</h2>
          <p class="card-sub">{{ filtered.length }} 份</p>
        </div>
        <div class="filters">
          <div class="segmented" role="group" aria-label="按类型筛选">
            <button
              :class="{ active: typeFilter === 'all' }"
              @click="typeFilter = 'all'"
            >
              全部
            </button>
            <button
              :class="{ active: typeFilter === 'team' }"
              @click="typeFilter = 'team'"
            >
              团队
            </button>
            <button
              :class="{ active: typeFilter === 'personal' }"
              @click="typeFilter = 'personal'"
            >
              个人
            </button>
          </div>
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
                <div class="report-title-line">
                  <span class="report-icon">
                    <component
                      :is="report.report_type === 'team' ? Users : User"
                      :size="15"
                      :stroke-width="1.5"
                    />
                  </span>
                  <span class="report-title">
                    {{ report.member_name ? `${report.member_name} · ` : '' }}{{ typeLabel(report.report_type) }}
                  </span>
                </div>
                <span class="report-meta">{{ report.report_date }} · {{ summaryLine(report) }}</span>
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
                <ArrowRight :size="16" :stroke-width="1.5" class="report-arrow" />
              </div>
            </RouterLink>
          </li>
        </ul>
        <p v-else class="state-line">没有匹配的日报</p>
      </template>
    </section>
  </div>
</template>
