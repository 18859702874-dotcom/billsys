<template>
  <div class="clothing-form-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        返回
      </button>
      <h1>{{ isEdit ? '编辑服装' : '添加服装' }}</h1>
    </div>

    <div class="form-layout">
      <div class="form-main">
        <div class="form-card">
          <h2 class="section-title">基本信息</h2>

          <div class="form-grid">
            <div class="form-group">
              <label>服装名称 <span class="required">*</span></label>
              <input v-model="form.name" class="form-input" placeholder="例如：白色 T 恤" />
            </div>

            <div class="form-group">
              <label>分类 <span class="required">*</span></label>
              <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
                <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
              </el-select>
            </div>

            <div class="form-group">
              <label>颜色</label>
              <el-select v-model="form.color" placeholder="选择颜色" filterable allow-create style="width: 100%">
                <el-option v-for="c in colorOptions" :key="c" :label="c" :value="c" />
              </el-select>
            </div>

            <div class="form-group">
              <label>品牌</label>
              <input v-model="form.brand" class="form-input" placeholder="品牌名称" />
            </div>

            <div class="form-group">
              <label>购买价格</label>
              <div class="input-with-prefix">
                <span class="input-prefix">¥</span>
                <input v-model.number="form.purchase_price" type="number" min="0" step="0.01" class="form-input has-prefix" />
              </div>
            </div>

            <div class="form-group">
              <label>购买日期</label>
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
                style="width: 100%"
              />
            </div>

            <div class="form-group">
              <label>购买渠道</label>
              <el-select v-model="form.purchase_channel" placeholder="选择渠道" filterable allow-create style="width: 100%">
                <el-option v-for="ch in channelOptions" :key="ch" :label="ch" :value="ch" />
              </el-select>
            </div>

            <div class="form-group">
              <label>适用季节</label>
              <el-select v-model="form.season" placeholder="选择季节" style="width: 100%">
                <el-option v-for="s in seasonOptions" :key="s" :label="s" :value="s" />
              </el-select>
            </div>
          </div>

          <div class="form-group full-width">
            <label>备注</label>
            <textarea v-model="form.notes" class="form-textarea" rows="3" placeholder="添加备注..." />
          </div>
        </div>
      </div>

      <div class="form-side">
        <div class="form-card ai-card">
          <h2 class="section-title">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="18"
              height="18"
              style="vertical-align: -3px; margin-right: 6px; color: var(--accent)"
            >
              <path d="M12 2a5 5 0 015 5v1H7V7a5 5 0 015-5z" />
              <path d="M4 10l2 11h12l2-11" />
              <circle cx="12" cy="15" r="2" />
            </svg>
            AI 智能识别
          </h2>
          <p class="ai-desc">上传订单截图，自动识别订单中的多件商品，可勾选后批量导入。</p>

          <div
            class="ai-upload-area"
            :class="{ recognizing }"
            @click="aiInput?.click()"
            @dragover.prevent
            @drop.prevent="onAiDrop"
          >
            <div v-if="recognizing" class="ai-loading">
              <div class="spinner" />
              <p>AI 识别中...</p>
            </div>
            <div v-else-if="aiPreview" class="ai-preview-wrap">
              <img :src="aiPreview" class="ai-preview-img" alt="订单截图预览" />
              <div class="ai-recognized-badge">已识别</div>
            </div>
            <div v-else class="ai-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <p>点击上传订单截图</p>
            </div>
          </div>
          <input ref="aiInput" type="file" accept="image/*" style="display: none" @change="onAiFileChange" />

          <div v-if="recognizedItems.length" class="recognized-hint">
            最近一次识别到 {{ recognizedItems.length }} 件商品
            <button class="mini-link" @click="recognizedDialogVisible = true">查看并导入</button>
          </div>
        </div>

        <div class="form-card">
          <h2 class="section-title">服装图片</h2>
          <div
            class="upload-area"
            :class="{ 'has-image': previewUrl }"
            @click="triggerUpload"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <img v-if="previewUrl" :src="previewUrl" class="preview-image" alt="服装图" />
            <div v-else class="upload-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p>点击或拖拽上传图片</p>
              <span>支持 JPG、PNG</span>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleFileChange" />
          <button v-if="previewUrl" class="remove-image-btn" @click="removeImage">移除图片</button>
        </div>

        <div class="form-card actions-card">
          <button class="btn-primary full" @click="handleSubmit" :disabled="saving || importing">
            {{ saving ? '保存中...' : (isEdit ? '更新' : '添加') }}
          </button>
          <button class="btn-secondary full" @click="$router.back()">取消</button>
        </div>
      </div>
    </div>

    <el-dialog v-model="recognizedDialogVisible" title="识别结果（多商品）" width="960px" :close-on-click-modal="false">
      <div v-if="recognizedOrder.order_no || recognizedOrder.purchase_date || recognizedOrder.purchase_channel" class="recognized-meta">
        <span v-if="recognizedOrder.order_no">订单号：{{ recognizedOrder.order_no }}</span>
        <span v-if="recognizedOrder.purchase_date">日期：{{ recognizedOrder.purchase_date }}</span>
        <span v-if="recognizedOrder.purchase_channel">渠道：{{ recognizedOrder.purchase_channel }}</span>
      </div>

      <div class="recognized-actions">
        <label class="check-all">
          <input type="checkbox" :checked="allSelected" @change="toggleSelectAll($event)" />
          全选
        </label>
        <span>已选 {{ selectedRecognizedCount }} / {{ recognizedItems.length }}</span>
      </div>

      <div class="recognized-table-wrap">
        <table class="recognized-table">
          <thead>
            <tr>
              <th style="width: 52px">选择</th>
              <th>名称</th>
              <th style="width: 120px">分类</th>
              <th style="width: 110px">颜色</th>
              <th style="width: 110px">品牌</th>
              <th style="width: 110px">单价</th>
              <th style="width: 90px">数量</th>
              <th style="width: 120px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in recognizedItems" :key="item._id">
              <td>
                <input type="checkbox" v-model="item.selected" />
              </td>
              <td>
                <input v-model="item.name" class="table-input" />
              </td>
              <td>
                <select v-model="item.category" class="table-input">
                  <option v-for="c in categoryOptions" :key="c" :value="c">{{ c }}</option>
                </select>
              </td>
              <td>
                <input v-model="item.color" class="table-input" />
              </td>
              <td>
                <input v-model="item.brand" class="table-input" />
              </td>
              <td>
                <input v-model.number="item.purchase_price" class="table-input" type="number" min="0" step="0.01" />
              </td>
              <td>
                <input v-model.number="item.qty" class="table-input" type="number" min="1" step="1" />
              </td>
              <td>
                <button class="mini-btn" @click="applyItemToForm(item)">填入表单</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <template #footer>
        <el-button @click="recognizedDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="importing" @click="importRecognizedItems">
          批量导入已选（{{ selectedRecognizedCount }}）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createClothing, createClothingBatch, getClothing, recognizeClothing, updateClothing } from '../api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const importing = ref(false)

