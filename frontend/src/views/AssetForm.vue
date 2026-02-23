<template>
  <div class="form-page">
    <div class="form-card">
      <div class="form-header">
        <button class="back-btn" @click="goBack()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
        </button>
        <div>
          <h3>{{ isEdit ? '编辑资产' : '新增资产' }}</h3>
          <p class="form-desc">{{ isEdit ? '修改资产信息' : '录入新的个人资产' }}</p>
        </div>
      </div>

      <div class="form-layout">
        <div class="form-main">
          <div class="form-section">
            <h4 class="form-section-title">基本信息</h4>
            <div class="form-grid">
              <div class="form-group full">
                <label>资产名称 <span class="required">*</span></label>
                <input v-model="form.name" placeholder="如：MacBook Pro 14" class="form-input" />
              </div>

              <div class="form-group">
                <div class="category-label-row">
                  <label>资产分类 <span class="required">*</span></label>
                  <button type="button" class="inline-link-btn" @click="handleCreateCategory">新建分类</button>
                </div>
                <el-select v-model="form.category_id" placeholder="选择分类" filterable style="width: 100%">
                  <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
                  <template #empty>
                    <div class="category-empty">
                      <span>暂无分类</span>
                      <el-button link type="primary" @click="handleCreateCategory">立即新建</el-button>
                    </div>
                  </template>
                </el-select>
              </div>

              <div class="form-group">
                <label>购买渠道</label>
                <el-select v-model="form.purchase_channel" placeholder="选择或输入渠道" filterable allow-create style="width: 100%">
                  <el-option label="京东" value="京东" />
                  <el-option label="淘宝" value="淘宝" />
                  <el-option label="拼多多" value="拼多多" />
                  <el-option label="苏宁" value="苏宁" />
                  <el-option label="官网" value="官网" />
                  <el-option label="线下" value="线下" />
                  <el-option label="二手" value="二手" />
                  <el-option label="闲鱼" value="闲鱼" />
                </el-select>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4 class="form-section-title">购买信息</h4>
            <div class="form-grid form-grid-3">
              <div class="form-group">
                <label>购买价格 <span class="required">*</span></label>
                <div class="input-with-prefix">
                  <span class="input-prefix">¥</span>
                  <input v-model.number="form.purchase_price" type="number" min="0" step="0.01" class="form-input has-prefix" />
                </div>
              </div>
              <div class="form-group">
                <label>购买日期 <span class="required">*</span></label>
                <el-date-picker v-model="form.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </div>
              <div class="form-group">
                <label>预计使用天数</label>
                <div class="input-with-suffix">
                  <input v-model.number="form.expected_days" type="number" min="1" step="1" class="form-input has-suffix" placeholder="如：1095（约3年）" />
                  <span class="input-suffix">天</span>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section" v-if="isEdit">
            <h4 class="form-section-title">弃用与回收</h4>
            <div class="form-grid form-grid-3">
              <div class="form-group">
                <label>弃用日期</label>
                <el-date-picker v-model="form.disposed_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" clearable />
              </div>
              <div class="form-group">
                <label>弃用原因</label>
                <el-select v-model="form.disposed_reason" placeholder="选择原因" filterable allow-create clearable style="width: 100%">
                  <el-option label="坏了" value="坏了" />
                  <el-option label="以旧换新" value="以旧换新" />
                  <el-option label="卖了" value="卖了" />
                  <el-option label="送人" value="送人" />
                  <el-option label="丢了" value="丢了" />
                  <el-option label="不需要了" value="不需要了" />
                </el-select>
              </div>

              <div class="form-group">
                <label>回收金额</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">¥</span>
                  <input v-model.number="form.recovery_amount" type="number" min="0" step="0.01" class="form-input has-prefix" placeholder="可选" />
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4 class="form-section-title">备注</h4>
            <textarea v-model="form.notes" placeholder="可选的补充说明..." class="form-textarea" rows="3"></textarea>
          </div>
        </div>

        <aside class="form-side">
          <div class="side-card">
            <h4 class="side-title">实时预览</h4>
            <div class="side-kv"><span>资产名称</span><strong>{{ form.name || '未填写' }}</strong></div>
            <div class="side-kv"><span>资产分类</span><strong>{{ categoryName }}</strong></div>
            <div class="side-kv"><span>购买渠道</span><strong>{{ form.purchase_channel || '未填写' }}</strong></div>
            <div class="side-kv"><span>购买价格</span><strong>¥{{ priceText }}</strong></div>
            <div class="side-kv" v-if="form.expected_days"><span>预计使用</span><strong>{{ form.expected_days }} 天</strong></div>
            <div class="side-kv" v-if="form.expected_days"><span>预估日费用</span><strong>¥{{ estimatedDailyCostText }}/天</strong></div>
            <div class="side-kv" v-if="isEdit"><span>回收金额</span><strong>¥{{ recoveryText }}</strong></div>
            <div class="side-kv" v-if="isEdit"><span>实际费用</span><strong>¥{{ netCostText }}</strong></div>
            <div class="side-kv" v-if="isEdit"><span>当前状态</span><strong>{{ statusText }}</strong></div>
          </div>

          <div class="side-card muted">
            <h4 class="side-title">填写建议</h4>
            <p class="side-tip">弃用且有回收收入时，填写回收金额，系统会自动计算实际费用（购买价格 - 回收金额）。</p>
          </div>

          <div class="side-actions">
            <button class="btn-secondary" @click="goBack()">取消</button>
            <button class="btn-primary" @click="submit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              {{ isEdit ? '保存修改' : '创建资产' }}
            </button>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAsset, createAsset, updateAsset, getCategories, createCategory } from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const categories = ref([])

