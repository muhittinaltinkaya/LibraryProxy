import axios from 'axios';

// Get API URL from runtime config or environment
const getApiBaseUrl = () => {
  // Check if we're in production and have runtime config
  if (window.APP_CONFIG && window.APP_CONFIG.API_URL) {
    return window.APP_CONFIG.API_URL;
  }
  // Fallback to environment variable or default
  return process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data); // Debug log
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.log('API Error:', error.response?.status, error.response?.data, error.config?.url); // Debug log
    
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  
  register: (data: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => api.post('/auth/register', data),
  
  getProfile: () => api.get('/auth/profile'),
  
  updateProfile: (data: any) => api.put('/auth/profile', data),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
  
  logout: () => api.post('/auth/logout'),
  
  refresh: () => api.post('/auth/refresh'),
};

// Journals API
export const journalsApi = {
  getJournals: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    subject_area?: string;
    access_level?: string;
  }) => api.get('/journals', { params }),
  
  getJournal: (id: number) => api.get(`/journals/${id}`),
  
  requestAccess: (id: number) => api.post(`/journals/${id}/access`),
  
  getProxyUrl: (id: number) => api.get(`/journals/${id}/proxy-url`),
  
  searchJournals: (params: {
    q?: string;
    publisher?: string;
    issn?: string;
    subject_areas?: string[];
    access_level?: string;
  }) => api.get('/journals/search', { params }),
  
  getSubjectAreas: () => api.get('/journals/subject-areas'),
};

// Proxy API
export const proxyApi = {
  generateConfig: (data: { journal_id: number }) =>
    api.post('/proxy/generate', data),
  
  removeConfig: (id: number) => api.delete(`/proxy/${id}`),
  
  getStatus: () => api.get('/proxy/status'),
  
  getStats: () => api.get('/proxy/stats'),
  
  cleanup: () => api.post('/proxy/cleanup'),
  
  reload: () => api.post('/proxy/reload'),
  
  getConfigs: (params?: { page?: number; per_page?: number }) =>
    api.get('/proxy/configs', { params }),
};

// Admin API
export const adminApi = {
  getUsers: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
  }) => api.get('/admin/users', { params }),
  
  createUser: (data: any) => api.post('/admin/users', data),
  
  updateUser: (id: number, data: any) => api.put(`/admin/users/${id}`, data),
  
  getJournals: (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    subject_area?: string;
    access_level?: string;
  }) => api.get('/admin/journals', { params }),
  
  createJournal: (data: any) => api.post('/admin/journals', data),
  
  updateJournal: (id: number, data: any) => api.put(`/admin/journals/${id}`, data),
  
  deleteJournal: (id: number, permanent: boolean = false) => 
    api.delete(`/admin/journals/${id}${permanent ? '?permanent=true' : ''}`),
  
  getStats: () => api.get('/admin/stats'),
  
  getAccessLogs: (params?: {
    page?: number;
    per_page?: number;
    user_id?: number;
    journal_id?: number;
    ip_address?: string;
    start_date?: string;
    end_date?: string;
    status_code?: number;
    method?: string;
    search?: string;
  }) => api.get('/admin/access-logs', { params }),
  
  updateUserPassword: (userId: number, password: string) => 
    api.put(`/admin/users/${userId}/password`, { password }),
};

// Analytics API
export const analyticsApi = {
  getDashboardStats: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/dashboard', { params }),
  
  getResourceReport: (params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }) => api.get('/analytics/resources', { params }),
  
  getUserReport: (params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }) => api.get('/analytics/users', { params }),
  
  getDepartmentReport: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/departments', { params }),
  
  getGeographicReport: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/geographic', { params }),
  
  getFailureAnalysis: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/failures', { params }),
  
  getTurnAwayAnalysis: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/turn-aways', { params }),
  
  getBreakdownReport: (params?: {
    field: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/breakdown', { params }),
  
  getAnalyticsLogs: (params?: {
    page?: number;
    per_page?: number;
    start_date?: string;
    end_date?: string;
    user_id?: number;
    resource_name?: string;
  }) => api.get('/analytics/logs', { params }),
  
  exportData: (params?: {
    type: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/export', { params }),
};

export default api;
