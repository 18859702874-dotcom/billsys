<template>
  <div class="bill-form-page">
    <div class="form-card">
      <div class="form-header">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16">
            <path d="M9.78 12.78a.75.75 0 01-1.06 0L4.47 8.53a.75.75 0 010-1.06l4.25-4.25a.75.75 0 011.06 1.06L6.06 8l3.72 3.72a.75.75 0 010 1.06z"/>
          </svg>
          返回
        </button>
        <h2 class="form-title">{{ isEdit ? '编辑记账' : '新增记账' }}</h2>
      </div>

      <!-- 支出 / 收入 切换 -->
      <div class="type-tabs">
        <button
          class="type-tab"
          :class="{ active: form.type === 'expense', expense: form.type === 'expense' }"
          @click="form.type = 'expense'"
        >支出</button>
        <button
          class="type-tab"
          :class="{ active: form.type === 'income', income: form.type === 'income' }"
          @click="form.type = 'income'"
        >收入</button>
      </div>

      <!-- 金额 -->
      <div class="amount-section">
        <span class="currency-sign">¥</span>
        <input
          ref="amountInput"
          v-model="amountStr"
          type="number"
          min="0.01"
          step="0.01"
          placeholder="0.00"
          class="amount-input"
          :class="form.type"
        />
      </div>

      <div class="fields">
        <!-- 分类：两级选择 -->
        <div class="field-group">
          <label class="field-label">分类</label>
          <div class="cat-selector">
            <div class="cat-level">
              <span class="level-hint">一级</span>
              <div class="cat-chips">
                <button
                  v-for="cat in l1Categories"
                  :key="cat.id"
                  class="cat-chip"
                  :class="{ active: selectedL1 && selectedL1.id === cat.id }"
                  @click="selectL1(cat)"
                >
                  {{ cat.name }}
                  <span v-if="isCategoryWithAssetRecord(cat.id)" class="chip-asset-flag">资产</span>
                </button>
              </div>
            </div>
            <div class="cat-level" v-if="selectedL1 && currentChildren.length">
              <span class="level-hint">二级</span>
              <div class="cat-chips">
                <button
                  v-for="cat in currentChildren"
                  :key="cat.id"
                  class="cat-chip sub"
                  :class="{ active: form.category_id === cat.id }"
                  @click="selectL2(cat)"
                >
                  {{ cat.name }}
                  <span v-if="isCategoryWithAssetRecord(cat.id)" class="chip-asset-flag">资产</span>
                </button>
              </div>
            </div>
          </div>
          <div class="selected-cat" v-if="selectedCatLabel">
            已选：<strong>{{ selectedCatLabel }}</strong>
          </div>
        </div>

        <!-- 日期 -->
        <div class="field-group">
          <label class="field-label">日期</label>
          <input type="date" v-model="form.date" class="field-input" :max="todayStr" />
        </div>

        <!-- 支付方式 -->
        <div class="field-group">
          <label class="field-label">支付方式</label>
          <div class="method-chips">
            <button
              v-for="m in paymentMethods"
              :key="m"
              class="method-chip"
              :class="{ active: form.payment_method === m }"
              @click="form.payment_method = m"
            >{{ m }}</button>
          </div>
        </div>

        <!-- 备注 -->
        <div class="field-group">
          <label class="field-label">备注</label>
          <textarea v-model="form.notes" class="field-textarea" placeholder="可选备注…" rows="2"></textarea>
        </div>
      </div>

      <div class="form-footer">
        <button class="btn-cancel" @click="goBack">取消</button>
        <button class="btn-submit" :class="form.type" @click="handleSubmit" :disabled="submitting">
          {{ submitting ? '保存中…' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAssets, getCategories, getTransactions, createTransaction, updateTransaction } from '../api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const categories = ref([])
const assetCategoryIdSet = ref(new Set())
const submitting = ref(false)
const amountStr = ref('')

const form = ref({
  type: 'expense',
  category_id: null,
  date: new Date().toISOString().slice(0, 10),
  payment_method: '微信',
  notes: '',
})

const selectedL1 = ref(null)
const todayStr = new Date().toISOString().slice(0, 10)

const paymentMethods = ['微信', '支付宝', '信用卡', '现金', '其他']

const l1Categories = computed(() => categories.value.filter((c) => !c.parent_id))
const currentChildren = computed(() => {
  if (!selectedL1.value) return []
  return categories.value.filter((c) => c.parent_id === selectedL1.value.id)
})

const selectedCatLabel = computed(() => {
  if (!form.value.category_id) return selectedL1.value ? selectedL1.value.name : ''
  const child = categories.value.find((c) => c.id === form.value.category_id)
  if (!child) return ''
  const parent = l1Categories.value.find((c) => c.id === child.parent_id)
  return parent ? `${parent.name} / ${child.name}` : child.name
})

function selectL1(cat) {
  selectedL1.value = cat
  // 如果一级本身作为叶节点（无子分类），直接设为 category_id
  const children = categories.value.filter((c) => c.parent_id === cat.id)
  if (children.length === 0) {
    form.value.category_id = cat.id
  } else {
    form.value.category_id = null
  }
}

function selectL2(cat) {
  form.value.category_id = cat.id
}

async function loadCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function loadAssetCategoryIds() {
  try {
    const res = await getAssets()
    assetCategoryIdSet.value = new Set(res.data.map((row) => row.category_id).filter(Boolean))
  } catch (e) {
    console.error(e)
  }
}

async function loadEdit() {
  try {
    const res = await getTransactions({ })
    const tx = res.data.find((t) => t.id === Number(route.params.id))
    if (!tx) {
      ElMessage.error('记账记录不存在')
      router.replace('/bills')
      return
    }
    form.value.type = tx.type
    amountStr.value = String(Number(tx.amount).toFixed(2))
    form.value.category_id = tx.category_id
    form.value.date = tx.date
    form.value.payment_method = tx.payment_method || '微信'
    form.value.notes = tx.notes || ''

    if (tx.category_id) {
      const cat = categories.value.find((c) => c.id === tx.category_id)
      if (cat) {
        if (cat.parent_id) {
          selectedL1.value = categories.value.find((c) => c.id === cat.parent_id) || null
        } else {
          selectedL1.value = cat
        }
      }
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('加载编辑数据失败')
  }
}

async function handleSubmit() {
  const amount = Number(amountStr.value)
  if (!amountStr.value || isNaN(amount) || amount <= 0) {
    ElMessage.warning('请输入有效金额')
    return
  }

  submitting.value = true
  try {
    const payload = {
      amount,
      type: form.value.type,
      category_id: form.value.category_id || null,
      date: form.value.date,
      payment_method: form.value.payment_method || null,
      notes: form.value.notes || null,
    }

    if (isEdit.value) {
      await updateTransaction(route.params.id, payload)
      ElMessage.success('记账已更新')
      router.push('/bills')
    } else {
      await createTransaction(payload)
      ElMessage.success('记账已保存')
      const shouldPrompt = payload.type === 'expense' && isCategoryWithAssetRecord(payload.category_id)
      if (shouldPrompt) {
        const goToAsset = await confirmCreateAssetFromBill(payload)
        if (goToAsset) {
          router.push({
            path: '/assets/new',
            query: {
              from: 'bill',
              amount: String(payload.amount),
              purchase_date: payload.date,
              category_id: payload.category_id ? String(payload.category_id) : '',
              notes: payload.notes || `来自记账：${selectedCatLabel.value || '资产相关支出'}`,
            },
          })
          return
        }
      }
      router.push('/bills')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

function isCategoryWithAssetRecord(categoryId) {
  if (!categoryId) return false
  if (assetCategoryIdSet.value.has(categoryId)) return true
  const children = categories.value.filter((c) => c.parent_id === categoryId)
  return children.some((child) => assetCategoryIdSet.value.has(child.id))
}

async function confirmCreateAssetFromBill(payload) {
  try {
    await ElMessageBox.confirm(
      '检测到该分类已有资产记录，是否同时新增一条资产记录？',
      '资产相关提醒',
      {
        confirmButtonText: '去新增资产',
        cancelButtonText: '暂不',
        type: 'info',
      }
    )
    return true
  } catch {
    return false
  }
}

function goBack() {
  router.push('/bills')
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadAssetCategoryIds()])
  if (isEdit.value) await loadEdit()
})
</script>

<style scoped>
.bill-form-page {
  width: 100%;
  max-width: 560px;
}

.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: color var(--transition), background var(--transition);
}
.back-btn:hover { color: var(--accent); background: var(--accent-light); }

.form-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Type tabs */
.type-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.type-tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: color var(--transition), border-bottom var(--transition);
  border-bottom: 2px solid transparent;
}

