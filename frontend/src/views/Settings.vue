<template>
  <div class="settings-page">
    <!-- 分类管理模块 -->
    <div class="module-card">
      <div class="module-header">
        <div class="header-main">
          <span class="module-tag">Category</span>
          <h3 class="module-title">分类管理</h3>
          <p class="module-desc">维护两级分类体系，资产与记账共用。一级为大类，二级为细分。</p>

          <div class="kpi-row">
            <div class="kpi-chip">
              <div class="kpi-icon-box" style="--kpi-color: #4f6ef7; --kpi-bg: rgba(79,110,247,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path d="M1 2.5A1.5 1.5 0 012.5 1h3A1.5 1.5 0 017 2.5v3A1.5 1.5 0 015.5 7h-3A1.5 1.5 0 011 5.5v-3zm8 0A1.5 1.5 0 0110.5 1h3A1.5 1.5 0 0115 2.5v3A1.5 1.5 0 0113.5 7h-3A1.5 1.5 0 019 5.5v-3zm-8 8A1.5 1.5 0 012.5 9h3A1.5 1.5 0 017 10.5v3A1.5 1.5 0 015.5 15h-3A1.5 1.5 0 011 13.5v-3zm8 0A1.5 1.5 0 0110.5 9h3a1.5 1.5 0 011.5 1.5v3a1.5 1.5 0 01-1.5 1.5h-3A1.5 1.5 0 019 13.5v-3z"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ l1Categories.length }}</strong>
                <span class="kpi-label">一级分类</span>
              </div>
            </div>

            <div class="kpi-chip">
              <div class="kpi-icon-box" style="--kpi-color: #7c5cfc; --kpi-bg: rgba(124,92,252,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M4 1h8a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1zm1 3v1h6V4H5zm0 3v1h6V7H5zm0 3v1h4v-1H5z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ l2TotalCount }}</strong>
                <span class="kpi-label">二级分类</span>
              </div>
            </div>

            <div
              class="kpi-chip kpi-chip-clickable"
              :class="{ active: budgetOnly }"
              role="button"
              tabindex="0"
              @click="toggleBudgetOnly"
              @keydown.enter.prevent="toggleBudgetOnly"
              @keydown.space.prevent="toggleBudgetOnly"
            >
              <div class="kpi-icon-box" style="--kpi-color: #10b981; --kpi-bg: rgba(16,185,129,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M8 1a7 7 0 100 14A7 7 0 008 1zm-.5 4.5a.5.5 0 011 0v.612c.61.152 1.25.586 1.25 1.388 0 .77-.574 1.23-1.25 1.4v1.6c.39-.102.625-.324.625-.625a.5.5 0 011 0c0 .905-.737 1.48-1.625 1.609V11.5a.5.5 0 01-1 0v-.516C6.637 10.83 6 10.264 6 9.5c0-.77.574-1.23 1.25-1.4V6.5c-.39.102-.625.324-.625.625a.5.5 0 01-1 0c0-.905.737-1.48 1.625-1.609V5.5z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ budgetConfiguredCount }}</strong>
                <span class="kpi-label">{{ budgetOnly ? '仅已设预算' : '已设置预算' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button class="btn-secondary" @click="handleAddCategory(null)">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
              <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/>
            </svg>
            新建一级分类
          </button>
          <button class="btn-primary" @click="handleAddCategory(selectedL1Id)">
            <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
              <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/>
            </svg>
            新建子分类
          </button>
        </div>
      </div>

      <div class="cat-layout" v-loading="loading">
        <!-- 左侧：一级分类列表 -->
        <div class="l1-panel">
          <div class="panel-title panel-title-l1">
            <span>一级分类</span>
            <span v-if="!budgetOnly && visibleL1Categories.length > 1" class="panel-drag-hint">可上下拖拽排序</span>
          </div>
          <div
            v-for="cat in visibleL1Categories"
            :key="cat.id"
            class="l1-item"
            :class="{
              active: selectedL1Id === cat.id,
              dragging: draggingL1Id === cat.id,
              'drag-over-before': dragOverL1Id === cat.id && dragOverPosition === 'before',
              'drag-over-after': dragOverL1Id === cat.id && dragOverPosition === 'after',
            }"
            :draggable="!budgetOnly && !savingL1Order && visibleL1Categories.length > 1"
            @dragstart="onL1DragStart($event, cat.id)"
            @dragover.prevent="onL1DragOver($event, cat.id)"
            @drop.prevent="onL1Drop($event, cat.id)"
            @dragend="onL1DragEnd"
            @click="selectedL1Id = cat.id"
          >
            <span class="cat-dot" :style="{ background: getCategoryColor(cat.name) }"></span>
            <span class="l1-name">{{ cat.name }}</span>
            <span v-if="isCategoryWithAssetRecord(cat.id)" class="asset-flag">资产</span>
            <span class="l1-count" v-if="getVisibleChildren(cat.id).length">{{ getVisibleChildren(cat.id).length }}</span>
            <div class="l1-actions">
              <button class="icon-btn" title="移动为子分类" @click.stop="handleMoveCategory(cat)">
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                  <path d="M7 2v10M7 12l-3-3M7 12l3-3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="icon-btn" title="重命名" @click.stop="handleRenameCategory(cat)">
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                  <path d="M9.5 1.5L12.5 4.5L5 12H2V9L9.5 1.5Z" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="icon-btn danger" title="删除" @click.stop="handleDeleteCategory(cat)">
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                  <path d="M2 3.5h10M5 3.5V2h4v1.5M3 3.5l.75 8h6.5L11 3.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <div v-if="!visibleL1Categories.length" class="l1-empty">{{ budgetOnly ? '暂无已设置预算的分类' : '暂无一级分类' }}</div>
        </div>

        <!-- 右侧：子分类 + 日预算 -->
        <div class="l2-panel">
          <div v-if="!selectedL1" class="l2-empty">请先在左侧选择一级分类</div>
          <div v-else>
            <table class="data-table" v-if="currentChildren.length">
              <thead>
                <tr>
                  <th class="name-col">子分类名称</th>
                  <th class="budget-col">日预算（元/天）</th>
                  <th class="actions-col">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="child in currentChildren" :key="child.id">
                  <td class="name-col">
                    <div class="cat-name-row">
                      <span class="cat-dot" :style="{ background: getCategoryColor(child.name) }"></span>
                      <span class="cat-name">{{ child.name }}</span>
                      <span v-if="isCategoryWithAssetRecord(child.id)" class="asset-flag">资产</span>
                    </div>
                  </td>
                  <td class="budget-col">
                    <span v-if="hasBudget(child)" class="budget-badge">
                      ¥{{ formatBudget(child.daily_budget) }}<span class="budget-unit">/天</span>
                    </span>
                    <span v-else class="no-budget">未设置</span>
                  </td>
                  <td class="actions-col">
                    <div class="action-btns">
                      <button class="action-btn" @click="handleMoveCategory(child)">移动</button>
                      <button class="action-btn" @click="handleRenameCategory(child)">重命名</button>
                      <button class="action-btn budget" @click="handleSetBudget(child)">预算</button>
                      <button class="action-btn danger" @click="handleDeleteCategory(child)">删除</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-else class="l2-empty">
              <p>{{ budgetOnly ? '当前分类下暂无已设置预算的子分类' : '该分类暂无子分类' }}</p>
              <button v-if="!budgetOnly" class="btn-link" @click="handleAddCategory(selectedL1Id)">+ 添加子分类</button>
            </div>

            <!-- 一级分类本身的日预算设置 -->
            <div class="l1-budget-row">
              <span class="l1-budget-label">「{{ selectedL1.name }}」自身日预算：</span>
              <span v-if="hasBudget(selectedL1)" class="budget-badge">
                ¥{{ formatBudget(selectedL1.daily_budget) }}/天
              </span>
              <span v-else class="no-budget">未设置</span>
              <button class="action-btn budget" style="margin-left:12px" @click="handleSetBudget(selectedL1)">设置</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createCategory, deleteCategory, getAssets, getCategories, updateCategory } from '../api'

