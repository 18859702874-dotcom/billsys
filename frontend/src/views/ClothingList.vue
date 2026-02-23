<template>
  <div class="clothing-page">
    <div class="toolbar">
      <div class="toolbar-filters">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input v-model="filters.search" placeholder="搜索服装名称..." @keyup.enter="load" />
        </div>
        <el-select v-model="filters.category" placeholder="全部分类" clearable @change="load" class="filter-select">
          <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filters.season" placeholder="全部季节" clearable @change="load" class="filter-select">
          <el-option v-for="s in seasonOptions" :key="s" :label="s" :value="s" />
        </el-select>
      </div>
      <button class="btn-primary" @click="$router.push('/clothing/new')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        添加服装
      </button>
    </div>

    <div class="clothing-grid">
      <div
        v-for="item in items"
        :key="item.id"
        class="clothing-card"
        @click="$router.push(`/clothing/${item.id}/edit`)"
      >
        <div class="card-image">
          <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
          <div v-else class="no-image">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
              <path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/>
              <path d="M12 2v7"/>
            </svg>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-name">{{ item.name }}</h3>
          <div class="card-tags">
            <span class="tag category-tag" :style="catStyle(item.category)">{{ item.category }}</span>
            <span v-if="item.season" class="tag season-tag">{{ item.season }}</span>
            <span v-if="item.color" class="tag color-tag">{{ item.color }}</span>
          </div>
          <div class="card-footer">
            <span v-if="item.brand" class="brand">{{ item.brand }}</span>
            <span v-if="item.purchase_price" class="price">¥{{ Number(item.purchase_price).toFixed(2) }}</span>
          </div>
        </div>
        <div class="card-actions" @click.stop>
          <el-popconfirm title="确定要删除这件服装吗？" @confirm="handleDelete(item.id)" width="220">
            <template #reference>
              <button class="action-btn danger" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                </svg>
              </button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <div v-if="!items.length" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/>
        <path d="M12 2v7"/>
      </svg>
      <p>衣柜空空如也，快去添加服装吧</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getClothingList, deleteClothing } from '../api'

const items = ref([])
const filters = ref({ category: null, season: null, search: '' })

const categoryOptions = ['上衣', '下装', '外套', '鞋子', '配饰']
const seasonOptions = ['春', '夏', '秋', '冬', '四季']

const catColors = { '上衣': '#4f6ef7', '下装': '#10b981', '外套': '#8b5cf6', '鞋子': '#f59e0b', '配饰': '#ec4899' }

function catStyle(cat) {
  const color = catColors[cat] || '#4f6ef7'
  return { background: color + '18', color }
}

async function load() {
  const params = {}
  if (filters.value.category) params.category = filters.value.category
  if (filters.value.season) params.season = filters.value.season
  if (filters.value.search) params.search = filters.value.search
  const res = await getClothingList(params)
  items.value = res.data
}

async function handleDelete(id) {
  await deleteClothing(id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.toolbar-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(180deg, #ffffff 0%, #fdfdff 100%);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
  height: 40px;
  width: 240px;
  transition: border-color var(--transition), box-shadow var(--transition);
  color: var(--text-secondary);
}
.search-box:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}
.search-box input {
  border: none;
  outline: none;
  background: none;
  font-size: 13px;
  color: var(--text-primary);
  width: 100%;
}
.search-box input::placeholder { color: var(--text-muted); }
.filter-select { width: 130px; }

.clothing-page :deep(.filter-select .el-select__wrapper) {
  min-height: 40px;
  border-radius: 10px;
  box-shadow: none;
  background: linear-gradient(180deg, #ffffff 0%, #fdfdff 100%);
  border: 1px solid var(--border-color);
  font-size: 13px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0 20px;
  height: 38px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition), transform var(--transition);
}
.btn-primary:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

.clothing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.clothing-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition), transform var(--transition);
  position: relative;
}
.clothing-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-image {
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f3f4f6;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.card-body {
  padding: 14px;
}
.card-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
}
.season-tag {
  background: #fef3c7;
  color: #92400e;
}
.color-tag {
  background: #e0e7ff;
  color: #3730a3;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.brand {
  color: var(--text-secondary);
}
.price {
  font-weight: 600;
  color: var(--accent);
}

.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity var(--transition);
}
.clothing-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}
.action-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: var(--danger-light);
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--text-muted);
}
.empty-state svg {
  margin-bottom: 16px;
  opacity: 0.5;
}
.empty-state p {
  font-size: 14px;
}

@media (max-width: 900px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  .search-box { width: 100%; }
  .clothing-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
}
</style>