.type-tab.active.expense { color: var(--danger); border-bottom-color: var(--danger); }
.type-tab.active.income  { color: var(--success); border-bottom-color: var(--success); }

/* Amount */
.amount-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 28px 24px 16px;
}

.currency-sign {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-secondary);
}

.amount-input {
  border: none;
  outline: none;
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary);
  background: transparent;
  width: 220px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
.amount-input.expense { color: var(--danger); }
.amount-input.income  { color: var(--success); }
.amount-input::placeholder { color: var(--text-muted); }
.amount-input::-webkit-outer-spin-button,
.amount-input::-webkit-inner-spin-button { -webkit-appearance: none; }

/* Fields */
.fields { padding: 0 24px 8px; display: flex; flex-direction: column; gap: 16px; }

.field-group { display: flex; flex-direction: column; gap: 6px; }

.field-label { font-size: 12px; font-weight: 700; color: var(--text-secondary); letter-spacing: 0.5px; text-transform: uppercase; }

.field-input {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-card);
  outline: none;
  transition: border-color var(--transition);
  width: 180px;
}
.field-input:focus { border-color: var(--accent); }

.field-textarea {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-card);
  outline: none;
  resize: vertical;
  font-family: inherit;
  transition: border-color var(--transition);
}
.field-textarea:focus { border-color: var(--accent); }

