// Configuration for Jira and Device42 API access
// This is the demo configuration - copy config.example.js and customize for production

const CONFIG = {
  // Jira Configuration
  jira: {
    enabled: false,
    domain: 'your-company.atlassian.net',
    email: 'your-email@company.com',
    apiToken: 'YOUR_JIRA_API_TOKEN',
  },

  // Device42 Configuration
  device42: {
    enabled: false,
    url: 'https://your-device42-instance.com',
    username: 'YOUR_D42_USERNAME',
    password: 'YOUR_D42_PASSWORD',
  },

  // Dashboard Settings
  dashboard: {
    refreshInterval: 300000,
    autoRefresh: false,
  },

  // Demo Mode (uses mock data)
  demo: {
    enabled: true, // Set to false when using real APIs
  }
};
