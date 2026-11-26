<script setup>
import { Link2, RefreshCw } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import client from '../api/client'

const loading = ref(true)
const error = ref('')
const notice = ref('')
const rows = ref([])
const members = ref([])

const form = ref({
  member_id: '',
  provider: 'github',
  external_id: '',
  external_username: '',
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [unmatched, memberList] = await Promise.all([
      client.get('/identities/unmatched'),
      client.get('/members'),
    ])
    rows.value = unmatched.data
    members.value = memberList.data
    if (!form.value.member_id && members.value.length) {
      form.value.member_id = String(members.value[0].id)
    }
  } catch {
    error.value = '无法加载身份数据'
  } finally {
    loading.value = false
  }
}

async function bind() {
  notice.value = ''
  if (!form.value.member_id || !form.value.external_id.trim()) {
    notice.value = '请选择成员并填写外部 ID'
    return
  }
  try {
    await client.post(`/members/${form.value.member_id}/identities`, {
      provider: form.value.provider,
      external_id: form.value.external_id.trim(),
      external_username: form.value.external_username.trim() || null,
    })
    notice.value = '绑定成功'
    form.value.external_id = ''
    form.value.external_username = ''
    await load()
  } catch (err) {
    notice.value =
      err.response?.status === 409 ? '该外部身份已绑定' : '绑定失败，请检查输入'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker">
        <span class="brand-dot" aria-hidden="true"></span>
        身份绑定
      </p>
      <h1 class="page-title">未归属身份</h1>
      <p class="page-sub">把 GitHub / 飞书账号映射到具体成员</p>
    </header>

    <section class="card">
      <header class="card-head">
        <div>
          <h2 class="card-title">未归属记录</h2>
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
              <th>来源</th>
              <th>外部 ID</th>
              <th>名称</th>
              <th>数据类型</th>
              <th>数据 ID</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td class="mono">{{ row.provider }}</td>
              <td class="mono">{{ row.external_id }}</td>
              <td>{{ row.external_name || '—' }}</td>
              <td class="mono">{{ row.source_type }}</td>
              <td class="mono wrap">{{ row.source_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="state-line">没有未归属记录</p>
    </section>

    <section class="card">
      <h2 class="card-title">手工绑定</h2>
      <p class="card-sub">绑定后重新生成日报即可归属</p>
      <form class="form-grid" @submit.prevent="bind">
        <label class="field">
          <span>成员</span>
          <select v-model="form.member_id" class="select">
            <option v-for="member in members" :key="member.id" :value="String(member.id)">
              {{ member.name }} · {{ member.email }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>平台</span>
          <select v-model="form.provider" class="select">
            <option value="github">GitHub</option>
            <option value="feishu">飞书</option>
          </select>
        </label>
        <label class="field">
          <span>外部 ID</span>
          <input v-model="form.external_id" class="input" placeholder="如 ou_xxx / github login" />
        </label>
        <label class="field">
          <span>外部用户名（可选）</span>
          <input v-model="form.external_username" class="input" />
        </label>
        <button class="btn btn--primary" type="submit">
          <Link2 :size="14" :stroke-width="1.6" />
          绑定
        </button>
        <span v-if="notice" class="note">{{ notice }}</span>
      </form>
    </section>
  </div>
</template>
