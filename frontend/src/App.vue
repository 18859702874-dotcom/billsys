<template>
  <div class="app-layout">
    <aside class="sidebar collapsed">
      <div class="sidebar-header">
        <div class="logo">
<transition name="fade">
            <span v-if="!isCollapsed" class="logo-text">AssetTrack</span>
          </transition>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :title="item.label"
          :class="{ active: isActive(item.path) }"
        >
          <div class="nav-icon" v-html="item.icon"></div>
          <transition name="fade">
            <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>
      </nav>
    </aside>

    <main class="main-content">
      <div class="page-container">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const isCollapsed = true

const navItems = [
  {
    path: '/assets',
    label: '资产管理',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M20 7h-9M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/></svg>',
  },
  {
    path: '/bills',
    label: '记账',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h2M10 15h2"/></svg>',
  },
  {
    path: '/analytics',
    label: '分析报表',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  },
  {
    path: '/clothing',
    label: '我的衣柜',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M6.5 2L2 7l4.5 2V22h11V9L22 7l-4.5-5h-11z"/><path d="M12 2v7"/></svg>',
  },
  {
    path: '/outfits',
    label: '服装搭配',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  },
  {
    path: '/tryon',
    label: 'AI换装',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M12 2a5 5 0 015 5v1H7V7a5 5 0 015-5z"/><path d="M4 10l2 11h12l2-11"/><circle cx="12" cy="15" r="2"/></svg>',
  },
  {
    path: '/settings',
    label: '设置',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.6 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.6a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9c.18.53.7.9 1.26.99H21a2 2 0 010 4h-.34a1.65 1.65 0 00-1.26 1z"/></svg>',
  },
]

function isActive(path) {
  return route.path.startsWith(path)
}
</script>

<style>
:root {
  --sidebar-width: 240px;
  --sidebar-collapsed: 72px;
  --bg-primary: #f8f9fd;
  --bg-card: #ffffff;
  --text-primary: #1a1d2e;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border-color: #e8ecf1;
  --accent: #4f6ef7;
  --accent-light: #eef1fe;
  --accent-gradient: linear-gradient(135deg, #4f6ef7 0%, #7c5cfc 100%);
  --success: #10b981;
  --success-light: #ecfdf5;
  --warning: #f59e0b;
  --warning-light: #fffbeb;
  --danger: #ef4444;
  --danger-light: #fef2f2;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.08);
  --radius: 12px;
  --radius-sm: 8px;
  --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--text-primary);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  transition: width var(--transition);
  overflow: hidden;
}
.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  white-space: nowrap;
}
.logo-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  color: var(--accent);
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-sm);
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  transition: var(--transition);
  cursor: pointer;
  white-space: nowrap;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.85);
}
.nav-item.active {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.35);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-label {
  font-size: 14px;
  font-weight: 500;
}

.main-content {
  margin-left: var(--sidebar-width);
  flex: 1;
  min-height: 100vh;
  transition: margin-left var(--transition);
}
.sidebar.collapsed ~ .main-content {
  margin-left: var(--sidebar-collapsed);
}

.page-container {
  padding: 20px 32px 28px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active {
  transition: opacity 0.3s, transform 0.3s;
}
.page-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.el-table {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: #f8f9fd;
  border-radius: var(--radius) !important;
  overflow: hidden;
}
.el-table th.el-table__cell {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-secondary);
}
.el-card {
  border: 1px solid var(--border-color) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow var(--transition) !important;
}
.el-card:hover {
  box-shadow: var(--shadow-md) !important;
}
.el-card__header {
  border-bottom: 1px solid var(--border-color) !important;
  padding: 16px 20px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
}
.el-card__body {
  padding: 20px !important;
}
.el-button--primary {
  background: var(--accent-gradient) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
}
.el-button--primary:hover {
  filter: brightness(1.08);
}
.el-descriptions {
  --el-descriptions-item-bordered-label-background: #f8f9fd;
}
.el-tag {
  border-radius: 6px !important;
}

/* Keep form control text/icon colors stable on hover/focus. */
.el-select,
.el-input,
.el-date-editor {
  --el-input-text-color: var(--text-primary);
  --el-text-color-regular: var(--text-primary);
  --el-text-color-placeholder: var(--text-muted);
}

.el-select__wrapper,
.el-input__wrapper,
.el-date-editor .el-input__wrapper {
  color: var(--text-primary) !important;
}

.el-select__wrapper:hover,
.el-select__wrapper.is-focused,
.el-input__wrapper:hover,
.el-input__wrapper.is-focus,
.el-date-editor .el-input__wrapper:hover,
.el-date-editor .el-input__wrapper.is-focus {
  color: var(--text-primary) !important;
}

.el-select__selected-item,
.el-input__inner,
.el-range-input,
.el-range-separator,
.el-select__placeholder,
.el-input__placeholder,
.el-select__caret,
.el-input__icon,
.el-icon-circle-close {
  transition: none !important;
}

.el-select__selected-item,
.el-input__inner,
.el-range-input {
  color: var(--text-primary) !important;
}

.el-select__placeholder,
.el-input__placeholder,
.el-range-separator {
  color: var(--text-muted) !important;
}

.el-select__caret,
.el-input__icon,
.el-icon-circle-close {
  color: var(--text-secondary) !important;
}
</style>