const categories = ref([])
const assetCategoryIdSet = ref(new Set())
const loading = ref(false)
const selectedL1Id = ref(null)
const budgetOnly = ref(false)
const draggingL1Id = ref(null)
const dragOverL1Id = ref(null)
const dragOverPosition = ref('before')
const savingL1Order = ref(false)

const l1Categories = computed(() => categories.value.filter((c) => !c.parent_id))
const l2TotalCount = computed(() => categories.value.filter((c) => c.parent_id).length)
const budgetConfiguredCount = computed(() => categories.value.filter((cat) => hasBudget(cat)).length)
const visibleL1Categories = computed(() => {
  if (!budgetOnly.value) return l1Categories.value
  return l1Categories.value.filter((cat) => hasBudget(cat) || getChildren(cat.id).some((child) => hasBudget(child)))
})

const selectedL1 = computed(() => visibleL1Categories.value.find((c) => c.id === selectedL1Id.value) || null)
const currentChildren = computed(() => getVisibleChildren(selectedL1Id.value))

function getChildren(parentId) {
  if (!parentId) return []
  return categories.value.filter((c) => c.parent_id === parentId)
}

function getVisibleChildren(parentId) {
  const children = getChildren(parentId)
  return budgetOnly.value ? children.filter((child) => hasBudget(child)) : children
}

