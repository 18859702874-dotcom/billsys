<template>
  <div class="outfit-editor-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        返回
      </button>
      <div class="header-main">
        <h1>{{ isEdit ? '编辑部位搭配' : '新建部位搭配' }}</h1>
        <p>按部位放置衣物，结构化生成整身搭配</p>
      </div>
      <div class="header-badges">
        <span class="badge">已放置 {{ placedCount }} 件</span>
      </div>
    </div>

    <div class="editor-layout">
      <aside class="panel wardrobe-panel">
        <div class="panel-head">
          <h2>衣柜</h2>
          <span>拖拽到部位区</span>
        </div>

        <div class="wardrobe-tools">
          <input v-model.trim="wardrobeKeyword" class="search-input" placeholder="搜索名称" type="text" />
          <el-select v-model="wardrobeCategory" placeholder="全部分类" clearable size="small">
            <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
          </el-select>
        </div>

        <div class="wardrobe-list" v-loading="wardrobeLoading">
          <div
            v-for="item in filteredWardrobeItems"
            :key="item.id"
            class="wardrobe-item"
            draggable="true"
            @dragstart="onDragStart($event, item)"
          >
            <div class="wardrobe-thumb">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
              <div v-else class="thumb-empty">无图</div>
            </div>
            <div class="wardrobe-info">
              <div class="wardrobe-name">{{ item.name }}</div>
              <div class="wardrobe-meta">{{ item.category }}</div>
            </div>
          </div>
          <div v-if="!filteredWardrobeItems.length" class="wardrobe-empty">没有符合条件的衣物</div>
        </div>
      </aside>

      <section class="panel stage-panel">
        <div class="panel-head">
          <h2>部位搭配台</h2>
          <div class="stage-actions">
            <button class="mini-btn" @click="autoFillSlots">一键填充</button>
            <button class="mini-btn mini-btn-primary" @click="generateOutfitRender" :disabled="generatingRender || !placedCount">
              {{ generatingRender ? '生成中...' : 'AI生成整身图' }}
            </button>
            <button class="mini-btn" @click="clearSlots" :disabled="!placedCount">清空</button>
          </div>
        </div>

        <div class="mannequin-board">
          <div class="silhouette"></div>

          <div
            class="slot-zone zone-outer"
            :class="{ active: selectedSlot === 'outer', filled: !!slots.outer }"
            @click="selectedSlot = 'outer'"
            @dragover.prevent
            @drop.prevent="onDropToSlot('outer')"
          >
            <div class="slot-title">外套区</div>
            <div v-if="slots.outer" class="slot-item">
              <img v-if="slots.outer.image_url" :src="slots.outer.image_url" :alt="slots.outer.name" />
              <span>{{ slots.outer.name }}</span>
              <button @click.stop="removeSlot('outer')">移除</button>
            </div>
            <div v-else class="slot-empty">拖拽外套到此</div>
          </div>

          <div
            class="slot-zone zone-top"
            :class="{ active: selectedSlot === 'top', filled: !!slots.top }"
            @click="selectedSlot = 'top'"
            @dragover.prevent
            @drop.prevent="onDropToSlot('top')"
          >
            <div class="slot-title">上衣区</div>
            <div v-if="slots.top" class="slot-item">
              <img v-if="slots.top.image_url" :src="slots.top.image_url" :alt="slots.top.name" />
              <span>{{ slots.top.name }}</span>
              <button @click.stop="removeSlot('top')">移除</button>
            </div>
            <div v-else class="slot-empty">拖拽上衣到此</div>
          </div>

          <div
            class="slot-zone zone-bottom"
            :class="{ active: selectedSlot === 'bottom', filled: !!slots.bottom }"
            @click="selectedSlot = 'bottom'"
            @dragover.prevent
            @drop.prevent="onDropToSlot('bottom')"
          >
            <div class="slot-title">下装区</div>
            <div v-if="slots.bottom" class="slot-item">
              <img v-if="slots.bottom.image_url" :src="slots.bottom.image_url" :alt="slots.bottom.name" />
              <span>{{ slots.bottom.name }}</span>
              <button @click.stop="removeSlot('bottom')">移除</button>
            </div>
            <div v-else class="slot-empty">拖拽下装到此</div>
          </div>

          <div
            class="slot-zone zone-shoes"
            :class="{ active: selectedSlot === 'shoes', filled: !!slots.shoes }"
            @click="selectedSlot = 'shoes'"
            @dragover.prevent
            @drop.prevent="onDropToSlot('shoes')"
          >
            <div class="slot-title">鞋子区</div>
            <div v-if="slots.shoes" class="slot-item">
              <img v-if="slots.shoes.image_url" :src="slots.shoes.image_url" :alt="slots.shoes.name" />
              <span>{{ slots.shoes.name }}</span>
              <button @click.stop="removeSlot('shoes')">移除</button>
            </div>
            <div v-else class="slot-empty">拖拽鞋子到此</div>
          </div>
        </div>

        <div
          class="accessory-zone"
          :class="{ active: selectedSlot === 'accessory', filled: slots.accessory.length }"
          @click="selectedSlot = 'accessory'"
          @dragover.prevent
          @drop.prevent="onDropToSlot('accessory')"
        >
          <div class="slot-title">配饰区（最多3件）</div>
          <div v-if="slots.accessory.length" class="accessory-list">
            <div v-for="(item, idx) in slots.accessory" :key="item.id + '-' + idx" class="accessory-item">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
              <span>{{ item.name }}</span>
              <button @click.stop="removeAccessory(idx)">移除</button>
            </div>
          </div>
          <div v-else class="slot-empty">拖拽配饰到此</div>
        </div>
      </section>

      <aside class="panel inspector-panel">
        <div class="panel-head">
          <h2>搭配信息</h2>
          <span>保存前确认</span>
        </div>

        <div class="form-group">
          <label>搭配名称 <span class="required">*</span></label>
          <input v-model="form.name" class="form-input" placeholder="例如：周末出街" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>场合</label>
            <el-select v-model="form.occasion" placeholder="选择场合" clearable>
              <el-option v-for="o in occasionOptions" :key="o" :label="o" :value="o" />
            </el-select>
          </div>
          <div class="form-group">
            <label>季节</label>
            <el-select v-model="form.season" placeholder="选择季节" clearable>
              <el-option v-for="s in seasonOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </div>
        </div>

        <div class="form-group">
          <label>备注</label>
          <textarea v-model="form.notes" class="form-textarea" rows="4" placeholder="记录风格和穿搭重点"></textarea>
        </div>

        <div class="summary-block">
          <div class="summary-title">部位完成度</div>
          <div class="summary-item" v-for="row in slotSummary" :key="row.key">
            <span>{{ row.label }}</span>
            <strong :class="{ done: row.done }">{{ row.done ? '已选' : '未选' }}</strong>
          </div>
          <div class="summary-tip">先放置单品，再用 AI 生成整身效果图。</div>
        </div>

        <div class="render-block">
          <div class="summary-title">AI 整身图</div>
          <div v-if="generatingRender" class="render-status">正在调用 Gemini 生成，请稍候...</div>
          <div v-else-if="renderedImageUrl" class="render-preview">
            <img :src="renderedImageUrl" alt="AI生成整身图" />
            <div class="render-meta">
              <span>模型：{{ renderedModel }}</span>
              <a :href="renderedImageUrl" target="_blank" rel="noopener">查看原图</a>
            </div>
            <div v-if="renderedText" class="render-text">{{ renderedText }}</div>
          </div>
          <div v-else class="summary-tip">将当前已选部位发送给 AI，合成完整穿搭图。</div>
        </div>

        <div class="editor-actions">
          <button class="btn-primary" @click="handleSave" :disabled="saving">{{ saving ? '保存中...' : '保存搭配' }}</button>
          <button class="btn-secondary" @click="$router.back()">取消</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createOutfit, getClothingList, getOutfit, renderOutfitImage, updateOutfit } from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const saving = ref(false)
