<script setup>
import { computed, onMounted, ref } from 'vue'

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

const connectionLabel = computed(() => {
  if (loading.value) return '正在检测'
  if (error.value) return '连接失败'
  return '后端在线'
})

const sources = computed(() => {
  if (!health.value) return []
  return Object.entries(health.value.credentials).map(([key, ready]) => ({
    key,
    ready,
    ...(SOURCE_META[key] ?? { name: key, desc: '' }),
  }))
})

async function loadHealth() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/health')
    health.value = data
  } catch {
    error.value = '无法连接后端服务，请确认 FastAPI 已在 8000 端口启动'
  } finally {
    loading.value = false
  }
}

onMounted(loadHealth)
</script>

<template>
  <div class="page">
  <header class="page-head">
    <p class="page-kicker">
      <span class="brand-dot" aria-hidden="true"></span>
      当日
    </p>
    <h1 class="page-title">
      <time :datetime="isoDate">{{ dateLabel }}</time>
    </h1>
    <p class="page-sub">数据源与推送状态</p>
  </header>

  <section class="card card--sources" aria-labelledby="sources-title">
    <header class="card-head">
      <div>
        <h2 id="sources-title" class="card-title">数据源</h2>
        <p class="card-sub">
          {{ connectionLabel }}
          <template v-if="health">
            · <span class="mono">{{ health.app_env }}</span>
          </template>
        </p>
      </div>
      <button class="btn" :disabled="loading" @click="loadHealth">
        {{ loading ? '检测中' : '重新检测' }}
      </button>
    </header>

    <p v-if="loading" class="state-line">正在检测后端连接</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <ul v-else class="source-list">
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
    <p v-if="!loading && !error" class="source-note">
      「已配置」表示环境变量已填写，实际连通性以采集结果为准
    </p>
  </section>

  <section class="card card--note" aria-labelledby="note-title">
    <h2 id="note-title" class="card-title">说明</h2>
    <p class="side-note">
      后端已实现采集、生成与推送链路。此页用于查看数据源与凭证状态。
    </p>
    <dl class="layer-list">
      <div>
        <dt>采集</dt>
        <dd>GitHub 提交 · 飞书任务与群消息</dd>
      </div>
      <div>
        <dt>生成</dt>
        <dd>个人日报 · 团队日报</dd>
      </div>
      <div>
        <dt>推送</dt>
        <dd>邮件 · 飞书机器人</dd>
      </div>
    </dl>
    <p class="side-foot">日报列表与编辑页尚未接入</p>
  </section>
  </div>
</template>
