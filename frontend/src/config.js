/**
 * Configuration for d42j frontend.
 *
 * IMPORTANT: Update API_BASE_URL to point to your backend API server.
 */

// Default to localhost for development
// For production, set this to your internal API server URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Risk level colors
export const RISK_COLORS = {
  low: '#4caf50',      // Green
  medium: '#ff9800',   // Orange
  high: '#ff5722',     // Deep Orange
  critical: '#f44336'  // Red
};

// Asset type icons/labels
export const ASSET_TYPE_LABELS = {
  physical_server: 'Physical Server',
  virtual_server: 'Virtual Server',
  network_switch: 'Network Switch',
  router: 'Router',
  firewall: 'Firewall',
  access_point: 'Access Point',
  storage_device: 'Storage Device',
  hypervisor: 'Hypervisor'
};

// Refresh interval (milliseconds)
export const AUTO_REFRESH_INTERVAL = 300000; // 5 minutes

export default {
  API_BASE_URL,
  RISK_COLORS,
  ASSET_TYPE_LABELS,
  AUTO_REFRESH_INTERVAL
};