const generatingRender = ref(false)
const wardrobeLoading = ref(false)
const wardrobeKeyword = ref('')
const wardrobeCategory = ref('')
const selectedSlot = ref('top')
const renderedImageUrl = ref('')
const renderedModel = ref('')
const renderedText = ref('')

const allWardrobeItems = ref([])

const form = ref({
  name: '',
  occasion: '',
  season: '',
  notes: '',
})

const createEmptySlots = () => ({
  outer: null,
  top: null,
  bottom: null,
  shoes: null,
  accessory: [],
})

const slots = ref(createEmptySlots())

const SLOT_META = {
  outer: { label: '外套', category: '外套' },
  top: { label: '上衣', category: '上衣' },
  bottom: { label: '下装', category: '下装' },
  shoes: { label: '鞋子', category: '鞋子' },
  accessory: { label: '配饰', category: '配饰' },
}

const POSITION_MAP = {
  outer: { x: 240, y: 70, scale: 1.04 },
  top: { x: 240, y: 185, scale: 1.0 },
  bottom: { x: 240, y: 320, scale: 1.0 },
  shoes: { x: 240, y: 470, scale: 0.9 },
  accessory: [
    { x: 140, y: 215, scale: 0.72 },
    { x: 410, y: 215, scale: 0.72 },
    { x: 275, y: 540, scale: 0.72 },
  ],
}

