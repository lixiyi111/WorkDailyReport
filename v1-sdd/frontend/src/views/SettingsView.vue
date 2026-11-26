<script setup>
import { Save } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'

import client from '../api/client'

const DEFAULT_FORM = {
  timezone: 'Asia/Shanghai',
  auto_collect_time: '09:00',
  auto_generate_time: '09:10',
  auto_push_time: '09:15',
  retention_days: '90',
  ai_enabled: 'false',
  ai_model: '',
  report_template: '个人日报四段式 + 团队日报四段式',
}

const form = reactive({ ...DEFAULT_FORM })
const loading = ref(true)
const error = ref('')
const notice = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/settings')
    Object.assign(form, DEFAULT_FORM, data)
  } catch {
    error.value = '无法加载系统设置'
  } finally {
    loading.value = false
  }
}

async function save() {
  notice.value = ''
  try {
    await client.put('/settings', { values: { ...form } })
    notice.value = '已保存'
  } catch {
    notice.value = '保存失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>设置</p>
      <h1 class="page-title">系统设置</h1>
      <p class="page-sub">日报模板、自动任务时间与 AI 配置（非敏感项）</p>
    </header>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">运行配置</h2>
          <p class="card-sub">凭证类配置仍由 `.env` 管理</p>
        </div>
        <button class="btn" @click="save"><Save :size="14" :stroke-width="1.5" />保存</button>
      </header>

      <p v-if="loading" class="state-line">正在加载设置</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <template v-else>
        <div class="form-grid">
          <label class="field">
            <span>系统时区</span>
            <input v-model="form.timezone" class="input" placeholder="Asia/Shanghai" />
          </label>
          <label class="field">
            <span>自动采集时间</span>
            <input v-model="form.auto_collect_time" class="input" placeholder="09:00" />
          </label>
          <label class="field">
            <span>自动生成时间</span>
            <input v-model="form.auto_generate_time" class="input" placeholder="09:10" />
          </label>
          <label class="field">
            <span>自动推送时间</span>
            <input v-model="form.auto_push_time" class="input" placeholder="09:15" />
          </label>
          <label class="field">
            <span>数据保留天数</span>
            <input v-model="form.retention_days" class="input" type="number" min="1" />
          </label>
          <label class="field">
            <span>AI 润色</span>
            <select v-model="form.ai_enabled" class="input">
              <option value="false">关闭</option>
              <option value="true">开启</option>
            </select>
          </label>
          <label class="field">
            <span>AI 模型</span>
            <input v-model="form.ai_model" class="input" placeholder="如 claude-sonnet-5-5" />
          </label>
          <label class="field">
            <span>日报模板</span>
            <input v-model="form.report_template" class="input" />
          </label>
        </div>
        <p v-if="notice" class="saved-note">{{ notice }}</p>
        <p class="muted">
          说明：自动任务时间目前用于记录配置，调度器接入设置读取后可生效；AI 润色为可插拔扩展，未配置模型时使用确定性模板。
        </p>
      </template>
    </section>
  </div>
</template>