const form = ref({
  name: '',
  category: '',
  color: '',
  brand: '',
  purchase_price: null,
  purchase_date: '',
  purchase_channel: '',
  season: '',
  notes: '',
})

const imageFile = ref(null)
const previewUrl = ref('')
const fileInput = ref(null)
const aiInput = ref(null)
const recognizing = ref(false)
const aiPreview = ref('')

const recognizedDialogVisible = ref(false)
const recognizedOrder = ref({
  order_no: '',
  purchase_date: '',
  purchase_channel: '',
})
const recognizedItems = ref([])

const categoryOptions = ['上衣', '下装', '外套', '鞋子', '配饰']
const seasonOptions = ['春', '夏', '秋', '冬', '四季']
const colorOptions = ['黑色', '白色', '灰色', '红色', '蓝色', '绿色', '黄色', '粉色', '紫色', '棕色', '米色', '藏青']
const channelOptions = ['淘宝', '京东', '拼多多', '线下门店', '海外代购', '直播购买', '闲鱼']

const selectedRecognizedCount = computed(() => recognizedItems.value.filter((x) => x.selected).length)
const allSelected = computed(() => recognizedItems.value.length > 0 && selectedRecognizedCount.value === recognizedItems.value.length)

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

function normalizeRecognizedItem(raw, order) {
  const category = categoryOptions.includes(raw.category) ? raw.category : '上衣'
  const season = seasonOptions.includes(raw.season) ? raw.season : ''
  const qty = Math.max(1, Number.parseInt(raw.qty || 1, 10) || 1)

  return {
    _id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    selected: true,
    name: String(raw.name || '').trim(),
    category,
    color: raw.color || '',
    brand: raw.brand || '',
    purchase_price: toNumber(raw.purchase_price),
    purchase_date: raw.purchase_date || order.purchase_date || '',
    purchase_channel: raw.purchase_channel || order.purchase_channel || '',
    season,
    qty,
    notes: raw.notes || '',
  }
}

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) setImage(file)
}

