<script setup>
import { ArrowRight, LockKeyhole, UserRound } from '@lucide/vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('admin')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value.trim(), password.value)
    router.push('/')
  } catch {
    error.value = '用户名或密码错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="login-card">
    <div class="login-brand">
      <span class="brand-mark">DR</span>
      <div>
        <h1>智能日报</h1>
        <p>v2 · Superpowers 工作流驱动</p>
      </div>
    </div>

    <form class="login-form" @submit.prevent="submit">
      <label class="field">
        <span><UserRound :size="14" :stroke-width="1.6" />用户名</span>
        <input v-model="username" class="input" autocomplete="username" />
      </label>

      <label class="field">
        <span><LockKeyhole :size="14" :stroke-width="1.6" />密码</span>
        <input
          v-model="password"
          class="input"
          type="password"
          autocomplete="current-password"
          placeholder="请输入密码"
        />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="btn btn--primary" type="submit" :disabled="loading">
        {{ loading ? '登录中' : '登录' }}
        <ArrowRight :size="15" :stroke-width="1.6" />
      </button>
    </form>

    <p class="login-hint">演示账号：admin / admin123 · leader / leader123 · member / member123</p>
  </section>
</template>
