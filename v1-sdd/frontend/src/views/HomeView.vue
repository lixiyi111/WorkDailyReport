<script setup>
import {
  ArrowRight,
  FileText,
  GitCommitHorizontal,
  ListChecks,
  ListTree,
} from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import client from '../api/client'

const SOURCE_META = {
  github: { name: 'GitHub', desc: '提交与 PR' },
  feishu: { name: '飞书', desc: '任务与群消息' },
  smtp: { name: '邮件', desc: '日报推送' },
}

const now = new Date()
const pad = (value) => String(value).padStart(2, '0')
const isoDate = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
const dateLabel = `${new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
}).format(now)} ${new Intl.DateTimeFormat('zh-CN', { weekday: 'long' }).format(now)}`

const loading = ref(true)
const error = ref('')
const health = ref(null)
const reports = ref([])
const dashboard = ref(null)

const latestTeam = computed(
  () => reports.value.find((report) => report.report_type === 'team') ?? null,
)

const stats = computed(() => {
  const work = dashboard.value?.work_records ?? {}
  const reportStatus = dashboard.value?.report_status ?? {}
  const todayReports =
    (reportStatus.personal?.total ?? 0) + (reportStatus.team?.total ?? 0)
  return [
    { label: '今日记录', value: work.total ?? 0, meta: '采集总量', icon: ListTree },
    {
      label: '今日提交',
      value: work.commits ?? 0,
      meta: 'GitHub',
      icon: GitCommitHorizontal,
    },
    { label: '今日任务', value: work.tasks ?? 0, meta: '飞书', icon: ListChecks },
    { label: '今日日报', value: todayReports, meta: '个人 + 团队', icon: FileText },
  ]
})

const taskStatus = computed(() => dashboard.value?.task_status ?? {})

const recentReports = computed(() => reports.value.slice(0, 5))

