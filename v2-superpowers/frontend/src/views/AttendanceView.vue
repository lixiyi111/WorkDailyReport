<script setup>
import { CalendarDays, RefreshCw } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'

import client from '../api/client'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const today = new Date().toISOString().slice(0, 10)
const dateFilter = ref(today)
const loading = ref(true)
const error = ref('')
const rows = ref([])

const isMember = computed(() => auth.role === 'member')

const statusLabel = (status) =>
  ({
    normal: '正常',
    late: '迟到',
    early: '早退',
    absent: '缺勤',
    leave: '请假',
    holiday: '节假日',
  })[status] ?? status

const statusClass = (status) =>
  status === 'normal' ? 'badge--on' : 'badge--off'

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(`${value}Z`)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai',
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const query = dateFilter.value ? `?date=${dateFilter.value}` : ''
    const { data } = await client.get(`/attendance${query}`)
    rows.value = data
  } catch {
    error.value = '无法加载考勤数据'
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
        考勤
      </p>
      <h1 class="page-title">考勤记录</h1>
      <p class="page-sub">
        {{ isMember ? '只显示本人的考勤' : '按日期查看成员考勤' }}
      </p>
    </header>

    <div class="toolbar">
      <label class="field field--inline">
        <span><CalendarDays :size="14" :stroke-width="1.6" />日期</span>
        <input v-model="dateFilter" type="date" class="input" @change="load" />
      </label>
      <button class="btn btn--ghost" :disabled="loading" @click="load">
        <RefreshCw :size="14" :stroke-width="1.6" />
        刷新
      </button>
      <span class="muted">{{ rows.length }} 条</span>
    </div>

    <section class="card">
      <header class="card-head">
        <div>
          <h2 class="card-title">考勤明细</h2>
          <p class="card-sub">状态与首末打卡时间</p>
        </div>
      </header>

      <p v-if="loading" class="state-line">正在加载</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else-if="rows.length" class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>成员</th>
              <th>日期</th>
              <th>状态</th>
              <th>上班</th>
              <th>下班</th>
              <th>来源</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.member_name }}</td>
              <td class="mono">{{ row.attendance_date }}</td>
              <td>
                <span class="badge" :class="statusClass(row.status)">
                  {{ statusLabel(row.status) }}
                </span>
              </td>
              <td class="mono">{{ formatTime(row.check_in_at) }}</td>
              <td class="mono">{{ formatTime(row.check_out_at) }}</td>
              <td class="mono">{{ row.source }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="state-line">该日期没有考勤记录</p>
    </section>
  </div>
</template>
