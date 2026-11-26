<script setup>
import { Play } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import client from '../api/client'

const today = () => new Date().toISOString().slice(0, 10)
const STATUS_LABEL = {
  normal: '正常',
  late: '迟到',
  early: '早退',
  absent: '缺卡',
  leave: '请假',
}

const workDate = ref(today())
const loading = ref(true)
const error = ref('')
const notice = ref('')
const rows = ref([])

const formatTime = (value) => (value ? value.replace('T', ' ').slice(11, 16) : '—')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/attendance', { params: { date: workDate.value } })
    rows.value = data
  } catch {
    error.value = '无法加载考勤数据'
  } finally {
    loading.value = false
  }
}

async function collect() {
  notice.value = ''
  try {
    const { data } = await client.post('/attendance/collect', { work_date: workDate.value })
    notice.value = `已采集 ${data.collected} 人考勤`
    await load()
  } catch {
    notice.value = '考勤采集失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>考勤</p>
      <h1 class="page-title">考勤数据</h1>
      <p class="page-sub">打卡时间、迟到早退与请假记录（当前为 Mock 数据）</p>
    </header>

    <div class="toolbar span-all">
      <label class="field field--inline">
        <span>日期</span>
        <input v-model="workDate" type="date" class="input" @change="load" />
      </label>
      <button class="btn" @click="collect"><Play :size="14" :stroke-width="1.5" />采集考勤</button>
      <span v-if="notice" class="saved-note">{{ notice }}</span>
    </div>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">考勤记录</h2>
          <p class="card-sub">{{ rows.length }} 人</p>
        </div>
      </header>
      <p v-if="loading" class="state-line">正在加载考勤</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>成员</th>
              <th>日期</th>
              <th>上班</th>
              <th>下班</th>
              <th>状态</th>
              <th>迟到 / 早退</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.member_name || '未归属' }}</td>
              <td class="mono">{{ row.work_date }}</td>
              <td class="mono">{{ formatTime(row.check_in) }}</td>
              <td class="mono">{{ formatTime(row.check_out) }}</td>
              <td><span class="tag">{{ STATUS_LABEL[row.status] || row.status }}</span></td>
              <td class="mono">
                {{ row.late_minutes || 0 }} / {{ row.early_minutes || 0 }} 分钟
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!rows.length" class="state-line">当天还没有考勤数据，点击“采集考勤”生成 Mock 数据</p>
      </div>
    </section>
  </div>
</template>
