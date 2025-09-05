import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
  
  updateUser: (id: number, data: any) => api.put(`/admin/users/${id}`, data),
  
  createJournal: (data: any) => api.post('/admin/journals', data),
  
  updateJournal: (id: number, data: any) => api.put(`/admin/journals/${id}`, data),
  
  deleteJournal: (id: number) => api.delete(`/admin/journals/${id}`),
  
  getStats: () => api.get('/admin/stats'),
  
  getAccessLogs: (params?: {
    page?: number;
    per_page?: number;
    user_id?: number;
    journal_id?: number;
  }) => api.get('/admin/access-logs', { params }),
};

export default api;
