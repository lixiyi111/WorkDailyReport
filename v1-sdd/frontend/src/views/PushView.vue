<script setup>
import { RotateCcw } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const notice = ref('')
const logs = ref([])

const formatTime = (value) => (value ? value.replace('T', ' ').slice(0, 16) : '—')
const statusLabel = (status) => ({ success: '成功', failed: '失败' })[status] ?? status

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/push-logs')
    logs.value = data
  } catch {
    error.value = '无法加载推送记录'
  } finally {
    loading.value = false
  }
}

async function retry(log) {
  notice.value = ''
  try {
    const { data } = await client.post(`/reports/${log.report_id}/push`, {
      channel: log.channel,
      target: log.target,
    })
    notice.value = data.success ? '重新推送成功' : `推送失败：${data.error || '未知错误'}`
    await load()
  } catch {
    notice.value = '重新推送失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>推送</p>
      <h1 class="page-title">推送管理</h1>
      <p class="page-sub">邮件与飞书机器人推送历史</p>
    </header>

    <p v-if="notice" class="saved-note span-all">{{ notice }}</p>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">推送记录</h2>
          <p class="card-sub">{{ logs.length }} 条</p>
        </div>
        <button class="btn" @click="load">刷新</button>
      </header>
      <p v-if="loading" class="state-line">正在加载推送记录</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>日报</th>
              <th>渠道</th>
              <th>目标</th>
              <th>状态</th>
              <th>尝试</th>
              <th>错误</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="mono">{{ formatTime(log.sent_at) }}</td>
              <td>#{{ log.report_id }}</td>
              <td>{{ log.channel }}</td>
              <td class="mono">{{ log.target }}</td>
              <td><span class="tag">{{ statusLabel(log.status) }}</span></td>
              <td>{{ log.attempt }}</td>
              <td class="record-detail">{{ log.error_message || '—' }}</td>
              <td><button class="btn btn--small" @click="retry(log)"><RotateCcw :size="13" :stroke-width="1.5" />重推</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
