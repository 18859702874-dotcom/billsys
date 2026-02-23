<template>
  <div class="outfit-editor-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        返回
      </button>
      <h1>{{ isEdit ? '编辑搭配' : '新建搭配' }}</h1>
    </div>

    <div class="editor-layout">
      <!-- Left: Wardrobe panel -->
      <div class="wardrobe-panel">
        <h2 class="panel-title">我的衣柜</h2>
        <div class="wardrobe-filters">
          <el-select v-model="wardrobeCategory" placeholder="全部分类" clearable size="small" @change="loadWardrobe">
            <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
        <div class="wardrobe-list">
          <div
            v-for="item in wardrobeItems"
            :key="item.id"
            class="wardrobe-item"
            draggable="true"
            @dragstart="onDragStart($event, item)"
          >
            <div class="wardrobe-thumb">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
              <div v-else class="thumb-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
                  <path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/>
                  <path d="M12 2v7"/>
                </svg>
              </div>
            </div>
            <span class="wardrobe-name">{{ item.name }}</span>
          </div>
          <div v-if="!wardrobeItems.length" class="wardrobe-empty">
            暂无服装
          </div>
        </div>
      </div>

      <!-- Right: Canvas + Info -->
      <div class="editor-main">
        <div class="outfit-info">
          <div class="info-row">
            <div class="form-group">
              <label>搭配名称 <span class="required">*</span></label>
              <input v-model="form.name" class="form-input" placeholder="例：日常休闲搭配" />
            </div>
            <div class="form-group">
              <label>场合</label>
              <el-select v-model="form.occasion" placeholder="选择场合" clearable style="width: 100%">
                <el-option v-for="o in occasionOptions" :key="o" :label="o" :value="o" />
              </el-select>
            </div>
            <div class="form-group">
              <label>季节</label>
              <el-select v-model="form.season" placeholder="选择季节" clearable style="width: 100%">
                <el-option v-for="s in seasonOptions" :key="s" :label="s" :value="s" />
              </el-select>
            </div>
          </div>
        </div>

        <div
          class="canvas-area"
          @dragover.prevent
          @drop.prevent="onCanvasDrop"
        >
          <div class="canvas-hint" v-if="!canvasItems.length">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
            <p>从左侧衣柜拖拽服装到这里</p>
          </div>

          <div
            v-for="(ci, idx) in canvasItems"
            :key="ci.clothing.id + '-' + idx"
            class="canvas-item"
            :style="{ left: ci.position_x + 'px', top: ci.position_y + 'px', transform: `scale(${ci.scale})` }"
            @mousedown.prevent="startDrag($event, idx)"
          >
            <div class="canvas-item-image">
              <img v-if="ci.clothing.image_url" :src="ci.clothing.image_url" :alt="ci.clothing.name" />
              <div v-else class="canvas-item-placeholder">{{ ci.clothing.name }}</div>
            </div>
            <div class="canvas-item-label">{{ ci.clothing.name }}</div>
            <button class="canvas-item-remove" @click.stop="removeCanvasItem(idx)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <div class="canvas-item-scale">
              <button @click.stop="scaleItem(idx, -0.1)">-</button>
              <span>{{ Math.round(ci.scale * 100) }}%</span>
              <button @click.stop="scaleItem(idx, 0.1)">+</button>
            </div>
          </div>
        </div>

        <div class="editor-actions">
          <button class="btn-primary" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : '保存搭配' }}
          </button>
          <button class="btn-secondary" @click="$router.back()">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getClothingList, getOutfit, createOutfit, updateOutfit } from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

const form = ref({ name: '', occasion: '', season: '', notes: '' })
const canvasItems = ref([])
const wardrobeItems = ref([])
const wardrobeCategory = ref('')

const categoryOptions = ['上衣', '下装', '外套', '鞋子', '配饰']
const occasionOptions = ['日常', '通勤', '运动', '约会', '正式']
const seasonOptions = ['春', '夏', '秋', '冬', '四季']

// Dragging state
let dragClothing = null
let dragIdx = -1
let dragOffset = { x: 0, y: 0 }

async function loadWardrobe() {
  const params = {}
  if (wardrobeCategory.value) params.category = wardrobeCategory.value
  const res = await getClothingList(params)
  wardrobeItems.value = res.data
}

function onDragStart(e, item) {
  dragClothing = item
  e.dataTransfer.effectAllowed = 'copy'
}

function onCanvasDrop(e) {
  if (!dragClothing) return
  const canvas = e.currentTarget.getBoundingClientRect()
  canvasItems.value.push({
    clothing: dragClothing,
    clothing_id: dragClothing.id,
    position_x: Math.round(e.clientX - canvas.left - 60),
    position_y: Math.round(e.clientY - canvas.top - 60),
    scale: 1.0,
  })
  dragClothing = null
}