function isCategoryWithAssetRecord(categoryId) {
  if (!categoryId) return false
  if (assetCategoryIdSet.value.has(categoryId)) return true
  const children = getChildren(categoryId)
  return children.some((child) => assetCategoryIdSet.value.has(child.id))
}

const categoryNames = computed(() => new Set(categories.value.map((x) => x.name.trim())))

const CATEGORY_COLORS = ['#4f6ef7', '#7c5cfc', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899']

function getCategoryColor(name) {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return CATEGORY_COLORS[Math.abs(hash) % CATEGORY_COLORS.length]
}

function hasBudget(category) {
  return category.daily_budget !== null && category.daily_budget !== undefined && category.daily_budget !== ''
}

function formatBudget(value) {
  return Number(value).toFixed(2)
}

function toggleBudgetOnly() {
  budgetOnly.value = !budgetOnly.value
}

async function loadData() {
  loading.value = true
  try {
    const [catRes, assetRes] = await Promise.all([getCategories(), getAssets()])
    categories.value = catRes.data
    assetCategoryIdSet.value = new Set(assetRes.data.map((row) => row.category_id).filter(Boolean))
    // 默认选中第一个一级分类
    if (!selectedL1Id.value && l1Categories.value.length) {
      selectedL1Id.value = l1Categories.value[0].id
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('设置数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function handleAddCategory(parentId) {
  const title = parentId ? '新建子分类' : '新建一级分类'
  const placeholder = parentId ? '例如：三餐' : '例如：餐饮'
  try {
    const { value } = await ElMessageBox.prompt('请输入分类名称', title, {
      inputPlaceholder: placeholder,
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (raw) => {
        const v = (raw || '').trim()
        if (!v) return '分类名称不能为空'
        if (v.length > 50) return '分类名称不能超过 50 个字符'
        if (categoryNames.value.has(v)) return '分类已存在'
        return true
      },
    })

    await createCategory({ name: value.trim(), parent_id: parentId || null })
    ElMessage.success('分类已创建')
    await loadData()
    if (parentId) selectedL1Id.value = parentId
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '创建分类失败')
  }
}

async function handleRenameCategory(category) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的分类名称', '重命名分类', {
      inputValue: category.name,
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValidator: (raw) => {
        const v = (raw || '').trim()
        if (!v) return '分类名称不能为空'
        if (v.length > 50) return '分类名称不能超过 50 个字符'
        if (v !== category.name && categoryNames.value.has(v)) return '分类已存在'
        return true
      },
    })

    const name = value.trim()
    if (name === category.name) return

    await updateCategory(category.id, { name })
    ElMessage.success('分类已更新')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '更新分类失败')
  }
}

