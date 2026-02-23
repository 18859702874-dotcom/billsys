<template>
  <div class="settings-page">
    <div class="module-card">
      <div class="module-header">
        <div>
          <h3 class="module-title">分类管理</h3>
          <p class="module-desc">维护资产分类，供资产录入和筛选使用。</p>
        </div>
        <button class="btn-primary" @click="handleAddCategory">新建分类</button>
      </div>

      <div class="table-wrap" v-loading="loading">
        <table class="data-table" v-if="categories.length">
          <thead>
            <tr>
              <th>分类名称</th>
              <th style="width: 130px; text-align: center">资产数量</th>
              <th style="width: 180px; text-align: center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categories" :key="cat.id">
              <td>{{ cat.name }}</td>
              <td style="text-align: center; font-variant-numeric: tabular-nums">{{ usageCount(cat.id) }}</td>
              <td>
                <div class="action-btns">
                  <button class="action-btn" @click="handleRenameCategory(cat)">重命名</button>
                  <button class="action-btn danger" @click="handleDeleteCategory(cat)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">
          <p>暂无分类，点击右上角“新建分类”开始创建。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createCategory, deleteCategory, getAssets, getCategories, updateCategory } from '../api'

const categories = ref([])
const assetsByCategory = ref({})
const loading = ref(false)

const categoryNames = computed(() => new Set(categories.value.map((x) => x.name.trim())))

function usageCount(categoryId) {
  return assetsByCategory.value[categoryId] || 0
}

async function loadData() {
  loading.value = true
  try {
    const [categoryRes, assetsRes] = await Promise.all([getCategories(), getAssets()])
    categories.value = categoryRes.data
    const usage = {}
    for (const item of assetsRes.data) {
      usage[item.category_id] = (usage[item.category_id] || 0) + 1
    }
    assetsByCategory.value = usage
  } catch (error) {
    console.error(error)
    ElMessage.error('设置数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function handleAddCategory() {
  try {
    const { value } = await ElMessageBox.prompt('请输入分类名称', '新建分类', {
      inputPlaceholder: '例如：平板电脑',
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

    await createCategory({ name: value.trim() })
    ElMessage.success('分类已创建')
    await loadData()
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

async function handleDeleteCategory(category) {
  const used = usageCount(category.id)
  if (used > 0) {
    ElMessage.warning(`该分类下还有 ${used} 条资产，无法删除`)
    return
  }

  try {
    await ElMessageBox.confirm(`确认删除分类“${category.name}”？`, '删除分类', {
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
    await loadData()
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '删除分类失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.settings-page {
  max-width: 1080px;
}

.module-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
}

.module-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--border-color);
  background: #fafbfd;
}

.module-title {
  font-size: 18px;
  font-weight: 700;
}

.module-desc {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 13px;
}

.table-wrap {
  padding: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  background: #f8f9fd;
}

.data-table td {
  padding: 14px 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  border-radius: 8px;
  height: 30px;
  padding: 0 10px;
  font-size: 12px;
  cursor: pointer;
  transition: var(--transition);
}

.action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.action-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: var(--danger-light);
}

.btn-primary {
  border: none;
  background: var(--accent-gradient);
  color: #fff;
  border-radius: var(--radius-sm);
  height: 38px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: filter var(--transition), transform var(--transition);
}

.btn-primary:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

.empty-state {
  padding: 48px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

@media (max-width: 860px) {
  .module-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