const categoryOptions = ['上衣', '下装', '外套', '鞋子', '配饰']
const occasionOptions = ['日常', '通勤', '运动', '约会', '正式']
const seasonOptions = ['春', '夏', '秋', '冬', '四季']

let dragClothing = null

const filteredWardrobeItems = computed(() => {
  const category = wardrobeCategory.value
  const kw = wardrobeKeyword.value.trim().toLowerCase()

  return allWardrobeItems.value.filter((item) => {
    if (category && item.category !== category) return false
    if (!kw) return true
    return (item.name || '').toLowerCase().includes(kw)
  })
})

const placedCount = computed(() => {
  return [slots.value.outer, slots.value.top, slots.value.bottom, slots.value.shoes].filter(Boolean).length + slots.value.accessory.length
})

const slotSummary = computed(() => [
  { key: 'outer', label: '外套', done: !!slots.value.outer },
  { key: 'top', label: '上衣', done: !!slots.value.top },
  { key: 'bottom', label: '下装', done: !!slots.value.bottom },
  { key: 'shoes', label: '鞋子', done: !!slots.value.shoes },
  { key: 'accessory', label: '配饰', done: !!slots.value.accessory.length },
])

function onDragStart(event, item) {
  dragClothing = item
  event.dataTransfer.effectAllowed = 'copy'
}

function resetRenderResult() {
  renderedImageUrl.value = ''
  renderedModel.value = ''
  renderedText.value = ''
}

function clearSlots() {
  slots.value = createEmptySlots()
  resetRenderResult()
}

function removeSlot(slotKey) {
  slots.value[slotKey] = null
  resetRenderResult()
}

function removeAccessory(index) {
  slots.value.accessory.splice(index, 1)
  resetRenderResult()
}

function onDropToSlot(slotKey) {
  if (!dragClothing) return

  const expectedCategory = SLOT_META[slotKey].category
  if (dragClothing.category !== expectedCategory) {
    ElMessage.warning(`该区域仅支持 ${expectedCategory}`)
    dragClothing = null
    return
  }

  if (slotKey === 'accessory') {
    const exists = slots.value.accessory.some((x) => x.id === dragClothing.id)
    if (exists) {
      ElMessage.info('该配饰已在当前搭配中')
      dragClothing = null
      return
    }

    if (slots.value.accessory.length >= 3) {
      ElMessage.warning('配饰区最多放 3 件')
      dragClothing = null
      return
    }

    slots.value.accessory.push(dragClothing)
  } else {
    slots.value[slotKey] = dragClothing
  }

  selectedSlot.value = slotKey
  dragClothing = null
  resetRenderResult()
}

function pickOne(items, category, usedIds) {
  const candidates = items.filter((it) => it.category === category && !usedIds.has(it.id))
  if (!candidates.length) return null
  const picked = candidates[Math.floor(Math.random() * candidates.length)]
  usedIds.add(picked.id)
  return picked
}

function autoFillSlots() {
  const source = allWardrobeItems.value
  if (!source.length) {
    ElMessage.warning('衣柜为空，无法填充')
    return
  }

  const usedIds = new Set()
  const next = createEmptySlots()

  next.outer = pickOne(source, '外套', usedIds)
  next.top = pickOne(source, '上衣', usedIds)
  next.bottom = pickOne(source, '下装', usedIds)
  next.shoes = pickOne(source, '鞋子', usedIds)

  const accessories = source.filter((it) => it.category === '配饰' && !usedIds.has(it.id))
  for (const item of accessories.slice(0, 3)) {
    next.accessory.push(item)
  }

  slots.value = next
  resetRenderResult()

  if (!placedCount.value) {
    ElMessage.warning('可用单品不足，未填充有效搭配')
    return
  }

  ElMessage.success('已完成一键填充，可继续微调')
}