async function handleSetBudget(category) {
  const currentBudget = category.daily_budget ? Number(category.daily_budget).toFixed(2) : ''
  try {
    const { value } = await ElMessageBox.prompt(
      `为「${category.name}」设置每日预算，留空表示不限制预算。`,
      '设置日预算',
      {
        inputValue: currentBudget,
        inputPlaceholder: '例如：10.00',
        inputType: 'number',
        confirmButtonText: '保存',
        cancelButtonText: '取消',
        inputValidator: (raw) => {
          if (raw === '' || raw === null || raw === undefined) return true
          const v = Number(raw)
          if (isNaN(v) || v < 0) return '请输入有效的非负数字'
          return true
        },
      }
    )

    const raw = (value || '').trim()
    const daily_budget = raw === '' ? null : Number(raw)
    await updateCategory(category.id, { daily_budget })
    ElMessage.success('预算已更新')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '更新预算失败')
  }
}

async function handleMoveCategory(category) {
  // Build options: all L1 categories except itself (and its children)
  const childIds = new Set(getChildren(category.id).map((c) => c.id))
  const options = [
    { label: '— 设为一级分类 —', value: null },
    ...l1Categories.value
      .filter((c) => c.id !== category.id && !childIds.has(c.id))
      .map((c) => ({ label: c.name, value: String(c.id) })),
  ]

  const currentParent = category.parent_id
    ? l1Categories.value.find((c) => c.id === category.parent_id)
    : null
  const currentLabel = currentParent ? currentParent.name : '一级分类（无父分类）'

  try {
    const { value } = await ElMessageBox.prompt(
      `当前所属：${currentLabel}\n请输入目标一级分类名称，或留空设为一级分类。\n\n可选：${options.map((o) => o.label).join('、')}`,
      `移动「${category.name}」`,
      {
        inputPlaceholder: '目标一级分类名称，留空 = 设为一级分类',
        confirmButtonText: '移动',
        cancelButtonText: '取消',
        inputValidator: (raw) => {
          const v = (raw || '').trim()
          if (!v) return true // empty = set as L1
          const target = l1Categories.value.find((c) => c.name === v)
          if (!target) return '未找到该一级分类'
          if (target.id === category.id) return '不能移动到自身'
          if (childIds.has(target.id)) return '不能移动到自己的子分类下'
          return true
        },
      }
    )

    const targetName = (value || '').trim()
    let newParentId = null
    if (targetName) {
      const target = l1Categories.value.find((c) => c.name === targetName)
      if (target) newParentId = target.id
    }

    if (newParentId === category.parent_id) {
      ElMessage.info('未变更')
      return
    }

    await updateCategory(category.id, { parent_id: newParentId })
    ElMessage.success('分类已移动')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '移动失败')
  }
}

async function handleDeleteCategory(category) {
  try {
    await ElMessageBox.confirm(`确认删除分类「${category.name}」？`, '删除分类', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    await deleteCategory(category.id)
    ElMessage.success('分类已删除')
    if (selectedL1Id.value === category.id) selectedL1Id.value = null
    await loadData()
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '删除分类失败')
  }
}

function clearL1DragState() {
  draggingL1Id.value = null
  dragOverL1Id.value = null
  dragOverPosition.value = 'before'
}

function onL1DragStart(event, categoryId) {
  if (savingL1Order.value || l1Categories.value.length <= 1) {
    event.preventDefault()
    return
  }
  draggingL1Id.value = categoryId
  dragOverL1Id.value = categoryId
  dragOverPosition.value = 'before'
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.dropEffect = 'move'
    event.dataTransfer.setData('text/plain', String(categoryId))
  }
}

function onL1DragOver(event, targetId) {
  if (!draggingL1Id.value || draggingL1Id.value === targetId) return
  const row = event.currentTarget
  if (!row) return
  const rect = row.getBoundingClientRect()
  dragOverPosition.value = event.clientY > rect.top + rect.height / 2 ? 'after' : 'before'
  dragOverL1Id.value = targetId
}

