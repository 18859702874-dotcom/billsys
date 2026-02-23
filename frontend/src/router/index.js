import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/assets' },
  { path: '/assets', name: 'AssetList', component: () => import('../views/AssetList.vue') },
  { path: '/assets/new', name: 'AssetNew', component: () => import('../views/AssetForm.vue') },
  { path: '/assets/:id/edit', name: 'AssetEdit', component: () => import('../views/AssetForm.vue') },
  { path: '/assets/:id', name: 'AssetDetail', component: () => import('../views/AssetDetail.vue') },
  { path: '/analytics', name: 'Analytics', component: () => import('../views/Analytics.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
  // Clothing module
  { path: '/clothing', name: 'ClothingList', component: () => import('../views/ClothingList.vue') },
  { path: '/clothing/new', name: 'ClothingNew', component: () => import('../views/ClothingForm.vue') },
  { path: '/clothing/:id/edit', name: 'ClothingEdit', component: () => import('../views/ClothingForm.vue') },
  { path: '/outfits', name: 'OutfitList', component: () => import('../views/OutfitList.vue') },
  { path: '/outfits/new', name: 'OutfitNew', component: () => import('../views/OutfitEditor.vue') },
  { path: '/outfits/:id/edit', name: 'OutfitEdit', component: () => import('../views/OutfitEditor.vue') },
  { path: '/tryon', name: 'TryOn', component: () => import('../views/TryOn.vue') },
  // Bills module
  { path: '/bills', name: 'BillList', component: () => import('../views/BillList.vue') },
  { path: '/bills/new', name: 'BillNew', component: () => import('../views/BillForm.vue') },
  { path: '/bills/:id/edit', name: 'BillEdit', component: () => import('../views/BillForm.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
