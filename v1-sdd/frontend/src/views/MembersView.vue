<script setup>
import { Link2, UserCog, UserPlus } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'

import client from '../api/client'

const ROLE_LABEL = { leader: '组长', member: '成员', mentor: '导师' }
const STATUS_LABEL = { active: '启用', inactive: '停用' }

const loading = ref(true)
const error = ref('')
const notice = ref('')
const members = ref([])
const newMember = reactive({ name: '', email: '', role: 'member' })
const editingId = ref(null)
const editForm = reactive({ name: '', email: '', role: 'member', status: 'active' })
const bindForm = reactive({ member_id: '', provider: 'github', external_id: '' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/members')
    members.value = data
  } catch {
    error.value = '无法加载成员列表'
  } finally {
    loading.value = false
  }
}

async function createMember() {
  notice.value = ''
  try {
    await client.post('/members', { ...newMember })
    newMember.name = ''
    newMember.email = ''
    newMember.role = 'member'
    notice.value = '成员已创建'
    await load()
  } catch {
    notice.value = '创建失败，请检查邮箱或必填项'
  }
}

function startEdit(member) {
  editingId.value = member.id
  Object.assign(editForm, {
    name: member.name,
    email: member.email,
    role: member.role,
    status: member.status,
  })
}

async function saveEdit() {
  try {
    await client.put(`/members/${editingId.value}`, { ...editForm })
    editingId.value = null
    notice.value = '成员已更新'
    await load()
  } catch {
    notice.value = '更新失败'
  }
}

async function deactivate(member) {
  try {
    await client.delete(`/members/${member.id}`)
    notice.value = `${member.name} 已停用`
    await load()
  } catch {
    notice.value = '停用失败'
  }
}

async function bindIdentity() {
  notice.value = ''
  try {
    const { data } = await client.post(`/members/${bindForm.member_id}/identities`, {
      provider: bindForm.provider,
      external_id: bindForm.external_id,
    })
    notice.value = `身份已绑定，回填 ${data.resolved_records} 条记录`
    bindForm.external_id = ''
    await load()
  } catch {
    notice.value = '绑定失败：身份可能已存在'
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page-head">
      <p class="page-kicker"><span class="brand-dot" aria-hidden="true"></span>成员</p>
      <h1 class="page-title">成员管理</h1>
      <p class="page-sub">维护成员、角色与 GitHub / 飞书身份绑定</p>
    </header>

    <p v-if="notice" class="saved-note span-all">{{ notice }}</p>

    <section class="card report-card">
      <header class="card-head">
        <div>
          <h2 class="card-title">团队成员</h2>
          <p class="card-sub">{{ members.length }} 人</p>
        </div>
      </header>
      <p v-if="loading" class="state-line">正在加载成员</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.id">
              <td>{{ member.name }}</td>
              <td class="mono">{{ member.email }}</td>
              <td>{{ ROLE_LABEL[member.role] || member.role }}</td>
              <td>{{ STATUS_LABEL[member.status] || member.status }}</td>
              <td class="actions">
                <button class="btn btn--small" @click="startEdit(member)">编辑</button>
                <button class="btn btn--small" :disabled="member.status === 'inactive'" @click="deactivate(member)">
                  停用
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div class="form-row">
      <section class="card">
        <header class="card-head">
          <h2 class="card-title"><UserPlus :size="16" :stroke-width="1.5" /> 新建成员</h2>
        </header>
        <label class="field"><span>姓名</span><input v-model="newMember.name" class="input" /></label>
        <label class="field"><span>邮箱</span><input v-model="newMember.email" class="input" type="email" /></label>
        <label class="field">
          <span>角色</span>
          <select v-model="newMember.role" class="input">
            <option value="member">成员</option>
            <option value="leader">组长</option>
            <option value="mentor">导师</option>
          </select>
        </label>
        <button class="btn" @click="createMember">创建</button>
      </section>

      <section class="card">
        <header class="card-head">
          <h2 class="card-title"><Link2 :size="16" :stroke-width="1.5" /> 绑定身份</h2>
        </header>
        <label class="field">
          <span>成员</span>
          <select v-model="bindForm.member_id" class="input">
            <option value="">选择成员</option>
            <option v-for="member in members" :key="member.id" :value="member.id">{{ member.name }}</option>
          </select>
        </label>
        <label class="field">
          <span>平台</span>
          <select v-model="bindForm.provider" class="input">
            <option value="github">GitHub</option>
            <option value="feishu">飞书</option>
          </select>
        </label>
        <label class="field">
          <span>外部 ID</span>
          <input v-model="bindForm.external_id" class="input" placeholder="GitHub 用户名 / 邮箱 / 飞书 open_id" />
        </label>
        <button class="btn" :disabled="!bindForm.member_id || !bindForm.external_id" @click="bindIdentity">绑定</button>
      </section>
    </div>

    <section v-if="editingId" class="card">
      <header class="card-head">
        <h2 class="card-title"><UserCog :size="16" :stroke-width="1.5" /> 编辑成员</h2>
      </header>
      <div class="form-grid">
        <label class="field"><span>姓名</span><input v-model="editForm.name" class="input" /></label>
        <label class="field"><span>邮箱</span><input v-model="editForm.email" class="input" type="email" /></label>
        <label class="field">
          <span>角色</span>
          <select v-model="editForm.role" class="input">
            <option value="member">成员</option>
            <option value="leader">组长</option>
            <option value="mentor">导师</option>
          </select>
        </label>
        <label class="field">
          <span>状态</span>
          <select v-model="editForm.status" class="input">
            <option value="active">启用</option>
            <option value="inactive">停用</option>
          </select>
        </label>
      </div>
      <div class="card-actions">
        <button class="btn" @click="saveEdit">保存</button>
        <button class="btn btn--ghost" @click="editingId = null">取消</button>
      </div>
    </section>
  </div>
</template>