async function onL1Drop(event, targetId) {
  if (!draggingL1Id.value || savingL1Order.value) return
  const draggedId = draggingL1Id.value
  const orderIds = l1Categories.value.map((cat) => cat.id)
  const fromIndex = orderIds.indexOf(draggedId)
  const toIndex = orderIds.indexOf(targetId)
  if (fromIndex === -1 || toIndex === -1) {
    clearL1DragState()
    return
  }

  let insertIndex = toIndex + (dragOverPosition.value === 'after' ? 1 : 0)
  if (fromIndex < insertIndex) insertIndex -= 1
  if (fromIndex === insertIndex) {
    clearL1DragState()
    return
  }

  orderIds.splice(fromIndex, 1)
  orderIds.splice(insertIndex, 0, draggedId)
  await persistL1Order(orderIds)
  clearL1DragState()
}

function onL1DragEnd() {
  clearL1DragState()
}

async function persistL1Order(orderIds) {
  const l1Map = new Map(l1Categories.value.map((cat) => [cat.id, cat]))
  const nextSortOrder = new Map()
  const updates = []

  orderIds.forEach((id, index) => {
    nextSortOrder.set(id, index)
    const cat = l1Map.get(id)
    if (cat && cat.sort_order !== index) {
      updates.push(updateCategory(id, { sort_order: index }))
    }
  })

  if (!updates.length) return

  const previous = categories.value.map((cat) => ({ ...cat }))
  categories.value = categories.value
    .map((cat) => (nextSortOrder.has(cat.id) ? { ...cat, sort_order: nextSortOrder.get(cat.id) } : cat))
    .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)

  savingL1Order.value = true
  try {
    await Promise.all(updates)
    await loadData()
    ElMessage.success('一级分类顺序已更新')
  } catch (error) {
    categories.value = previous
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '更新排序失败')
  } finally {
    savingL1Order.value = false
  }
}

watch(
  visibleL1Categories,
  (list) => {
    if (!list.length) {
      selectedL1Id.value = null
      return
    }
    if (!selectedL1Id.value || !list.some((cat) => cat.id === selectedL1Id.value)) {
      selectedL1Id.value = list[0].id
    }
  },
  { immediate: true }
)

onMounted(loadData)
</script>

<style scoped>
.settings-page {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

.module-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.module-header {
  padding: 22px 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, rgba(79, 110, 247, 0.04) 0%, transparent 55%);
}

.header-main { min-width: 0; flex: 1; }

.module-tag {
  display: inline-block;
  border: 1px solid rgba(79, 110, 247, 0.28);
  color: #3551cf;
  background: rgba(79, 110, 247, 0.07);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.9px;
  text-transform: uppercase;
  padding: 2px 8px;
  margin-bottom: 8px;
}

.module-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-primary);
}

.module-desc {
  margin-top: 5px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.55;
}

.kpi-row {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.kpi-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 12px;
  padding: 8px 14px 8px 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.kpi-chip-clickable {
  cursor: pointer;
  user-select: none;
  transition: border-color var(--transition), background var(--transition), box-shadow var(--transition);
}

.kpi-chip-clickable:hover {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.06);
}

.kpi-chip-clickable.active {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.1);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.18);
}

.kpi-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--kpi-bg);
  color: var(--kpi-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-body { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.kpi-num { font-size: 18px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; line-height: 1; }
.kpi-label { font-size: 11px; color: var(--text-muted); line-height: 1; }

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.btn-primary, .btn-secondary {
  border: none;
  border-radius: var(--radius-sm);
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: filter var(--transition), transform var(--transition);
}

.btn-primary {
  background: var(--accent-gradient);
  color: #fff;
  box-shadow: 0 3px 10px rgba(79, 110, 247, 0.28);
}
.btn-primary:hover { filter: brightness(1.07); transform: translateY(-1px); }

.btn-secondary {
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}
.btn-secondary:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }

/* Two-panel layout */
.cat-layout {
  display: flex;
  min-height: 320px;
}

.l1-panel {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--border-color);
  padding: 12px 0;
  background: #fafbfd;
}

