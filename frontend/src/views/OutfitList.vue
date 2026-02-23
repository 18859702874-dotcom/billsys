<template>
  <div class="outfit-list-page">
    <div class="toolbar">
      <div class="toolbar-filters">
        <el-select v-model="filters.occasion" placeholder="全部场合" clearable @change="load" class="filter-select">
          <el-option v-for="o in occasionOptions" :key="o" :label="o" :value="o" />
        </el-select>
        <el-select v-model="filters.season" placeholder="全部季节" clearable @change="load" class="filter-select">
          <el-option v-for="s in seasonOptions" :key="s" :label="s" :value="s" />
        </el-select>
      </div>
      <button class="btn-primary" @click="$router.push('/outfits/new')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        新建搭配
      </button>
    </div>

    <div class="outfit-grid">
      <div
        v-for="outfit in outfits"
        :key="outfit.id"
        class="outfit-card"
        @click="$router.push(`/outfits/${outfit.id}/edit`)"
      >
        <div class="outfit-preview">
          <div class="preview-items">
            <div
              v-for="(item, idx) in outfit.items.slice(0, 4)"
              :key="idx"
              class="preview-thumb"
            >
              <img v-if="item.clothing?.image_url" :src="item.clothing.image_url" :alt="item.clothing?.name" />
              <div v-else class="thumb-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
                  <path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/>
                  <path d="M12 2v7"/>
                </svg>
              </div>
            </div>
          </div>
          <div v-if="outfit.items.length > 4" class="more-badge">+{{ outfit.items.length - 4 }}</div>
        </div>
        <div class="outfit-body">
          <h3 class="outfit-name">{{ outfit.name }}</h3>
          <div class="outfit-meta">
            <span v-if="outfit.occasion" class="tag occasion-tag">{{ outfit.occasion }}</span>
            <span v-if="outfit.season" class="tag season-tag">{{ outfit.season }}</span>
            <span class="item-count">{{ outfit.items.length }} 件</span>
          </div>
        </div>
        <div class="card-actions" @click.stop>
          <el-popconfirm title="确定要删除这个搭配吗？" @confirm="handleDelete(outfit.id)" width="220">
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

    <div v-if="!outfits.length" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <rect x="3" y="3" width="7" height="7" rx="1"/>
        <rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
      <p>还没有搭配方案，去创建一个吧</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOutfits, deleteOutfit } from '../api'

const outfits = ref([])
const filters = ref({ occasion: null, season: null })

const occasionOptions = ['日常', '通勤', '运动', '约会', '正式']
const seasonOptions = ['春', '夏', '秋', '冬', '四季']

async function load() {
  const params = {}
  if (filters.value.occasion) params.occasion = filters.value.occasion
  if (filters.value.season) params.season = filters.value.season
  const res = await getOutfits(params)
  outfits.value = res.data
}

async function handleDelete(id) {
  await deleteOutfit(id)
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
}
.filter-select { width: 130px; }

.outfit-list-page :deep(.filter-select .el-select__wrapper) {
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
.btn-primary:hover { filter: brightness(1.08); transform: translateY(-1px); }

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.outfit-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition), transform var(--transition);
  position: relative;
}
.outfit-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.outfit-preview {
  padding: 16px;
  background: #f8f9fd;
  position: relative;
}
.preview-items {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.preview-thumb {
  aspect-ratio: 3/4;
  border-radius: 8px;
  overflow: hidden;
  background: #e5e7eb;
}
.preview-thumb img {
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
}
.more-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.outfit-body {
  padding: 14px 16px;
}
.outfit-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}
.outfit-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
}
.occasion-tag {
  background: #dbeafe;
  color: #1e40af;
}
.season-tag {
  background: #fef3c7;
  color: #92400e;
}
.item-count {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity var(--transition);
}
.outfit-card:hover .card-actions { opacity: 1; }

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
.empty-state svg { margin-bottom: 16px; opacity: 0.5; }
.empty-state p { font-size: 14px; }
</style>
