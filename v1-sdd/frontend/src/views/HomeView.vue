<script setup>
import { onMounted, ref } from 'vue'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const health = ref(null)

async function loadHealth() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/health')
    health.value = data
  } catch (err) {
    error.value = '无法连接后端服务，请确认 FastAPI 已在 8000 端口启动。'
  } finally {
    loading.value = false
  }
}

onMounted(loadHealth)
</script>

<template>
  <section class="card">
    <header class="card-head">
      <h2>系统状态</h2>
      <button class="btn" :disabled="loading" @click="loadHealth">
        {{ loading ? '检测中…' : '重新检测' }}
      </button>
    </header>

    <p v-if="loading" class="muted">正在检测后端连接…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else>
      <p class="ok">后端连接正常 · 环境：{{ health.app_env }}</p>
      <ul class="cred-list">
        <li v-for="(ready, name) in health.credentials" :key="name">
          <span>{{ name }}</span>
          <span :class="ready ? 'badge on' : 'badge off'">
            {{ ready ? '已就绪' : '未配置' }}
          </span>
        </li>
      </ul>
    </div>
  </section>

  <section class="card">
    <h2>下一步</h2>
    <p class="muted">
      当前为项目骨架。采集层 / 生成层 / 推送层 / 主编排入口将在后续按规范逐步实现，
      此页面仅用于验证前后端连通与凭证就绪状态。
    </p>
  </section>
</template>
