import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// --- Categories ---
export const getCategories = () => api.get('/categories')
export const getCategoriesTree = () => api.get('/categories/tree')
export const createCategory = (data) => api.post('/categories', data)
export const updateCategory = (id, data) => api.put(`/categories/${id}`, data)
export const deleteCategory = (id) => api.delete(`/categories/${id}`)

// --- Transactions ---
export const getTransactions = (params) => api.get('/transactions', { params })
export const createTransaction = (data) => api.post('/transactions', data)
export const updateTransaction = (id, data) => api.put(`/transactions/${id}`, data)
export const deleteTransaction = (id) => api.delete(`/transactions/${id}`)
export const getTransactionSummary = (params) => api.get('/transactions/summary', { params })

// --- Assets ---
export const getAssets = (params) => api.get('/assets', { params })
export const getAsset = (id) => api.get(`/assets/${id}`)
export const createAsset = (data) => api.post('/assets', data)
export const updateAsset = (id, data) => api.put(`/assets/${id}`, data)
export const deleteAsset = (id) => api.delete(`/assets/${id}`)
export const disposeAsset = (id, data) => api.post(`/assets/${id}/dispose`, data)
export const restoreAsset = (id) => api.post(`/assets/${id}/restore`)

// --- Analytics ---
export const getDailyCostTrend = (params) => api.get('/analytics/daily-cost-trend', { params })
export const getCategoryDistribution = () => api.get('/analytics/category-distribution')
export const getCostSummary = () => api.get('/analytics/cost-summary')

// --- Clothing ---
export const getClothingList = (params) => api.get('/clothing', { params })
export const getClothing = (id) => api.get(`/clothing/${id}`)
export const createClothing = (formData) => api.post('/clothing', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const createClothingBatch = (data) => api.post('/clothing/batch', data)
export const updateClothing = (id, formData) => api.put(`/clothing/${id}`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteClothing = (id) => api.delete(`/clothing/${id}`)
export const recognizeClothing = (formData) => api.post('/clothing/recognize', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// --- Outfits ---
export const getOutfits = (params) => api.get('/outfits', { params })
export const getOutfit = (id) => api.get(`/outfits/${id}`)
export const createOutfit = (data) => api.post('/outfits', data)
export const updateOutfit = (id, data) => api.put(`/outfits/${id}`, data)
export const deleteOutfit = (id) => api.delete(`/outfits/${id}`)
export const renderOutfitImage = (data) => api.post('/outfits/render-image', data)

// --- TryOn ---
export const submitTryOn = (formData) => api.post('/tryon', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const getTryOnResult = (taskId) => api.get(`/tryon/${taskId}`)
