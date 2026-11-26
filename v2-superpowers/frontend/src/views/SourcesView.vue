<script setup>
import { RefreshCw } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const rows = ref([])

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/sources/status')
    rows.value = data
  } catch {
    error.value = '无法加载数据源状态'
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
        数据源
      </p>
      <h1 class="page-title">数据源同步状态</h1>
      <p class="page-sub">GitHub / 飞书任务 / 飞书消息</p>
    </header>

    <section class="card">
      <header class="card-head">
        <div>
          <h2 class="card-title">同步记录</h2>
          <p class="card-sub">{{ rows.length }} 条</p>
        </div>
        <button class="btn btn--ghost" :disabled="loading" @click="load">
          <RefreshCw :size="14" :stroke-width="1.6" />
          刷新
        </button>
      </header>

      <p v-if="loading" class="state-line">正在加载</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else-if="rows.length" class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>数据源</th>
              <th>资源</th>
              <th>状态</th>
              <th>最近同步</th>
              <th>错误</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td class="mono">{{ row.source }}</td>
              <td class="mono">{{ row.resource_key }}</td>
              <td>
                <span class="badge" :class="row.status === 'success' ? 'badge--on' : 'badge--off'">
                  {{ row.status }}
                </span>
              </td>
              <td class="mono">{{ row.last_synced_at || '—' }}</td>
              <td class="wrap">{{ row.error_message || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="state-line">还没有同步记录，先在日报页生成一次</p>
    </section>
  </div>
</template>
