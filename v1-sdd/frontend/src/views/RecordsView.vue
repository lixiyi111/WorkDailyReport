<script setup>
import { Play, Search } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'

import client from '../api/client'

const today = () => new Date().toISOString().slice(0, 10)
const TYPE_LABEL = { commit: '提交', task: '任务', message: '消息' }

const loading = ref(true)
const error = ref('')
const records = ref([])
const total = ref(0)
const members = ref([])
const filters = reactive({
  type: '',
  source: '',
  member_id: '',
  date_from: '',
  date_to: '',
  q: '',
})

const formatTime = (value) => (value ? value.replace('T', ' ').slice(0, 16) : '—')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value !== ''),
    )
    const [recordResponse, memberResponse] = await Promise.all([
      client.get('/work-records', { params }),
      client.get('/members'),
    ])
    records.value = recordResponse.data.items
    total.value = recordResponse.data.total
    members.value = memberResponse.data
  } catch {
    error.value = '无法加载工作记录'
  } finally {
    loading.value = false
  }
}

async function collect() {
  try {
    await client.post('/work-records/collect', { date: today() })
    await load()
  } catch {
    error.value = '采集失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>工作数据</p>
      <h1 class="page-title">工作数据</h1>
      <p class="page-sub">GitHub 提交、飞书任务与群消息的统一视图</p>
    </header>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">采集记录</h2>
          <p class="card-sub">{{ total }} 条</p>
        </div>
        <div class="filters">
          <select v-model="filters.type" class="select">
            <option value="">全部类型</option>
            <option value="commit">提交</option>
            <option value="task">任务</option>
            <option value="message">消息</option>
          </select>
          <select v-model="filters.source" class="select">
            <option value="">全部来源</option>
            <option value="github">GitHub</option>
            <option value="feishu">飞书</option>
          </select>
          <select v-model="filters.member_id" class="select">
            <option value="">全部成员</option>
            <option v-for="member in members" :key="member.id" :value="member.id">
              {{ member.name }}
            </option>
          </select>
          <input v-model="filters.date_from" type="date" class="select" />
          <input v-model="filters.date_to" type="date" class="select" />
          <input v-model="filters.q" class="select" placeholder="搜索内容" />
          <button class="btn" @click="load"><Search :size="14" :stroke-width="1.5" />查询</button>
          <button class="btn" @click="collect"><Play :size="14" :stroke-width="1.5" />采集今日</button>
        </div>
      </header>

      <p v-if="loading" class="state-line">正在加载工作记录</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>类型</th>
              <th>来源</th>
              <th>成员</th>
              <th>内容</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="record.id">
              <td class="mono">{{ formatTime(record.occurred_at) }}</td>
              <td><span class="tag">{{ TYPE_LABEL[record.record_type] || record.record_type }}</span></td>
              <td>{{ record.source }}</td>
              <td>{{ record.member_name || '未归属' }}</td>
              <td>
                <div class="record-title">{{ record.title }}</div>
                <div class="record-detail">{{ record.detail }}</div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!records.length" class="state-line">没有匹配的工作记录</p>
      </div>
    </section>
  </div>
</template>
