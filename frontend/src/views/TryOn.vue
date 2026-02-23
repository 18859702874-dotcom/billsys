<template>
  <div class="tryon-page">
    <div class="page-header">
      <h1>AI 换装</h1>
      <p class="subtitle">上传你的照片，选择衣柜中的服装，体验虚拟试穿</p>
    </div>

    <div class="tryon-layout">
      <!-- Left: Person photo -->
      <div class="tryon-card">
        <h2 class="section-title">人物照片</h2>
        <div
          class="upload-area"
          :class="{ 'has-image': personPreview }"
          @click="$refs.personInput.click()"
          @dragover.prevent
          @drop.prevent="onDropPerson"
        >
          <img v-if="personPreview" :src="personPreview" class="preview-image" />
          <div v-else class="upload-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <p>点击或拖拽上传人物照片</p>
            <span>建议使用正面全身照</span>
          </div>
        </div>
        <input ref="personInput" type="file" accept="image/*" style="display:none" @change="onPersonChange" />
      </div>

      <!-- Center: Result -->
      <div class="tryon-card result-card">
        <h2 class="section-title">换装结果</h2>
        <div class="result-area">
          <div v-if="resultMessage" class="result-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <p>{{ resultMessage }}</p>
          </div>
          <div v-else-if="loading" class="result-loading">
            <div class="spinner"></div>
            <p>AI 正在换装中...</p>
          </div>
          <div v-else class="result-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <path d="M12 2a5 5 0 015 5v1H7V7a5 5 0 015-5z"/>
              <path d="M4 10l2 11h12l2-11"/>
              <circle cx="12" cy="15" r="2"/>
            </svg>
            <p>上传照片并选择服装后点击「开始换装」</p>
          </div>
        </div>

        <button
          class="btn-primary full"
          @click="handleTryOn"
          :disabled="!personFile || !selectedClothing || loading"
        >
          {{ loading ? '换装中...' : '开始换装' }}
        </button>
      </div>

      <!-- Right: Clothing selection -->
      <div class="tryon-card">
        <h2 class="section-title">选择服装</h2>
        <el-select v-model="clothingCategory" placeholder="全部分类" clearable size="small" @change="loadClothing" style="width:100%;margin-bottom:12px">
          <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <div class="clothing-select-list">
          <div
            v-for="item in clothingItems"
            :key="item.id"
            class="select-item"
            :class="{ selected: selectedClothing?.id === item.id }"
            @click="selectedClothing = item"
          >
            <div class="select-thumb">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
              <div v-else class="thumb-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
                  <path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/>
                  <path d="M12 2v7"/>
                </svg>
              </div>
            </div>
            <span class="select-name">{{ item.name }}</span>
            <div v-if="selectedClothing?.id === item.id" class="check-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>
          <div v-if="!clothingItems.length" class="select-empty">
            暂无服装，请先去衣柜添加
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getClothingList, submitTryOn } from '../api'

const personFile = ref(null)
const personPreview = ref('')
const selectedClothing = ref(null)
const clothingItems = ref([])
const clothingCategory = ref('')
const loading = ref(false)
const resultMessage = ref('')

const categoryOptions = ['上衣', '下装', '外套', '鞋子', '配饰']

function onPersonChange(e) {
  const file = e.target.files[0]
  if (file) setPerson(file)
}

function onDropPerson(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) setPerson(file)
}

function setPerson(file) {
  personFile.value = file
  personPreview.value = URL.createObjectURL(file)
}

async function loadClothing() {
  const params = {}
  if (clothingCategory.value) params.category = clothingCategory.value
  const res = await getClothingList(params)
  clothingItems.value = res.data
}

async function handleTryOn() {
  if (!personFile.value) {
    ElMessage.warning('请先上传人物照片')
    return
  }
  if (!selectedClothing.value) {
    ElMessage.warning('请选择一件服装')
    return
  }

  loading.value = true
  resultMessage.value = ''
  try {
    const fd = new FormData()
    fd.append('person_image', personFile.value)
    fd.append('clothing_image_url', selectedClothing.value.image_url || '')
    const res = await submitTryOn(fd)
    resultMessage.value = res.data.message || 'AI换装功能即将接入，敬请期待！'
  } catch (err) {
    ElMessage.error('换装请求失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadClothing)
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 22px;
  font-weight: 700;
}
.subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.tryon-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 20px;
  align-items: start;
}

.tryon-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition), background var(--transition);
  min-height: 300px;
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
.upload-placeholder { color: var(--text-muted); }
.upload-placeholder p { margin-top: 12px; font-size: 14px; font-weight: 500; }
.upload-placeholder span { font-size: 12px; display: block; margin-top: 4px; }
.preview-image {
  max-width: 100%;
  max-height: 340px;
  border-radius: 8px;
  object-fit: contain;
}

/* Result area */
.result-card { display: flex; flex-direction: column; }
.result-area {
  flex: 1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  margin-bottom: 16px;
  background: #f8f9fd;
}
.result-placeholder, .result-loading, .result-message {
  text-align: center;
  color: var(--text-muted);
}
.result-placeholder p, .result-loading p, .result-message p {
  margin-top: 12px;
  font-size: 14px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  height: 42px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition);
}
.btn-primary:hover { filter: brightness(1.08); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary.full { width: 100%; }

/* Clothing selection */
.clothing-select-list {
  max-height: 380px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.select-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}
.select-item:hover { border-color: var(--accent); background: var(--accent-light); }
.select-item.selected { border-color: var(--accent); background: var(--accent-light); }

.select-thumb {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  overflow: hidden;
  background: #f3f4f6;
  flex-shrink: 0;
}
.select-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
.select-name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.check-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.select-empty {
  text-align: center;
  padding: 30px;
  color: var(--text-muted);
  font-size: 13px;
}

.tryon-page :deep(.el-select__wrapper) {
  min-height: 34px;
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid var(--border-color);
  font-size: 13px;
}

@media (max-width: 1100px) {
  .tryon-layout { grid-template-columns: 1fr; }
}
</style>
