<script setup>
import { RotateCcw } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const notice = ref('')
const runs = ref([])

const formatTime = (value) => (value ? value.replace('T', ' ').slice(0, 19) : '—')
const statusLabel = (status) =>
  ({ running: '运行中', success: '成功', partial: '部分成功', failed: '失败' })[status] ?? status

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/runs')
    runs.value = data
  } catch {
    error.value = '无法加载运行记录'
  } finally {
    loading.value = false
  }
}

async function retry(run) {
  notice.value = ''
  try {
    const { data } = await client.post(`/runs/${run.id}/retry`)
    notice.value = `重跑完成：采集 ${JSON.stringify(data.collected)}`
    await load()
  } catch {
    notice.value = '重跑失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>运行日志</p>
      <h1 class="page-title">运行日志</h1>
      <p class="page-sub">采集、生成与推送任务执行记录</p>
    </header>

    <p v-if="notice" class="saved-note span-all">{{ notice }}</p>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">最近运行</h2>
          <p class="card-sub">{{ runs.length }} 条</p>
        </div>
        <button class="btn" @click="load">刷新</button>
      </header>
      <p v-if="loading" class="state-line">正在加载运行记录</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>类型</th>
              <th>状态</th>
              <th>开始</th>
              <th>结束</th>
              <th>记录数</th>
              <th>错误</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="run in runs" :key="run.id">
              <td class="mono">#{{ run.id }}</td>
              <td>{{ run.run_type }}</td>
              <td><span class="tag">{{ statusLabel(run.status) }}</span></td>
              <td class="mono">{{ formatTime(run.started_at) }}</td>
              <td class="mono">{{ formatTime(run.finished_at) }}</td>
              <td>{{ run.records_count }}</td>
              <td class="record-detail">{{ run.error_message || '—' }}</td>
              <td><button class="btn btn--small" @click="retry(run)"><RotateCcw :size="13" :stroke-width="1.5" />重跑</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
