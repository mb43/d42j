// Configuration for Jira and Device42 API access
// Copy this file to 'config.js' and fill in your credentials

const CONFIG = {
  // Jira Configuration
  jira: {
    enabled: true,
    domain: 'your-company.atlassian.net', // Your Jira domain
    email: 'your-email@company.com', // Your Jira email
    apiToken: 'YOUR_JIRA_API_TOKEN', // Generate at: https://id.atlassian.com/manage-profile/security/api-tokens
    // For Jira Cloud, use Basic Auth with base64(email:token)
  },

  // Device42 Configuration
  device42: {
    enabled: true,
    url: 'https://your-device42-instance.com', // Your Device42 URL (no trailing slash)
    username: 'YOUR_D42_USERNAME', // Device42 username
    password: 'YOUR_D42_PASSWORD', // Device42 password
  },

  // Dashboard Settings
  dashboard: {
    refreshInterval: 300000, // Auto-refresh every 5 minutes (300000ms)
    autoRefresh: false, // Set to true to enable auto-refresh
  },

  // Demo Mode (for testing without real credentials)
  demo: {
    enabled: true, // Set to false when using real APIs
  }
};
