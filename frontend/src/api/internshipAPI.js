import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const fetchInternships = async (filters = {}) => {
  try {
    const params = new URLSearchParams()
    
    if (filters.field) params.append('field', filters.field)
    if (filters.location) params.append('location', filters.location)
    if (filters.active_only !== undefined) params.append('active_only', filters.active_only)

    const response = await api.get(`/api/v1/internships?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error fetching internships:', error)
    throw new Error('Failed to fetch internships')
  }
}

export const fetchInternshipById = async (id) => {
  try {
    const response = await api.get(`/api/v1/internships/${id}`)
    return response.data
  } catch (error) {
    console.error('Error fetching internship:', error)
    throw new Error('Failed to fetch internship')
  }
}

export const fetchStats = async () => {
  try {
    const response = await api.get('/api/v1/internships/stats/summary')
    return response.data
  } catch (error) {
    console.error('Error fetching stats:', error)
    throw new Error('Failed to fetch statistics')
  }
}

export const createInternship = async (internshipData) => {
  try {
    const response = await api.post('/api/v1/internships', internshipData)
    return response.data
  } catch (error) {
    console.error('Error creating internship:', error)
    throw new Error('Failed to create internship')
  }
}

export const updateInternship = async (id, internshipData) => {
  try {
    const response = await api.put(`/api/v1/internships/${id}`, internshipData)
    return response.data
  } catch (error) {
    console.error('Error updating internship:', error)
    throw new Error('Failed to update internship')
  }
}

export const deleteInternship = async (id) => {
  try {
    const response = await api.delete(`/api/v1/internships/${id}`)
    return response.data
  } catch (error) {
    console.error('Error deleting internship:', error)
    throw new Error('Failed to delete internship')
  }
}

export const updateApplicationStatus = async (internshipId, status) => {
  try {
    const response = await api.patch(`/api/v1/internships/${internshipId}/status`, {
      application_status: status
    })
    return response.data
  } catch (error) {
    console.error('Error updating application status:', error)
    throw new Error('Failed to update application status')
  }
}

export default api
