<script setup>
import { GitCommitHorizontal, Mail, MessagesSquare, Play, RotateCw, Save } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'

import client from '../api/client'

const ICONS = { github: GitCommitHorizontal, feishu: MessagesSquare, smtp: Mail }
const META = {
  github: { name: 'GitHub', desc: '提交与 PR 数据源' },
  feishu: { name: '飞书', desc: '任务与群消息数据源' },
  smtp: { name: '邮件', desc: '日报推送通道' },
}

const today = () => new Date().toISOString().slice(0, 10)
const split = (value) => (value || '').split(',').map((item) => item.trim()).filter(Boolean)

const loading = ref(true)
const error = ref('')
const sources = ref([])
const forms = reactive({})
const notice = ref({})
const collectDate = ref(today())

function hydrate(rows) {
  sources.value = rows
  rows.forEach((row) => {
    const config = row.config || {}
    forms[row.source] = {
      enabled: row.enabled,
      repos: (config.repos || []).join(', '),
      chat_ids: (config.chat_ids || []).join(', '),
      base_url: config.base_url || 'https://open.feishu.cn',
      recipients: (config.recipients || []).join(', '),
    }
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/sources')
    hydrate(data)
  } catch {
    error.value = '无法加载数据源配置'
  } finally {
    loading.value = false
  }
}

function configFor(source) {
  const form = forms[source]
  if (source === 'github') return { repos: split(form.repos) }
  if (source === 'feishu') return { chat_ids: split(form.chat_ids), base_url: form.base_url }
  return { recipients: split(form.recipients) }
}

async function save(source) {
  try {
    await client.put(`/sources/${source}`, {
      enabled: forms[source].enabled,
      config: configFor(source),
    })
    notice.value[source] = '已保存'
    await load()
  } catch {
    notice.value[source] = '保存失败'
  }
}

async function test(source) {
  try {
    const { data } = await client.post(`/sources/${source}/test`)
    notice.value[source] = data.ok ? '连接正常' : data.message || '连接失败'
  } catch {
    notice.value[source] = '测试失败'
  }
}

async function collect(source) {
  try {
    const { data } = await client.post(`/sources/${source}/collect`, {
      date: collectDate.value,
    })
    notice.value[source] = `采集完成：${JSON.stringify(data.collected)}，错误 ${data.errors.length} 条`
    await load()
  } catch {
    notice.value[source] = '采集失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>数据源</p>
      <h1 class="page-title">数据源管理</h1>
      <p class="page-sub">配置采集范围、测试连接、手动触发采集</p>
    </header>

    <div class="toolbar span-all">
      <label class="field field--inline">
        <span>采集日期</span>
        <input v-model="collectDate" type="date" class="input" />
      </label>
      <span class="muted">Token / Secret / 授权码仍由 `.env` 管理，不在页面保存</span>
      <button class="btn" @click="load">刷新</button>
    </div>

    <p v-if="loading" class="state-line span-all">正在加载数据源</p>
    <p v-else-if="error" class="error span-all">{{ error }}</p>
    <div v-else class="source-grid">
      <article v-for="source in sources" :key="source.source" class="card source-card">
        <header class="source-card-head">
          <span class="source-card-icon">
            <component :is="ICONS[source.source]" :size="18" :stroke-width="1.5" />
          </span>
          <div class="source-card-title">
            <h2 class="card-title">{{ META[source.source]?.name || source.source }}</h2>
            <p class="card-sub">{{ META[source.source]?.desc }}</p>
          </div>
          <span class="report-status">
            <span
              class="status-dot"
              :class="source.configured ? 'is-ready' : 'is-missing'"
              aria-hidden="true"
            ></span>
            {{ source.configured ? '已配置' : '未配置' }}
          </span>
        </header>

        <div v-if="forms[source.source]" class="source-fields">
          <label v-if="source.source === 'github'" class="field">
            <span>仓库（owner/repo，逗号分隔）</span>
            <input v-model="forms[source.source].repos" class="input" placeholder="team/repo-a, team/repo-b" />
          </label>
          <template v-if="source.source === 'feishu'">
            <label class="field">
              <span>群 chat_id（逗号分隔）</span>
              <input v-model="forms[source.source].chat_ids" class="input" placeholder="oc_xxx, oc_yyy" />
            </label>
            <label class="field">
              <span>API Base URL</span>
              <input v-model="forms[source.source].base_url" class="input" />
            </label>
          </template>
          <label v-if="source.source === 'smtp'" class="field">
            <span>收件人（逗号分隔）</span>
            <input v-model="forms[source.source].recipients" class="input" placeholder="a@example.com, b@example.com" />
          </label>
          <label class="check">
            <input v-model="forms[source.source].enabled" type="checkbox" />
            启用该数据源
          </label>
        </div>

        <div class="card-actions">
          <button class="btn" @click="save(source.source)"><Save :size="14" :stroke-width="1.5" />保存</button>
          <button class="btn" @click="test(source.source)"><RotateCw :size="14" :stroke-width="1.5" />测试连接</button>
          <button class="btn" @click="collect(source.source)"><Play :size="14" :stroke-width="1.5" />采集</button>
        </div>

        <p v-if="notice[source.source]" class="saved-note">{{ notice[source.source] }}</p>
        <p class="source-meta mono">
          最近运行：{{ source.last_run_at || '—' }} · {{ source.last_status || '未运行' }}
        </p>
        <p v-if="source.last_error" class="error">{{ source.last_error }}</p>
      </article>
    </div>
  </div>
</template>