const previewText = computed(() => {
  const text = latestTeam.value?.content_md ?? ''
  const section = text.split('## 成员摘要')[1]?.split('##')[0] ?? text
  return section
    .replace(/^#.*$/gm, '')
    .replace(/^[-*]\s*/gm, '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 3)
    .join(' · ')
})

const sources = computed(() => {
  if (!health.value) return []
  return Object.entries(health.value.credentials).map(([key, ready]) => {
    const meta = SOURCE_META[key] ?? { name: key, desc: '' }
    const desc =
      key === 'feishu' && health.value.feishu_mode === 'mock'
        ? `${meta.desc} · Mock`
        : meta.desc
    return { key, ready, name: meta.name, desc }
  })
})

const connectionLabel = computed(() => {
  if (loading.value) return '正在检测'
  if (error.value) return '连接失败'
  return '后端在线'
})

const typeLabel = (type) => (type === 'team' ? '团队日报' : '个人日报')
const statusLabel = (status) =>
  ({ generated: '已生成', published: '已发布', draft: '草稿' })[status] ?? status

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [healthResponse, reportsResponse, dashboardResponse] = await Promise.all([
      client.get('/health'),
      client.get('/reports'),
      client.get('/dashboard'),
    ])
    health.value = healthResponse.data
    reports.value = reportsResponse.data
    dashboard.value = dashboardResponse.data
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
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>当日</p>
      <h1 class="page-title"><time :datetime="isoDate">{{ dateLabel }}</time></h1>
      <p class="page-sub">团队工作概览 · 数据源、日报与最近活动</p>
    </header>

    <p v-if="loading" class="state-line span-all">正在加载工作台</p>
    <p v-else-if="error" class="error span-all">{{ error }}</p>
    <template v-else>
      <div class="stat-row">
        <div v-for="stat in stats" :key="stat.label" class="stat-tile">
          <div class="stat-head">
            <component :is="stat.icon" :size="16" :stroke-width="1.5" />
            <span>{{ stat.label }}</span>
          </div>
          <div class="stat-value mono">{{ stat.value }}</div>
          <div class="stat-meta">{{ stat.meta }}</div>
        </div>
      </div>

      <div class="task-strip">
        <span class="task-strip-label">今日任务状态</span>
        <span class="tag">完成 {{ taskStatus.done ?? 0 }}</span>
        <span class="tag">进行中 {{ taskStatus.in_progress ?? 0 }}</span>
        <span class="tag">阻塞 {{ taskStatus.blocked ?? 0 }}</span>
      </div>

      <RouterLink v-if="latestTeam" :to="`/reports/${latestTeam.id}`" class="card report-preview">
        <div class="preview-head">
          <div>
            <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>最新团队日报</p>
            <h2 class="preview-title">{{ latestTeam.report_date }} · 团队日报</h2>
          </div>
          <span class="report-status">
            <span
              class="status-dot"
              :class="latestTeam.status === 'draft' ? 'is-missing' : 'is-ready'"
              aria-hidden="true"
            ></span>
            {{ statusLabel(latestTeam.status) }}
          </span>
        </div>
        <div class="preview-stats mono">
          <span>{{ latestTeam.summary?.members ?? 0 }} 人</span>
          <span>{{ latestTeam.summary?.commits ?? 0 }} 提交</span>
          <span>{{ latestTeam.summary?.tasks ?? 0 }} 任务</span>
          <span>{{ latestTeam.summary?.messages ?? 0 }} 消息</span>
        </div>
        <p class="preview-excerpt">{{ previewText }}</p>
        <span class="preview-cta">阅读全文 <ArrowRight :size="14" :stroke-width="1.5" /></span>
      </RouterLink>

      <section v-else class="card report-preview empty-preview">
        <p class="muted">还没有团队日报</p>
        <RouterLink class="text-link" to="/reports">查看日报</RouterLink>
      </section>

      <section class="card card--sources" aria-labelledby="sources-title">
        <header class="card-head">
          <div>
            <h2 id="sources-title" class="card-title">数据源</h2>
            <p class="card-sub">
              {{ connectionLabel }}
              <template v-if="health"> · <span class="mono">{{ health.app_env }}</span></template>
            </p>
          </div>
          <button class="btn" @click="load">重新检测</button>
        </header>
        <ul class="source-list">
          <li v-for="source in sources" :key="source.key" class="source-row">
            <div class="source-main">
              <span class="source-name">{{ source.name }}</span>
              <span class="source-desc">{{ source.desc }}</span>
            </div>
            <span class="source-state">
              <span
                class="status-dot"
                :class="source.ready ? 'is-ready' : 'is-missing'"
                aria-hidden="true"
              ></span>
              <span class="mono">{{ source.ready ? '已配置' : '未配置' }}</span>
            </span>
          </li>
        </ul>
        <p class="source-note">「已配置」表示环境变量已填写，实际连通性以采集结果为准</p>
      </section>

      <section class="card recent-card" aria-labelledby="recent-title">
        <header class="card-head">
          <div>
            <h2 id="recent-title" class="card-title">最近日报</h2>
            <p class="card-sub">最近 5 份</p>
          </div>
          <RouterLink class="text-link" to="/reports">查看全部</RouterLink>
        </header>
        <ul class="report-list">
          <li v-for="report in recentReports" :key="report.id" class="report-row">
            <RouterLink :to="`/reports/${report.id}`" class="report-link">
              <div class="report-main">
                <span class="report-date mono">{{ report.report_date }}</span>
                <span class="report-title">
                  {{ report.member_name ? `${report.member_name} · ` : '' }}{{ typeLabel(report.report_type) }}
                </span>
              </div>
              <div class="report-side">
                <span class="report-status">
                  <span
                    class="status-dot"
                    :class="report.status === 'draft' ? 'is-missing' : 'is-ready'"
                    aria-hidden="true"
                  ></span>
                  {{ statusLabel(report.status) }}
                </span>
                <span class="mono report-version">v{{ report.current_version }}</span>
              </div>
            </RouterLink>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