function buildRenderItems() {
  const result = []

  const addSingle = (slotKey, clothing) => {
    if (!clothing) return
    result.push({
      name: clothing.name,
      category: SLOT_META[slotKey].category,
      image_url: clothing.image_url || '',
    })
  }

  addSingle('outer', slots.value.outer)
  addSingle('top', slots.value.top)
  addSingle('bottom', slots.value.bottom)
  addSingle('shoes', slots.value.shoes)
  slots.value.accessory.forEach((clothing) => {
    if (!clothing) return
    result.push({
      name: clothing.name,
      category: SLOT_META.accessory.category,
      image_url: clothing.image_url || '',
    })
  })

  return result
}

async function generateOutfitRender() {
  const items = buildRenderItems()
  if (!items.length) {
    ElMessage.warning('请先放置至少一件服装')
    return
  }

  const missingImageItems = items.filter((item) => !item.image_url)
  if (missingImageItems.length) {
    ElMessage.warning(`以下单品没有图片，无法生成：${missingImageItems.map((x) => x.name).join('、')}`)
    return
  }

  generatingRender.value = true
  try {
    const res = await renderOutfitImage({
      items,
      prompt: form.value.notes || undefined,
    })
    renderedImageUrl.value = res.data.image_url || ''
    renderedModel.value = res.data.model || '-'
    renderedText.value = (res.data.text || '').slice(0, 200)
    const saved = await persistOutfit({
      requireName: false,
      autoNameIfMissing: true,
      navigateToList: false,
      successMessage: 'AI 整身图已生成并自动保存',
    })
    if (!saved) return
  } catch (err) {
    const msg = err?.response?.data?.detail || 'AI 整身图生成失败'
    ElMessage.error(msg)
  } finally {
    generatingRender.value = false
  }
}

async function loadWardrobe() {
  wardrobeLoading.value = true
  try {
    const res = await getClothingList({})
    allWardrobeItems.value = res.data || []
  } finally {
    wardrobeLoading.value = false
  }
}

function hydrateSlotsFromOutfit(outfitItems = []) {
  const next = createEmptySlots()

  for (const row of outfitItems) {
    const clothing = row.clothing
    if (!clothing) continue

    if (clothing.category === '配饰') {
      if (next.accessory.length < 3) next.accessory.push(clothing)
      continue
    }

    if (clothing.category === '外套' && !next.outer) next.outer = clothing
    if (clothing.category === '上衣' && !next.top) next.top = clothing
    if (clothing.category === '下装' && !next.bottom) next.bottom = clothing
    if (clothing.category === '鞋子' && !next.shoes) next.shoes = clothing
  }

  slots.value = next
  resetRenderResult()
}

function buildPayloadItems() {
  const result = []

  const addSingle = (slotKey, clothing) => {
    if (!clothing) return
    const pos = POSITION_MAP[slotKey]
    result.push({
      clothing_id: clothing.id,
      position_x: pos.x,
      position_y: pos.y,
      scale: pos.scale,
    })
  }

  addSingle('outer', slots.value.outer)
  addSingle('top', slots.value.top)
  addSingle('bottom', slots.value.bottom)
  addSingle('shoes', slots.value.shoes)

  slots.value.accessory.forEach((clothing, idx) => {
    const pos = POSITION_MAP.accessory[idx] || POSITION_MAP.accessory[POSITION_MAP.accessory.length - 1]
    result.push({
      clothing_id: clothing.id,
      position_x: pos.x,
      position_y: pos.y,
      scale: pos.scale,
    })
  })

  return result
}

function buildAutoOutfitName() {
  const now = new Date()
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  const hh = String(now.getHours()).padStart(2, '0')
  const mi = String(now.getMinutes()).padStart(2, '0')
  return `AI搭配 ${mm}-${dd} ${hh}:${mi}`
}

