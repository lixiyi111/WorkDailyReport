<script setup>
import { ArrowRight } from '@lucide/vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import client from '../api/client'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('admin')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.post('/auth/login', {
      username: username.value,
      password: password.value,
    })
    auth.setAuth(data.access_token, data.user)
    await router.push('/')
  } catch {
    error.value = '用户名或密码错误，或账号已停用'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-shell">
    <form class="card login-card" @submit.prevent="submit">
      <div class="login-brand">
        <span class="brand-dot" aria-hidden="true"></span>
        <span class="brand-word">智能日报</span>
      </div>
      <p class="page-kicker">工作日报管理平台</p>
      <h1 class="login-title">登录</h1>
      <p class="page-sub">使用团队账号进入管理工作台</p>

      <label class="field">
        <span>用户名</span>
        <input v-model="username" class="input" autocomplete="username" />
      </label>
      <label class="field">
        <span>密码</span>
        <input
          v-model="password"
          class="input"
          type="password"
          autocomplete="current-password"
        />
      </label>

      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn login-submit" :disabled="loading">
        {{ loading ? '登录中' : '登录' }}
        <ArrowRight :size="14" :stroke-width="1.5" />
      </button>
      <p class="login-hint muted">演示环境默认账号见项目 README / `.env`</p>
    </form>
  </div>
</template>