.l2-panel {
  flex: 1;
  padding: 16px 20px;
  min-width: 0;
}

.panel-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 0 16px 10px;
}

.panel-title-l1 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.panel-drag-hint {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: none;
  letter-spacing: 0;
}

.l1-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px 9px 16px;
  cursor: pointer;
  transition: background var(--transition);
  border-radius: 0;
  position: relative;
  user-select: none;
}

.l1-item[draggable='true'] {
  cursor: grab;
}

.l1-item.dragging {
  opacity: 0.56;
}

.l1-item.drag-over-before::before,
.l1-item.drag-over-after::after {
  content: '';
  position: absolute;
  left: 16px;
  right: 12px;
  height: 2px;
  background: var(--accent);
  border-radius: 999px;
}

.l1-item.drag-over-before::before {
  top: 0;
}

.l1-item.drag-over-after::after {
  bottom: 0;
}

.l1-item:hover { background: rgba(79, 110, 247, 0.05); }
.l1-item.active {
  background: var(--accent-light);
  border-right: 3px solid var(--accent);
}
.l1-item.active .l1-name { color: var(--accent); font-weight: 700; }

.l1-name {
  flex: 1;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.l1-count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(79, 110, 247, 0.1);
  color: var(--accent);
  font-weight: 600;
  flex-shrink: 0;
}

.l1-actions {
  display: none;
  gap: 3px;
  flex-shrink: 0;
}
.l1-item:hover .l1-actions { display: flex; }

.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 3px;
  border-radius: 5px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  transition: color var(--transition), background var(--transition);
}
.icon-btn:hover { color: var(--accent); background: var(--accent-light); }
.icon-btn.danger:hover { color: var(--danger); background: var(--danger-light); }
.l1-empty, .l2-empty {
  padding: 24px 16px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

.btn-link {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 0;
  margin-top: 6px;
  font-weight: 500;
}
.btn-link:hover { text-decoration: underline; }

/* Sub-category table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.data-table th {
  padding: 9px 12px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  background: #f8f9fd;
  text-transform: uppercase;
}

.data-table td {
  padding: 10px 12px;
  font-size: 13.5px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}

.data-table tbody tr:hover { background: #f5f8ff; }

.name-col   { width: auto; }
.budget-col { width: 160px; }
.actions-col { width: 200px; text-align: center; }
.data-table th.actions-col, .data-table td.actions-col { text-align: center; }

.cat-name-row { display: flex; align-items: center; gap: 9px; }
.cat-dot { width: 8px; height: 8px; border-radius: 999px; flex-shrink: 0; }
.cat-name { font-size: 13.5px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.asset-flag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 18px;
  padding: 0 6px;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.32);
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2px;
  flex-shrink: 0;
}

.budget-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  padding: 3px 9px;
  background: rgba(16, 185, 129, 0.08);
  color: #059669;
  border-radius: 999px;
  border: 1px solid rgba(16, 185, 129, 0.22);
  font-size: 12.5px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.budget-unit { font-size: 11px; font-weight: 500; opacity: 0.65; }
.no-budget { font-size: 13px; color: var(--text-muted); }

.action-btns { display: flex; align-items: center; justify-content: center; gap: 4px; }

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 7px;
  height: 26px;
  padding: 0 9px;
  font-size: 11.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}
.action-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
.action-btn.budget:hover { border-color: #059669; color: #059669; background: rgba(16, 185, 129, 0.07); }
.action-btn.danger:hover { border-color: var(--danger); color: var(--danger); background: var(--danger-light); }
/* L1 budget row */
.l1-budget-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0;
  padding-top: 14px;
  border-top: 1px solid var(--border-color);
  font-size: 13px;
  flex-wrap: wrap;
}
.l1-budget-label { color: var(--text-secondary); }
</style>