function handleDrop(e) {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) setImage(file)
}

function setImage(file) {
  imageFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function removeImage() {
  imageFile.value = null
  previewUrl.value = ''
}

function onAiFileChange(e) {
  const file = e.target.files?.[0]
  if (file) doRecognize(file)
}

function onAiDrop(e) {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) doRecognize(file)
}

function applyItemToForm(item) {
  form.value.name = item.name || form.value.name
  form.value.category = item.category || form.value.category
  form.value.color = item.color || form.value.color
  form.value.brand = item.brand || form.value.brand
  if (item.purchase_price != null) form.value.purchase_price = Number(item.purchase_price)
  form.value.purchase_date = item.purchase_date || form.value.purchase_date
  form.value.purchase_channel = item.purchase_channel || form.value.purchase_channel
  form.value.season = item.season || form.value.season
  if (item.notes) {
    form.value.notes = form.value.notes ? `${form.value.notes}\n${item.notes}` : item.notes
  }
  recognizedDialogVisible.value = false
  ElMessage.success('已填充到当前表单')
}

function toggleSelectAll(event) {
  const checked = !!event.target.checked
  for (const item of recognizedItems.value) {
    item.selected = checked
  }
}

async function doRecognize(file) {
  aiPreview.value = URL.createObjectURL(file)
  recognizing.value = true

  try {
    const fd = new FormData()
    fd.append('image', file)
    const res = await recognizeClothing(fd)
    const data = res.data || {}

    const order = {
      order_no: data.order?.order_no || '',
      purchase_date: data.order?.purchase_date || '',
      purchase_channel: data.order?.purchase_channel || '',
    }

    let items = Array.isArray(data.items) ? data.items : []
    if (!items.length && (data.name || data.category)) {
      items = [data]
    }

    const normalized = items
      .map((x) => normalizeRecognizedItem(x, order))
      .filter((x) => x.name)

    if (!normalized.length) {
      ElMessage.warning('未识别到可导入商品，请更换截图重试')
      return
    }

    recognizedOrder.value = order
    recognizedItems.value = normalized

    if (normalized.length === 1) {
      applyItemToForm(normalized[0])
      return
    }

    if (isEdit.value) {
      applyItemToForm(normalized[0])
      ElMessage.warning(`识别到 ${normalized.length} 件商品。编辑页仅填充第一件。`)
      return
    }

    recognizedDialogVisible.value = true
    ElMessage.success(`识别到 ${normalized.length} 件商品，请确认后批量导入`)    
  } catch (err) {
    const msg = err?.response?.data?.detail || 'AI 识别失败'
    ElMessage.error(msg)
  } finally {
    recognizing.value = false
  }
}

async function importRecognizedItems() {
  if (isEdit.value) {
    ElMessage.warning('编辑模式不支持批量导入')
    return
  }

  const selected = recognizedItems.value.filter((x) => x.selected && x.name && x.category)
  if (!selected.length) {
    ElMessage.warning('请至少勾选一件有效商品')
    return
  }

  const flattened = []
  for (const item of selected) {
    const qty = Math.max(1, Number.parseInt(item.qty || 1, 10) || 1)
    for (let i = 0; i < qty; i += 1) {
      const notes = []
      if (item.notes) notes.push(item.notes)
      if (recognizedOrder.value.order_no) notes.push(`订单号: ${recognizedOrder.value.order_no}`)
      if (qty > 1) notes.push(`同款第 ${i + 1}/${qty} 件`)

      flattened.push({
        name: item.name,
        category: item.category,
        color: item.color || null,
        brand: item.brand || null,
        purchase_price: item.purchase_price != null ? Number(item.purchase_price) : null,
        purchase_date: item.purchase_date || recognizedOrder.value.purchase_date || null,
        purchase_channel: item.purchase_channel || recognizedOrder.value.purchase_channel || null,
        season: item.season || null,
        notes: notes.length ? notes.join('；') : null,
      })
    }
  }

  if (!flattened.length) {
    ElMessage.warning('没有可导入数据')
    return
  }

  importing.value = true
  try {
    const chunkSize = 200
    for (let i = 0; i < flattened.length; i += chunkSize) {
      const chunk = flattened.slice(i, i + chunkSize)
      await createClothingBatch({ items: chunk })
    }

    ElMessage.success(`批量导入成功，共 ${flattened.length} 条`) 
    recognizedDialogVisible.value = false
    router.push('/clothing')
  } catch (err) {
    const msg = err?.response?.data?.detail || '批量导入失败'
    ElMessage.error(msg)
  } finally {
    importing.value = false
  }
}

