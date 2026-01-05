/**
 * API service for communicating with d42j backend.
 */
import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * API methods
 */
export const apiService = {
  // Health check
  getHealth: () => api.get('/health'),

  // Assets
  getAssets: (params = {}) => api.get('/api/assets', { params }),
  getAsset: (assetId) => api.get(`/api/assets/${assetId}`),
  getCriticalAssets: () => api.get('/api/critical-assets'),
  getAgingAssets: (thresholdYears = 5) =>
    api.get('/api/aging-assets', { params: { threshold_years: thresholdYears } }),
  getUnsupportedAssets: () => api.get('/api/unsupported-assets'),

  // Risk assessments
  getAssessments: (riskLevel = null) =>
    api.get('/api/assessments', { params: riskLevel ? { risk_level: riskLevel } : {} }),

  // Summary
  getSummary: () => api.get('/api/summary'),

  // Discrepancies
  getDiscrepancies: () => api.get('/api/discrepancies'),

  // Data refresh
  refreshData: (force = false) => api.post('/api/refresh', { force })
};

export default api;