/* Category selector */
.cat-selector { display: flex; flex-direction: column; gap: 8px; }
.cat-level { display: flex; align-items: flex-start; gap: 8px; }
.level-hint { font-size: 11px; color: var(--text-muted); padding-top: 6px; min-width: 24px; }
.cat-chips { display: flex; flex-wrap: wrap; gap: 6px; }

.cat-chip {
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}
.cat-chip:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
.cat-chip.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.cat-chip.sub.active { background: #7c5cfc; border-color: #7c5cfc; }
.chip-asset-flag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 6px;
  padding: 0 5px;
  height: 16px;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.15);
  color: #b45309;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
}
.cat-chip.active .chip-asset-flag {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.selected-cat { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

/* Payment method */
.method-chips { display: flex; flex-wrap: wrap; gap: 6px; }

.method-chip {
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 7px;
  padding: 5px 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}
.method-chip:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
.method-chip.active { background: var(--accent-light); color: var(--accent); border-color: var(--accent); font-weight: 700; }

/* Footer */
.form-footer {
  display: flex;
  gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
}

.btn-cancel {
  flex: 1;
  height: 42px;
  border: 1px solid var(--border-color);
  background: transparent;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition);
}
.btn-cancel:hover { border-color: var(--accent); color: var(--accent); }

.btn-submit {
  flex: 2;
  height: 42px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  transition: filter var(--transition);
  background: var(--accent-gradient);
}
.btn-submit.expense { background: linear-gradient(135deg, #ef4444 0%, #f97316 100%); }
.btn-submit.income  { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.btn-submit:hover:not(:disabled) { filter: brightness(1.06); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