async function handleSubmit() {
  if (!form.value.name || !form.value.category) {
    ElMessage.warning('请填写服装名称和分类')
    return
  }

  saving.value = true
  let requestPromise
  try {
    const fd = new FormData()
    for (const [key, val] of Object.entries(form.value)) {
      if (val !== null && val !== '' && val !== undefined) {
        fd.append(key, val)
      }
    }

    if (imageFile.value) {
      fd.append('image', imageFile.value)
    }

    if (isEdit.value) {
      requestPromise = updateClothing(route.params.id, fd)
      ElMessage.success('已提交更新，后台处理中')
    } else {
      requestPromise = createClothing(fd)
      ElMessage.success('已提交添加，后台处理中')
    }
    router.push('/clothing')
  } catch (err) {
    const msg = err?.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }

  if (requestPromise) {
    requestPromise.catch((err) => {
      const msg = err?.response?.data?.detail || '保存失败'
      ElMessage.error(`后台保存失败：${msg}`)
    })
  }
}

onMounted(async () => {
  if (!isEdit.value) return

  const res = await getClothing(route.params.id)
  const data = res.data
  form.value = {
    name: data.name,
    category: data.category,
    color: data.color || '',
    brand: data.brand || '',
    purchase_price: data.purchase_price ? Number(data.purchase_price) : null,
    purchase_date: data.purchase_date || '',
    purchase_channel: data.purchase_channel || '',
    season: data.season || '',
    notes: data.notes || '',
  }
  if (data.image_url) {
    previewUrl.value = data.image_url
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 700;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.back-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.form-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
}

.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group.full-width {
  margin-top: 16px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.required {
  color: var(--danger);
}

.form-input {
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
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
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
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

.form-textarea {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  resize: vertical;
  width: 100%;
  font-family: inherit;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.form-textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition), background var(--transition);
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--accent);
  background: var(--accent-light);
}

.upload-area.has-image {
  padding: 8px;
  border-style: solid;
}

.upload-placeholder {
  color: var(--text-muted);
}

.upload-placeholder p {
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
}

.upload-placeholder span {
  font-size: 12px;
  display: block;
  margin-top: 4px;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.remove-image-btn {
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--danger);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition);
}

.remove-image-btn:hover {
  background: var(--danger-light);
  border-color: var(--danger);
}

.actions-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0 20px;
  height: 42px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition);
}

.btn-primary:hover {
  filter: brightness(1.08);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary.full {
  width: 100%;
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0 20px;
  height: 42px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.btn-secondary:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.btn-secondary.full {
  width: 100%;
}

.ai-card {
  border-color: var(--accent);
  border-style: solid;
  background: linear-gradient(180deg, var(--accent-light) 0%, var(--bg-card) 100%);
}

.ai-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  line-height: 1.5;
}

.ai-upload-area {
  border: 2px dashed var(--accent);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: background var(--transition);
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-upload-area:hover {
  background: var(--accent-light);
}

.ai-upload-area.recognizing {
  pointer-events: none;
  opacity: 0.8;
}

.ai-placeholder {
  color: var(--accent);
}

.ai-placeholder p {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 500;
}

.ai-loading {
  color: var(--accent);
}

.ai-loading p {
  margin-top: 10px;
  font-size: 13px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.ai-preview-wrap {
  position: relative;
}

.ai-preview-img {
  max-width: 100%;
  max-height: 120px;
  border-radius: 8px;
  object-fit: contain;
}

.ai-recognized-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--success);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.recognized-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
}

.mini-link {
  border: none;
  background: none;
  color: var(--accent);
  cursor: pointer;
  margin-left: 8px;
}

.recognized-meta {
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.recognized-actions {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--text-secondary);
}

.check-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.recognized-table-wrap {
  max-height: 420px;
  overflow: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.recognized-table {
  width: 100%;
  border-collapse: collapse;
}

.recognized-table th,
.recognized-table td {
  border-bottom: 1px solid var(--border-color);
  padding: 8px;
  text-align: left;
  vertical-align: middle;
  font-size: 13px;
}

.recognized-table th {
  background: #f8f9fd;
  color: var(--text-secondary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-input {
  width: 100%;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0 8px;
  font-size: 13px;
}

.mini-btn {
  height: 30px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.mini-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.clothing-form-page :deep(.el-select__wrapper),
.clothing-form-page :deep(.el-date-editor .el-input__wrapper) {
  min-height: 40px;
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid var(--border-color);
  font-size: 14px;
}

@media (max-width: 900px) {
  .form-layout {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
