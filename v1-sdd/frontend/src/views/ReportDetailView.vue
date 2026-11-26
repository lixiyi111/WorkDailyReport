<script setup>
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import client from '../api/client'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const report = ref(null)
const editing = ref(false)
const draft = ref('')
const saving = ref(false)
const saveError = ref('')
const savedNote = ref('')

const rendered = computed(() => {
  if (!report.value?.content_md) return ''
  return DOMPurify.sanitize(marked.parse(report.value.content_md))
})

const heading = computed(() => {
  if (!report.value) return '日报详情'
  const label =
    report.value.report_type === 'team'
      ? '团队日报'
      : `${report.value.member_name || '成员'} 的个人日报`
  return `${report.value.report_date} · ${label}`
})

const statusLabel = computed(() => {
  const status = report.value?.status
  return ({ generated: '已生成', published: '已发布', draft: '草稿' })[status] ?? status ?? ''
})

async function loadReport() {
  loading.value = true
  error.value = ''
  editing.value = false
  savedNote.value = ''
  try {
    const { data } = await client.get(`/reports/${route.params.id}`)
    report.value = data
    draft.value = data.content_md ?? ''
  } catch {
    error.value = '无法加载日报详情'
  } finally {
    loading.value = false
  }
}

function startEdit() {
  draft.value = report.value?.content_md ?? ''
  editing.value = true
  savedNote.value = ''
  saveError.value = ''
}

async function saveReport() {
  saving.value = true
  saveError.value = ''
  try {
    const { data } = await client.put(`/reports/${route.params.id}`, {
      content_md: draft.value,
      editor: 'web',
      change_note: '前端编辑',
    })
    report.value = { ...report.value, ...data }
    editing.value = false
    savedNote.value = `已保存，当前 v${data.current_version}`
  } catch {
    saveError.value = '保存失败，请稍后重试'
  } finally {
    saving.value = false
  }
}

onMounted(loadReport)
watch(() => route.params.id, loadReport)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker">
        <span class="brand-dot" aria-hidden="true"></span>
        <RouterLink to="/reports" class="crumb">日报</RouterLink>
      </p>
      <h1 class="page-title">{{ heading }}</h1>
      <p v-if="report" class="page-sub">
        {{ statusLabel }} · v{{ report.current_version }}
        <template v-if="report.member_name"> · {{ report.member_name }}</template>
      </p>
    </header>

    <section class="card detail-card" aria-labelledby="detail-title">
      <header class="card-head">
        <div>
          <h2 id="detail-title" class="card-title">日报正文</h2>
          <p class="card-sub">Markdown · 可手工修订</p>
        </div>
        <button v-if="report && !editing" class="btn" @click="startEdit">编辑</button>
      </header>

      <p v-if="loading" class="state-line">正在加载日报</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <template v-else-if="report">
        <div v-if="!editing" class="markdown" v-html="rendered"></div>
        <div v-else class="editor">
          <textarea
            v-model="draft"
            class="textarea"
            rows="18"
            aria-label="日报 Markdown 内容"
          ></textarea>
          <div class="editor-actions">
            <button class="btn" :disabled="saving" @click="saveReport">
              {{ saving ? '保存中' : '保存' }}
            </button>
            <button class="btn btn--ghost" :disabled="saving" @click="editing = false">
              取消
            </button>
            <span v-if="saveError" class="error">{{ saveError }}</span>
          </div>
        </div>
        <p v-if="savedNote" class="saved-note">{{ savedNote }}</p>

        <ul v-if="report.items?.length" class="item-list">
          <li v-for="item in report.items" :key="item.id" class="item-row">
            <span class="item-cat mono">{{ item.category }}</span>
            <span class="item-title">{{ item.title }}</span>
            <span class="item-role mono">{{ item.attribution_role || '—' }}</span>
          </li>
        </ul>
      </template>
    </section>
  </div>
</template>
