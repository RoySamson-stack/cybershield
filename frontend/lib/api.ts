import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cache configuration
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Cache helper functions
const getCacheKey = (url: string, params?: any) => {
  return `${url}${params ? JSON.stringify(params) : ''}`;
};

const getCached = (key: string) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

const setCached = (key: string, data: any) => {
  cache.set(key, { data, timestamp: Date.now() });
};

api.interceptors.request.use((config) => {
  // Only add auth token if it exists (for testing, auth is disabled on backend)
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // If no token, request proceeds without auth header (works when DISABLE_AUTH_FOR_TESTING is enabled)
  
  // Check cache for GET requests
  if (config.method === 'get' && !config.params?.noCache) {
    const cacheKey = getCacheKey(config.url || '', config.params);
    const cached = getCached(cacheKey);
    if (cached) {
      return Promise.reject({
        __cached: true,
        data: cached,
      });
    }
  }
  
  return config;
});

api.interceptors.response.use(
  (response) => {
    // Cache GET responses
    if (response.config.method === 'get' && !response.config.params?.noCache) {
      const cacheKey = getCacheKey(response.config.url || '', response.config.params);
      setCached(cacheKey, response.data);
    }
    return response;
  },
  async (error) => {
    // Handle cached responses
    if (error.__cached) {
      return Promise.resolve({ data: error.data, __cached: true });
    }
    
    const originalRequest = error.config || {};
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry) {
      if (typeof window === 'undefined') {
        return Promise.reject(error);
      }

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        // No refresh token means we're in demo mode or not logged in;
        // just reject without forcing a logout redirect.
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      
      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/auth/refresh/`,
          { refresh: refreshToken }
        );
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