function startDrag(e, idx) {
  dragIdx = idx
  const item = canvasItems.value[idx]
  dragOffset = {
    x: e.clientX - item.position_x,
    y: e.clientY - item.position_y,
  }
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(e) {
  if (dragIdx < 0) return
  canvasItems.value[dragIdx].position_x = e.clientX - dragOffset.x
  canvasItems.value[dragIdx].position_y = e.clientY - dragOffset.y
}

function onMouseUp() {
  dragIdx = -1
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

function removeCanvasItem(idx) {
  canvasItems.value.splice(idx, 1)
}

function scaleItem(idx, delta) {
  const item = canvasItems.value[idx]
  item.scale = Math.max(0.3, Math.min(2.0, +(item.scale + delta).toFixed(1)))
}

async function handleSave() {
  if (!form.value.name) {
    ElMessage.warning('请输入搭配名称')
    return
  }
  if (!canvasItems.value.length) {
    ElMessage.warning('请至少添加一件服装')
    return
  }

  saving.value = true
  try {
    const payload = {
      ...form.value,
      items: canvasItems.value.map(ci => ({
        clothing_id: ci.clothing_id || ci.clothing.id,
        position_x: Math.round(ci.position_x),
        position_y: Math.round(ci.position_y),
        scale: ci.scale,
      })),
    }

    if (isEdit.value) {
      await updateOutfit(route.params.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createOutfit(payload)
      ElMessage.success('创建成功')
    }
    router.push('/outfits')
  } catch (err) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadWardrobe()
  if (isEdit.value) {
    const res = await getOutfit(route.params.id)
    const data = res.data
    form.value = {
      name: data.name,
      occasion: data.occasion || '',
      season: data.season || '',
      notes: data.notes || '',
    }
    canvasItems.value = (data.items || []).map(item => ({
      clothing: item.clothing,
      clothing_id: item.clothing_id,
      position_x: item.position_x,
      position_y: item.position_y,
      scale: Number(item.scale),
    }))
  }
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
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
.back-btn:hover { border-color: var(--accent); color: var(--accent); }

.editor-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
  height: calc(100vh - 140px);
}

/* Wardrobe Panel */
.wardrobe-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 16px;
  overflow-y: auto;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}
.wardrobe-filters { margin-bottom: 12px; }
.wardrobe-filters :deep(.el-select) { width: 100%; }

.wardrobe-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.wardrobe-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: grab;
  transition: var(--transition);
}
.wardrobe-item:hover {
  border-color: var(--accent);
  background: var(--accent-light);
}
.wardrobe-item:active { cursor: grabbing; }

.wardrobe-thumb {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  overflow: hidden;
  background: #f3f4f6;
  flex-shrink: 0;
}
.wardrobe-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
.wardrobe-name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.wardrobe-empty {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
  font-size: 13px;
}

/* Editor Main */
.editor-main { display: flex; flex-direction: column; gap: 16px; }

.outfit-info {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 16px 20px;
}
.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}
.required { color: var(--danger); }
.form-input {
  height: 38px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  background: var(--bg-card);
  width: 100%;
  transition: border-color var(--transition);
}
.form-input:focus { border-color: var(--accent); }

.outfit-editor-page :deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid var(--border-color);
  font-size: 14px;
}

/* Canvas */
.canvas-area {
  flex: 1;
  background: var(--bg-card);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius);
  position: relative;
  overflow: hidden;
  min-height: 400px;
}

.canvas-hint {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  gap: 12px;
  pointer-events: none;
}
.canvas-hint p { font-size: 14px; }

.canvas-item {
  position: absolute;
  width: 120px;
  cursor: move;
  transform-origin: center center;
  user-select: none;
}
.canvas-item-image {
  width: 120px;
  height: 150px;
  border-radius: 10px;
  overflow: hidden;
  background: #f3f4f6;
  border: 2px solid var(--border-color);
  transition: border-color var(--transition);
}
.canvas-item:hover .canvas-item-image {
  border-color: var(--accent);
}
.canvas-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.canvas-item-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 8px;
}
.canvas-item-label {
  text-align: center;
  font-size: 11px;
  font-weight: 500;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.canvas-item-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--danger);
  color: #fff;
  border: 2px solid var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--transition);
}
.canvas-item:hover .canvas-item-remove { opacity: 1; }

.canvas-item-scale {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity var(--transition);
}
.canvas-item:hover .canvas-item-scale { opacity: 1; }
.canvas-item-scale button {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}
.canvas-item-scale button:hover {
  border-color: var(--accent);
  color: var(--accent);
}
.canvas-item-scale span {
  font-size: 10px;
  color: var(--text-muted);
  min-width: 32px;
  text-align: center;
}

.editor-actions {
  display: flex;
  gap: 12px;
}
.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0 28px;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition);
}
.btn-primary:hover { filter: brightness(1.08); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0 28px;
  height: 40px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.btn-secondary:hover { border-color: var(--accent); color: var(--accent); }

@media (max-width: 900px) {
  .editor-layout { grid-template-columns: 1fr; height: auto; }
  .wardrobe-panel { max-height: 200px; }
  .info-row { grid-template-columns: 1fr; }
}
</style>
