<script setup>
import {
  ArrowLeft,
  CalendarDays,
  CircleDot,
  Download,
  GitCommitHorizontal,
  Hash,
  ListChecks,
  MessagesSquare,
  Pencil,
  Send,
  User,
  Users,
} from '@lucide/vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import client from '../api/client'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const report = ref(null)
const editing = ref(false)
const draft = ref('')
const saving = ref(false)
const saveError = ref('')
const savedNote = ref('')
const pushNote = ref('')

const rendered = computed(() => {
  if (!report.value?.content_md) return ''
  return DOMPurify.sanitize(marked.parse(report.value.content_md))
})

const heading = computed(() => {
  if (!report.value) return '日报详情'
  const label =
    report.value.report_type === 'team'
      ? '团队日报'
      : `${report.value.member_name || '成员'} 的个人日报`
  return `${report.value.report_date} · ${label}`
})

const typeLabel = computed(() =>
  report.value?.report_type === 'team' ? '团队日报' : '个人日报',
)

const statusLabel = computed(() => {
  const status = report.value?.status
  return ({ generated: '已生成', published: '已发布', draft: '草稿' })[status] ?? status ?? ''
})

const counts = computed(() => {
  const items = report.value?.items ?? []
  return {
    commit: items.filter((item) => item.category === 'commit').length,
    task: items.filter((item) => item.category === 'task').length,
    message: items.filter((item) => item.category === 'message').length,
  }
})

async function loadReport() {
  loading.value = true
  error.value = ''
  editing.value = false
  savedNote.value = ''
  try {
    const { data } = await client.get(`/reports/${route.params.id}`)
    report.value = data
    draft.value = data.content_md ?? ''
  } catch {
    error.value = '无法加载日报详情'
  } finally {
    loading.value = false
  }
}

function startEdit() {
  draft.value = report.value?.content_md ?? ''
  editing.value = true
  savedNote.value = ''
  saveError.value = ''
}

async function saveReport() {
  saving.value = true
  saveError.value = ''
  try {
    const { data } = await client.put(`/reports/${route.params.id}`, {
      content_md: draft.value,
      editor: 'web',
      change_note: '前端编辑',
    })
    report.value = { ...report.value, ...data }
    editing.value = false
    savedNote.value = `已保存，当前 v${data.current_version}`
  } catch {
    saveError.value = '保存失败，请稍后重试'
  } finally {
    saving.value = false
  }
}

async function pushReport() {
  pushNote.value = ''
  try {
    const { data } = await client.post(`/reports/${route.params.id}/push`, {
      channel: 'email',
    })
    pushNote.value = data.success ? '已发送邮件' : `推送失败：${data.error || '未知错误'}`
  } catch {
    pushNote.value = '推送失败'
  }
}

function exportReport() {
  if (!report.value) return
  const blob = new Blob([report.value.content_md], {
    type: 'text/markdown;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${report.value.report_date}-${report.value.report_type}.md`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(loadReport)
watch(() => route.params.id, loadReport)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker">
        <span class="brand-dot" aria-hidden="true"></span>
        <RouterLink to="/reports" class="crumb">日报</RouterLink>
      </p>
      <h1 class="page-title">{{ heading }}</h1>
      <p v-if="report" class="page-sub">
        {{ statusLabel }} · v{{ report.current_version }}
        <template v-if="report.member_name"> · {{ report.member_name }}</template>
      </p>
    </header>

    <section v-if="loading" class="card detail-state">
      <p class="state-line">正在加载日报</p>
    </section>
    <section v-else-if="error" class="card detail-state">
      <p class="error">{{ error }}</p>
    </section>
    <template v-else-if="report">
      <article class="card report-sheet">
        <header class="card-head">
          <div>
            <h2 class="card-title">日报正文</h2>
            <p class="card-sub">Markdown · 可手工修订</p>
          </div>
          <button v-if="!editing" class="btn" @click="startEdit">
            <Pencil :size="14" :stroke-width="1.5" />
            编辑
          </button>
        </header>

        <div v-if="!editing" class="markdown" v-html="rendered"></div>
        <div v-else class="editor">
          <textarea
            v-model="draft"
            class="textarea"
            rows="18"
            aria-label="日报 Markdown 内容"
          ></textarea>
          <div class="editor-actions">
            <button class="btn" :disabled="saving" @click="saveReport">
              {{ saving ? '保存中' : '保存' }}
            </button>
            <button class="btn btn--ghost" :disabled="saving" @click="editing = false">
              取消
            </button>
            <span v-if="saveError" class="error">{{ saveError }}</span>
          </div>
        </div>
        <p v-if="savedNote" class="saved-note">{{ savedNote }}</p>
      </article>

      <aside class="card report-aside">
        <h2 class="card-title">概览</h2>
        <dl class="meta-list">
          <div>
            <dt><CalendarDays :size="14" :stroke-width="1.5" />日期</dt>
            <dd class="mono">{{ report.report_date }}</dd>
          </div>
          <div>
            <dt>
              <component
                :is="report.report_type === 'team' ? Users : User"
                :size="14"
                :stroke-width="1.5"
              />
              类型
            </dt>
            <dd>{{ typeLabel }}</dd>
          </div>
          <div>
            <dt><User :size="14" :stroke-width="1.5" />成员</dt>
            <dd>{{ report.member_name || '全组' }}</dd>
          </div>
          <div>
            <dt><CircleDot :size="14" :stroke-width="1.5" />状态</dt>
            <dd>{{ statusLabel }}</dd>
          </div>
          <div>
            <dt><Hash :size="14" :stroke-width="1.5" />版本</dt>
            <dd class="mono">v{{ report.current_version }}</dd>
          </div>
        </dl>

        <h2 class="card-title aside-title">条目</h2>
        <ul class="count-list">
          <li>
            <GitCommitHorizontal :size="15" :stroke-width="1.5" />
            <span>提交</span>
            <span class="mono count">{{ counts.commit }}</span>
          </li>
          <li>
            <ListChecks :size="15" :stroke-width="1.5" />
            <span>任务</span>
            <span class="mono count">{{ counts.task }}</span>
          </li>
          <li>
            <MessagesSquare :size="15" :stroke-width="1.5" />
            <span>消息</span>
            <span class="mono count">{{ counts.message }}</span>
          </li>
        </ul>

        <div class="card-actions">
          <button class="btn" @click="pushReport"><Send :size="14" :stroke-width="1.5" />推送邮件</button>
          <button class="btn" @click="exportReport"><Download :size="14" :stroke-width="1.5" />导出</button>
        </div>
        <p v-if="pushNote" class="saved-note">{{ pushNote }}</p>

        <RouterLink class="text-link" to="/reports">
          <ArrowLeft :size="14" :stroke-width="1.5" />
          返回列表
        </RouterLink>
      </aside>

      <section class="card item-card" aria-labelledby="items-title">
        <h2 id="items-title" class="card-title">条目明细</h2>
        <ul v-if="report.items?.length" class="item-list">
          <li v-for="item in report.items" :key="item.id" class="item-row">
            <span class="item-cat mono">{{ item.category }}</span>
            <span class="item-title">{{ item.title }}</span>
            <span class="item-role mono">{{ item.attribution_role || '—' }}</span>
          </li>
        </ul>
        <p v-else class="state-line">暂无条目</p>
      </section>
    </template>
  </div>
</template>