async function persistOutfit({
  requireName = true,
  autoNameIfMissing = false,
  navigateToList = false,
  successMessage = '保存成功',
} = {}) {
  let finalName = (form.value.name || '').trim()
  if (!finalName && autoNameIfMissing) {
    finalName = buildAutoOutfitName()
    form.value.name = finalName
  }
  if (!finalName && requireName) {
    ElMessage.warning('请输入搭配名称')
    return null
  }

  const items = buildPayloadItems()
  if (!items.length) {
    ElMessage.warning('请至少放置一件服装')
    return null
  }

  saving.value = true
  try {
    const payload = {
      ...form.value,
      name: finalName || form.value.name || buildAutoOutfitName(),
      rendered_image_url: renderedImageUrl.value || null,
      items,
    }

    let saved = null
    if (isEdit.value) {
      const res = await updateOutfit(route.params.id, payload)
      saved = res.data
    } else {
      const res = await createOutfit(payload)
      saved = res.data
      if (!navigateToList && saved?.id) {
        await router.replace(`/outfits/${saved.id}/edit`)
      }
    }

    ElMessage.success(successMessage)
    if (navigateToList) {
      router.push('/outfits')
    }
    return saved
  } catch (err) {
    const msg = err?.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
    return null
  } finally {
    saving.value = false
  }
}

async function handleSave() {
  await persistOutfit({
    requireName: true,
    autoNameIfMissing: false,
    navigateToList: true,
    successMessage: isEdit.value ? '更新成功' : '创建成功',
  })
}

onMounted(async () => {
  await loadWardrobe()

  if (!isEdit.value) return
  const res = await getOutfit(route.params.id)
  const data = res.data
  form.value = {
    name: data.name || '',
    occasion: data.occasion || '',
    season: data.season || '',
    notes: data.notes || '',
  }
  hydrateSlotsFromOutfit(data.items || [])
  renderedImageUrl.value = data.rendered_image_url || ''
  renderedModel.value = data.rendered_image_url ? '已保存' : ''
  renderedText.value = ''
})
</script>

<style scoped>
.outfit-editor-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  /* App.vue page container has 20px top + 28px bottom padding. */
  height: calc(100vh - 48px);
  height: calc(100dvh - 48px);
  overflow: hidden;
  min-height: 0;
}

.page-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 14px;
}