const form = ref({
  name: '',
  category_id: null,
  purchase_price: 0,
  purchase_date: new Date().toISOString().slice(0, 10),
  purchase_channel: '',
  expected_days: null,
  status: 'active',
  disposed_date: null,
  disposed_reason: null,
  recovery_amount: null,
  recovery_date: null,
  notes: '',
})

const categoryName = computed(() => {
  const hit = categories.value.find((x) => x.id === form.value.category_id)
  return hit?.name || '未选择'
})

const priceText = computed(() => {
  const val = Number(form.value.purchase_price || 0)
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const recoveryText = computed(() => {
  const val = Number(form.value.recovery_amount || 0)
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const netCostText = computed(() => {
  const purchase = Number(form.value.purchase_price || 0)
  const recovery = Number(form.value.recovery_amount || 0)
  const net = Math.max(purchase - recovery, 0)
  return net.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const estimatedDailyCostText = computed(() => {
  const purchase = Number(form.value.purchase_price || 0)
  const recovery = Number(form.value.recovery_amount || 0)
  const net = Math.max(purchase - recovery, 0)
  const days = Number(form.value.expected_days || 0)
  if (!days) return '0.00'
  return (net / days).toFixed(2)
})

const statusText = computed(() => (form.value.status === 'disposed' ? '已弃用' : '使用中'))

function asQueryText(value) {
  return Array.isArray(value) ? value[0] : value
}

async function loadCategories(preferName = '') {
  try {
    const res = await getCategories()
    categories.value = res.data
    if (preferName) {
      const hit = categories.value.find((x) => x.name === preferName)
      if (hit) form.value.category_id = hit.id
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('分类加载失败，请确认后端服务已启动')
  }
}

async function handleCreateCategory() {
  try {
    const { value } = await ElMessageBox.prompt('请输入新分类名称', '新建分类', {
      inputPlaceholder: '例如：平板电脑',
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (v) => {
        if (!v || !v.trim()) return '分类名称不能为空'
        if (v.trim().length > 50) return '分类名称不能超过 50 个字符'
        return true
      },
    })

    const name = value.trim()
    const res = await createCategory({ name })
    categories.value.push(res.data)
    form.value.category_id = res.data.id
    ElMessage.success(`已创建分类：${name}`)
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '创建分类失败')
    await loadCategories()
  }
}

function buildPayload() {
  const payload = { ...form.value }

  payload.expected_days = payload.expected_days || null
  payload.disposed_date = payload.disposed_date || null
  payload.disposed_reason = payload.disposed_reason || null

  if (payload.recovery_amount === '' || payload.recovery_amount === undefined) {
    payload.recovery_amount = null
  }
  if (payload.recovery_amount !== null) {
    payload.recovery_amount = Number(payload.recovery_amount)
  }

  payload.recovery_date = null
  if (payload.status === 'disposed' && payload.recovery_amount !== null) {
    payload.recovery_date = payload.disposed_date
  }

  if (payload.status !== 'disposed') {
    payload.disposed_date = null
    payload.disposed_reason = null
    payload.recovery_amount = null
    payload.recovery_date = null
  }

  return payload
}

async function submit() {
  if (!form.value.name || !form.value.category_id) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const payload = buildPayload()
    if (isEdit.value) {
      await updateAsset(route.params.id, payload)
      ElMessage.success('已保存')
    } else {
      await createAsset(payload)
      ElMessage.success('已创建')
    }
    router.push('/assets')
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败，请稍后重试')
  }
}

function goBack() {
  if (route.query.from === 'bill') {
    router.push('/bills')
  } else if (route.query.from === 'cards') {
    router.push('/assets?view=cards')
  } else if (window.history.state?.back) {
    router.back()
  } else {
    router.push('/assets')
  }
}

function applyBillPrefill() {
  if (route.query.from !== 'bill' || isEdit.value) return

  const amountText = asQueryText(route.query.amount)
  const amount = Number(amountText)
  if (!isNaN(amount) && amount > 0) {
    form.value.purchase_price = Number(amount.toFixed(2))
  }

  const dateText = asQueryText(route.query.purchase_date)
  if (dateText && /^\d{4}-\d{2}-\d{2}$/.test(dateText)) {
    form.value.purchase_date = dateText
  }

  const categoryText = asQueryText(route.query.category_id)
  const categoryId = Number(categoryText)
  if (!isNaN(categoryId) && categories.value.some((c) => c.id === categoryId)) {
    form.value.category_id = categoryId
  }

  const notesText = asQueryText(route.query.notes)
  if (notesText && !form.value.notes) {
    form.value.notes = notesText
  }

  ElMessage.info('已自动带入记账信息，请确认后保存资产')
}

onMounted(async () => {
  await loadCategories()
  if (isEdit.value) {
    const r = await getAsset(route.params.id)
    Object.assign(form.value, r.data)
  } else {
    applyBillPrefill()
  }
})
</script>
<style scoped>
.form-page {
  max-width: 1320px;
  margin: 0 auto;
}

.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 28px;
  border-bottom: 1px solid var(--border-color);
  background: #fafbfd;
}
.form-header h3 {
  font-size: 17px;
  font-weight: 600;
}
.form-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}
.back-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 20px;
  padding: 24px;
}

.form-main {
  min-width: 0;
}

.form-side {
  position: sticky;
  top: 20px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: calc(100vh - 140px);
}

.side-card {
  background: #fafbfd;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 14px;
}

.side-card.muted {
  background: #f8fbff;
}

.side-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.side-kv {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  padding: 7px 0;
  border-bottom: 1px dashed var(--border-color);
  font-size: 13px;
  color: var(--text-secondary);
}

.side-kv:last-child {
  border-bottom: none;
}

.side-kv strong {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  text-align: right;
  word-break: break-word;
}

.side-tip {
  font-size: 12px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.side-tip + .side-tip {
  margin-top: 8px;
}

.side-actions {
  margin-top: auto;
  position: sticky;
  bottom: 14px;
  align-self: stretch;
  z-index: 2;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.form-section {
  margin-bottom: 24px;
}
.form-section:last-of-type {
  margin-bottom: 28px;
}
.form-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.form-grid.form-grid-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group.full {
  grid-column: 1 / -1;
}
.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}
.required {
  color: var(--danger);
}

.category-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.inline-link-btn {
  border: none;
  background: none;
  color: var(--accent);
  font-size: 12px;
  cursor: pointer;
  padding: 0;
}
.inline-link-btn:hover {
  text-decoration: underline;
}

.category-empty {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 4px;
  color: var(--text-secondary);
  font-size: 13px;
}

.form-page :deep(.el-select__wrapper),
.form-page :deep(.el-date-editor .el-input__wrapper) {
  background: var(--bg-card);
  color: var(--text-primary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  border-radius: var(--radius-sm);
}

.form-page :deep(.el-select__wrapper:hover),
.form-page :deep(.el-date-editor .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cfd6e4 inset;
}

.form-page :deep(.el-select__wrapper.is-focused),
.form-page :deep(.el-date-editor .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent) inset, 0 0 0 3px rgba(79, 110, 247, 0.1);
}

.form-page :deep(.el-select__selected-item),
.form-page :deep(.el-input__inner),
.form-page :deep(.el-select__input),
.form-page :deep(.el-range-input) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
  transition: none !important;
}

.form-page :deep(.el-select__placeholder),
.form-page :deep(.el-input__placeholder) {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  transition: none !important;
}

.form-page :deep(.el-select__caret),
.form-page :deep(.el-input__icon),
.form-page :deep(.el-icon-circle-close) {
  color: var(--text-secondary);
}

.form-page :deep(.el-select__wrapper:hover .el-select__selected-item),
.form-page :deep(.el-select__wrapper:hover .el-select__input),
.form-page :deep(.el-select__wrapper.is-focused .el-select__selected-item),
.form-page :deep(.el-select__wrapper.is-focused .el-select__input),
.form-page :deep(.el-date-editor:hover .el-input__inner),
.form-page :deep(.el-date-editor .el-input__wrapper.is-focus .el-input__inner) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}

.form-input {
  height: 38px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0 14px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  background: var(--bg-card);
  width: 100%;
}
.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.1);
}

.input-with-prefix {
  position: relative;
}
.input-prefix {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
}
.form-input.has-prefix {
  padding-left: 30px;
}
.input-with-suffix {
  position: relative;
}
.input-suffix {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
}
.form-input.has-suffix {
  padding-right: 36px;
}

.form-textarea {
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  resize: vertical;
  font-family: inherit;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.form-textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.1);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0 24px;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition);
}
.btn-primary:hover {
  filter: brightness(1.08);
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0 24px;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}
.btn-secondary:hover {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

@media (max-width: 1180px) {
  .form-page {
    max-width: 100%;
  }

  .form-layout {
    grid-template-columns: 1fr;
  }

  .form-side {
    position: static;
    top: auto;
    min-height: 0;
  }

  .side-actions {
    position: static;
    margin-top: 0;
  }

  .form-grid.form-grid-3 {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 860px) {
  .form-header {
    padding: 20px;
  }

  .form-layout {
    padding: 20px;
    gap: 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .side-actions {
    flex-wrap: wrap;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style>

