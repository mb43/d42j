# IT Executive Dashboard - Jira & Device42

A beautiful, real-time executive dashboard for IT Service Management metrics from Jira Service Management and Device42. Zero backend required - runs entirely in the browser.

![Dashboard Preview](https://img.shields.io/badge/status-ready-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 📊 **Real-time Metrics**: MTTR, SLA compliance, critical issues, asset counts
- 📈 **Beautiful Charts**: Issue trends, priority distribution, asset health, resolution times
- 🔄 **Auto-refresh**: Configurable automatic data refresh
- 🎨 **Modern UI**: Glass-morphism design with smooth animations
- 🚀 **No Backend**: Pure client-side JavaScript - deploy anywhere
- 🔐 **Secure**: API credentials stay in your browser, never transmitted to third parties

## 🚀 Quick Start

### Option 1: Run Locally (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd d42j

# Configure your API credentials
cp config.example.js config.js
# Edit config.js with your Jira and Device42 credentials

# Start a local server
python3 -m http.server 8000
# Or use: npm run serve

# Open in browser
open http://localhost:8000
```

### Option 2: Deploy to GitHub Pages (5 minutes)

1. **Fork/Clone this repository**

2. **Configure credentials**:
   ```bash
   cp config.example.js config.js
   # Edit config.js with your API details
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial dashboard setup"
   git push origin main
   ```

4. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

5. **Access your dashboard**:
   - `https://yourusername.github.io/d42j`

## 🔧 Configuration

### Jira Setup

1. **Generate API Token**:
   - Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Copy the token

2. **Update config.js**:
   ```javascript
   jira: {
     enabled: true,
     domain: 'your-company.atlassian.net',
     email: 'your-email@company.com',
     apiToken: 'YOUR_JIRA_API_TOKEN',
   }
   ```

### Device42 Setup

1. **Get credentials** from your Device42 admin

2. **Update config.js**:
   ```javascript
   device42: {
     enabled: true,
     url: 'https://your-device42-instance.com',
     username: 'YOUR_D42_USERNAME',
     password: 'YOUR_D42_PASSWORD',
   }
   ```

### Dashboard Settings

```javascript
dashboard: {
  refreshInterval: 300000,  // 5 minutes in milliseconds
  autoRefresh: true,        // Enable auto-refresh
}
```

## 📊 Metrics Explained

| Metric | Source | Description |
|--------|--------|-------------|
| **MTTR** | Jira | Mean Time to Resolve - average time to close issues (30-day window) |
| **SLA Compliance** | Jira | Percentage of issues resolved within SLA targets |
| **Critical Issues** | Jira | Currently open issues with Critical priority |
| **Total Assets** | Device42 | Total number of assets in Device42 inventory |

## 🎨 Customization

### Modify JQL Queries

Edit `app.js` → `loadJiraData()` function:

```javascript
const jql = 'priority=Critical AND status!=Closed';  // Customize this
```

### Add Custom Metrics

1. Fetch data in `loadJiraData()` or `loadDevice42Data()`
2. Add HTML card in `index.html`
3. Update display in `updateDashboard()`

### Change Theme Colors

Edit the gradient in `index.html`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 🔒 Security Notes

⚠️ **IMPORTANT**: This dashboard runs client-side, meaning API credentials are visible in your browser's JavaScript.

**Best Practices**:

1. ✅ Use **read-only** API tokens/accounts
2. ✅ Create dedicated service accounts with minimal permissions
3. ✅ Don't commit `config.js` to public repositories (it's in `.gitignore`)
4. ✅ For production, consider:
   - Hosting behind a VPN
   - Using a reverse proxy to hide credentials
   - Building a simple backend API to proxy requests

**For truly sensitive environments**, consider deploying with a backend proxy that handles authentication.

## 🛠️ Development

### File Structure

```
d42j/
├── index.html          # Main dashboard UI
├── app.js              # Dashboard logic & API integration
├── config.js           # Your API credentials (gitignored)
├── config.example.js   # Configuration template
├── package.json        # Project metadata
├── .gitignore          # Prevents committing secrets
├── .nojekyll           # GitHub Pages compatibility
└── README.md           # This file
```

### Testing with Demo Data

The dashboard includes demo mode for testing without real APIs:

```javascript
// In config.js
demo: {
  enabled: true  // Shows realistic fake data
}
```

### Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

## 📝 Jira API Reference

Common JQL queries for customization:

```jql
# All open critical issues
priority=Critical AND status!=Closed

# Issues breaching SLA
status!=Closed AND cf[10000] < now()

# Recent issues (last 7 days)
created >= -7d

# Unassigned high priority
priority=High AND assignee is EMPTY
```

[Full Jira REST API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

## 🐛 Troubleshooting

### CORS Errors

**Problem**: Browser blocks API requests due to CORS policy.

**Solutions**:
1. Use a browser extension like "CORS Unblock" (dev only)
2. Set up a reverse proxy (production)
3. Enable CORS in Jira/Device42 admin settings (if available)

### Authentication Failures

**Problem**: 401 Unauthorized errors.

**Solutions**:
- Verify credentials in `config.js`
- Check API token hasn't expired
- Ensure account has necessary permissions
- For Jira: verify email and token are correct

### No Data Showing

**Problem**: Dashboard loads but shows no data.

**Solutions**:
1. Open browser console (F12) to check for errors
2. Verify `CONFIG.demo.enabled = false` in config.js
3. Check network tab for failed API calls
4. Verify JQL queries return results in Jira

## 🚀 Deployment Options

| Platform | Difficulty | Cost | Notes |
|----------|------------|------|-------|
| **GitHub Pages** | Easy | Free | Best for public dashboards |
| **Netlify** | Easy | Free | Drag-and-drop deployment |
| **Vercel** | Easy | Free | Auto-deploys from Git |
| **AWS S3** | Medium | ~$0.50/mo | Requires AWS setup |
| **Internal Server** | Medium | Varies | Best for sensitive data |

## 📄 License

MIT License - feel free to customize and deploy as needed.

## 🤝 Contributing

Issues and pull requests welcome! Common additions:

- Additional chart types
- More Jira metrics (velocity, burndown, etc.)
- Device42 asset breakdown by type
- Export to PDF functionality
- Dark mode toggle

## 💡 Pro Tips

1. **Create a TV Display**: Set `autoRefresh: true` and display on office monitors
2. **Mobile-Friendly**: Dashboard is responsive - check metrics on the go
3. **Custom Alerts**: Add browser notifications for critical issues
4. **Historical Data**: Extend to store data locally for trends over time

---

**Need Help?** Open an issue or check the [Jira API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) and [Device42 API Docs](https://api.device42.com/).

Built with ❤️ for IT teams who want clarity, not clutter.