.back-btn {
  display: inline-flex;
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

.header-main h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.header-main p {
  margin-top: 5px;
  color: var(--text-muted);
  font-size: 13px;
}

.header-badges {
  display: flex;
  justify-content: flex-end;
}

.badge {
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #3151cc;
  border: 1px solid rgba(49, 81, 204, 0.24);
  background: rgba(49, 81, 204, 0.1);
}

.editor-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 320px;
  gap: 16px;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.panel {
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
  min-height: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
}

.panel-head h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.panel-head span {
  color: var(--text-muted);
  font-size: 12px;
}

.wardrobe-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.wardrobe-tools {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
}

.search-input {
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 12px;
  font-size: 13px;
  outline: none;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.wardrobe-panel :deep(.el-select__wrapper) {
  min-height: 36px;
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid var(--border-color);
}

.wardrobe-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.wardrobe-item {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 10px;
  align-items: center;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 7px;
  cursor: grab;
  transition: var(--transition);
}

.wardrobe-item:hover {
  border-color: var(--accent);
  background: rgba(79, 110, 247, 0.06);
}

.wardrobe-item:active {
  cursor: grabbing;
}

.wardrobe-thumb {
  width: 44px;
  height: 58px;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f3f8;
}

.wardrobe-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 11px;
}

.wardrobe-name {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wardrobe-meta {
  font-size: 11px;
  color: var(--text-muted);
}

.wardrobe-empty {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  padding: 20px;
}

.stage-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
  min-height: 0;
}

.stage-actions {
  display: flex;
  gap: 8px;
}

.mini-btn {
  height: 30px;
  border: 1px solid var(--border-color);
  background: #fff;
  border-radius: 8px;
  padding: 0 10px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.mini-btn:hover:not(:disabled) {
  color: var(--accent);
  border-color: var(--accent);
}

.mini-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mini-btn-primary {
  border-color: rgba(45, 88, 229, 0.35);
  color: #2f59e3;
  background: rgba(45, 88, 229, 0.08);
}

.mini-btn-primary:hover:not(:disabled) {
  border-color: #2f59e3;
}

.mannequin-board {
  position: relative;
  margin: 10px;
  border-radius: 14px;
  border: 1px dashed rgba(79, 110, 247, 0.35);
  background: linear-gradient(160deg, #ffffff 0%, #f5f8ff 56%, #f0f4ff 100%);
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.silhouette {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 260px;
  height: 500px;
  transform: translate(-50%, -50%);
  border-radius: 140px;
  background: radial-gradient(circle at 50% 24%, rgba(109, 125, 196, 0.22), rgba(109, 125, 196, 0.08) 58%, transparent 72%);
}

.slot-zone {
  position: absolute;
  left: 50%;
  width: 240px;
  transform: translateX(-50%);
  border: 1px dashed rgba(55, 82, 196, 0.35);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.86);
  padding: 8px;
  min-height: 92px;
  transition: var(--transition);
}

.slot-zone.active {
  border-color: rgba(52, 81, 214, 0.9);
  box-shadow: 0 0 0 3px rgba(52, 81, 214, 0.13);
}

.slot-zone.filled {
  border-style: solid;
}

.zone-outer { top: 34px; }
.zone-top { top: 154px; }
.zone-bottom { top: 276px; }
.zone-shoes { top: 418px; }

.slot-title {
  font-size: 12px;
  font-weight: 700;
  color: #405199;
  margin-bottom: 6px;
}

.slot-item {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  gap: 8px;
  align-items: center;
}

.slot-item img {
  width: 44px;
  height: 54px;
  border-radius: 8px;
  object-fit: cover;
  background: #f0f3f7;
}

.slot-item span {
  font-size: 12px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slot-item button,
.accessory-item button {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #fff;
  color: var(--text-secondary);
  font-size: 11px;
  padding: 4px 8px;
  cursor: pointer;
}

.slot-item button:hover,
.accessory-item button:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.slot-empty {
  font-size: 12px;
  color: var(--text-muted);
}

.accessory-zone {
  margin: 0 10px 10px;
  border: 1px dashed rgba(55, 82, 196, 0.35);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.88);
  padding: 10px;
  max-height: 132px;
  overflow-y: auto;
}

.accessory-zone.active {
  border-color: rgba(52, 81, 214, 0.9);
  box-shadow: 0 0 0 3px rgba(52, 81, 214, 0.13);
}

.accessory-zone.filled {
  border-style: solid;
}

.accessory-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
}

.accessory-item {
  display: grid;
  grid-template-columns: 34px 1fr auto;
  gap: 8px;
  align-items: center;
}

.accessory-item img {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  object-fit: cover;
}

.accessory-item span {
  font-size: 12px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inspector-panel {
  padding: 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
}

.inspector-panel .panel-head {
  margin: -12px -12px 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.required {
  color: var(--danger);
}

.form-input,
.form-textarea {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 13px;
  background: #fff;
  width: 100%;
  outline: none;
}

.form-input {
  height: 36px;
  padding: 0 10px;
}

.form-textarea {
  resize: vertical;
  min-height: 84px;
  padding: 10px;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.inspector-panel :deep(.el-select__wrapper) {
  min-height: 36px;
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid var(--border-color);
}

.summary-block {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 10px;
  background: #fbfcff;
}

.summary-title {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
}

.summary-item strong {
  color: #9aa3b6;
}

.summary-item strong.done {
  color: #2a8b4e;
}

.summary-tip {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.5;
}

.render-block {
  margin-top: 12px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 10px;
  background: #fbfcff;
}

.render-status {
  font-size: 12px;
  color: var(--text-secondary);
}

.render-preview img {
  width: 100%;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: #fff;
}

.render-meta {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: var(--text-muted);
}

.render-meta a {
  color: var(--accent);
  text-decoration: none;
}

.render-meta a:hover {
  text-decoration: underline;
}

.render-text {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.editor-actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
  padding-top: 12px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  height: 40px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  border: 0;
  color: #fff;
  background: linear-gradient(135deg, #4f6ef7 0%, #2d58e5 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  border: 1px solid var(--border-color);
  background: #fff;
  color: var(--text-secondary);
}

.btn-secondary:hover {
  color: var(--accent);
  border-color: var(--accent);
}

@media (max-width: 1200px) {
  .editor-layout {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .inspector-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .outfit-editor-page {
    height: auto;
    overflow: visible;
  }

  .page-header {
    grid-template-columns: 1fr;
  }

  .editor-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: auto;
    overflow: visible;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .mannequin-board {
    min-height: 560px;
    height: auto;
  }
}
</style>
