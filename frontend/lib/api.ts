import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Helper function to extract error message from API response
function extractErrorMessage(error: any): string {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    if (Array.isArray(detail)) {
      // Pydantic validation errors are arrays
      return detail.map((err: any) => {
        if (typeof err === 'string') return err
        if (err.msg) return `${err.loc?.join('.') || 'field'}: ${err.msg}`
        return JSON.stringify(err)
      }).join(', ')
    } else if (typeof detail === 'string') {
      return detail
    } else {
      return 'An error occurred'
    }
  }
  return error.message || 'An error occurred'
}

// Auth API
export const authApi = {
  signup: async (email: string, password: string) => {
    try {
      const response = await api.post('/api/auth/signup', { email, password })
      return response.data
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error)
      const newError = new Error(errorMessage)
      ;(newError as any).response = error.response
      throw newError
    }
  },
  login: async (email: string, password: string) => {
    try {
      // OAuth2PasswordRequestForm expects form data with username and password
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)
      
      const response = await api.post('/api/auth/login', formData.toString(), {
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      return response.data
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error)
      const newError = new Error(errorMessage)
      ;(newError as any).response = error.response
      throw newError
    }
  },
  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
  getGoogleAuthUrl: async () => {
    const response = await api.get('/api/auth/google/login')
    return response.data
  },
  googleCallback: async (code: string) => {
    const response = await api.post('/api/auth/google/callback', { code })
    return response.data
  },
}

// Feeds API
export const feedsApi = {
  getAll: async () => {
    const response = await api.get('/api/feeds')
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/api/feeds/${id}`)
    return response.data
  },
  create: async (data: { name: string; url: string; feed_type: string; config?: object; category_id?: number }) => {
    const response = await api.post('/api/feeds', data)
    return response.data
  },
  update: async (id: number, data: Partial<{ name: string; url: string; config: object }>) => {
    const response = await api.put(`/api/feeds/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    await api.delete(`/api/feeds/${id}`)
  },
  fetch: async (id: number) => {
    const response = await api.post(`/api/feeds/${id}/fetch`)
    return response.data
  },
  getItems: async (id: number) => {
    const response = await api.get(`/api/feeds/${id}/items`)
    return response.data
  },
}

// Categories API
export const categoriesApi = {
  getAll: async () => {
    const response = await api.get('/api/categories')
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/api/categories/${id}`)
    return response.data
  },
  create: async (data: { name: string; parent_id?: number }) => {
    const response = await api.post('/api/categories', data)
    return response.data
  },
  update: async (id: number, data: Partial<{ name: string; parent_id: number }>) => {
    const response = await api.put(`/api/categories/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    await api.delete(`/api/categories/${id}`)
  },
  assignItem: async (categoryId: number, itemId: number) => {
    const response = await api.post('/api/categories/assign', {
      category_id: categoryId,
      feed_item_id: itemId,
    })
    return response.data
  },
  removeItem: async (assignmentId: number) => {
    await api.delete(`/api/categories/assign/${assignmentId}`)
  },
  getItems: async (id: number) => {
    const response = await api.get(`/api/categories/${id}/items`)
    return response.data
  },
}

// Items API
export const itemsApi = {
  getAll: async (params?: { category_id?: number; feed_id?: number; unread_only?: boolean; since_date?: string }) => {
    const response = await api.get('/api/items', { params })
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/api/items/${id}`)
    return response.data
  },
  markRead: async (id: number) => {
    const response = await api.post(`/api/items/${id}/mark-read`)
    return response.data
  },
  markUnread: async (id: number) => {
    const response = await api.post(`/api/items/${id}/mark-unread`)
    return response.data
  },
  getCategories: async (id: number) => {
    const response = await api.get(`/api/items/${id}/categories`)
    return response.data
  },
}

