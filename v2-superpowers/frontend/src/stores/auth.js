import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import client from '../api/client'

const TOKEN_KEY = 'wdr2_token'
const USER_KEY = 'wdr2_user'

function readUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(readUser())

  const role = computed(() => user.value?.role || '')
  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  function persist() {
    if (token.value) {
      localStorage.setItem(TOKEN_KEY, token.value)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
    if (user.value) {
      localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  async function login(username, password) {
    const { data } = await client.post('/auth/login', { username, password })
    token.value = data.access_token
    user.value = data.user
    persist()
  }

  async function fetchMe() {
    const { data } = await client.get('/auth/me')
    user.value = data
    persist()
  }

  function logout() {
    token.value = ''
    user.value = null
    persist()
  }

  return { token, user, role, isAuthenticated, login, fetchMe, logout }
})
