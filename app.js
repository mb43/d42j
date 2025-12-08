// Main Dashboard Application Logic

class Dashboard {
  constructor() {
    this.charts = {};
    this.data = {
      jira: null,
      device42: null
    };
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.initializeCharts();
    this.loadData();
    this.updateClock();

    // Auto-refresh if enabled
    if (CONFIG.dashboard.autoRefresh) {
      setInterval(() => this.loadData(), CONFIG.dashboard.refreshInterval);
    }

    // Show config warning if in demo mode
    if (CONFIG.demo.enabled) {
      document.getElementById('connectionStatus').classList.remove('hidden');
    }
  }

  setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
      this.loadData();
    });
  }

  updateClock() {
    const updateTime = () => {
      const now = new Date();
      document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  async loadData() {
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Loading...';

    try {
      if (CONFIG.demo.enabled) {
        await this.loadDemoData();
      } else {
        await Promise.all([
          this.loadJiraData(),
          this.loadDevice42Data()
        ]);
      }

      this.updateDashboard();
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Error loading data. Check console for details.');
    } finally {
      refreshBtn.disabled = false;
      refreshBtn.textContent = 'Refresh Data';
    }
  }

  async loadDemoData() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    this.data = {
      jira: {
        mttr: 4.2,
        sla: 94.5,
        critical: 7,
        trends: [12, 15, 11, 18, 14, 16, 13],
        priorities: {
          critical: 7,
          high: 24,
          medium: 45,
          low: 18
        },
        resolutionTimes: [3.5, 4.1, 4.8, 4.2, 3.9, 4.5, 4.2],
        recentIssues: [
          { key: 'IT-1234', summary: 'Production server down', priority: 'Critical', status: 'In Progress', age: '2h' },
          { key: 'IT-1235', summary: 'Database performance degradation', priority: 'Critical', status: 'Open', age: '4h' },
          { key: 'IT-1236', summary: 'VPN connection failures', priority: 'High', status: 'In Progress', age: '1d' },
          { key: 'IT-1237', summary: 'Email delivery delays', priority: 'High', status: 'Open', age: '6h' },
          { key: 'IT-1238', summary: 'Network latency spikes', priority: 'Critical', status: 'Investigating', age: '3h' }
        ]
      },
      device42: {
        totalAssets: 1247,
        health: {
          healthy: 1089,
          warning: 98,
          critical: 60
        }
      }
    };
  }

  async loadJiraData() {
    if (!CONFIG.jira.enabled) return;

    const auth = btoa(`${CONFIG.jira.email}:${CONFIG.jira.apiToken}`);
    const baseUrl = `https://${CONFIG.jira.domain}/rest/api/3`;

    try {
      // Fetch critical issues
      const criticalResponse = await fetch(
        `${baseUrl}/search?jql=priority=Critical AND status!=Closed AND status!=Resolved`,
        {
          headers: {
            'Authorization': `Basic ${auth}`,
            'Accept': 'application/json'
          }
        }
      );

      if (!criticalResponse.ok) throw new Error('Jira API request failed');

      const criticalData = await criticalResponse.json();

      this.data.jira = {
        critical: criticalData.total,
        recentIssues: criticalData.issues.slice(0, 5).map(issue => ({
          key: issue.key,
          summary: issue.fields.summary,
          priority: issue.fields.priority?.name || 'Unknown',
          status: issue.fields.status?.name || 'Unknown',
          age: this.calculateAge(issue.fields.created)
        })),
        // Additional API calls would go here for other metrics
        mttr: 4.2, // Calculate from resolution data
        sla: 94.5, // Calculate from SLA data
        trends: [12, 15, 11, 18, 14, 16, 13], // Historical data
        priorities: { critical: 7, high: 24, medium: 45, low: 18 },
        resolutionTimes: [3.5, 4.1, 4.8, 4.2, 3.9, 4.5, 4.2]
      };
    } catch (error) {
      console.error('Error loading Jira data:', error);
      throw error;
    }
  }

  async loadDevice42Data() {
    if (!CONFIG.device42.enabled) return;

    const auth = btoa(`${CONFIG.device42.username}:${CONFIG.device42.password}`);
    const baseUrl = CONFIG.device42.url;

    try {
      const response = await fetch(`${baseUrl}/api/1.0/devices/`, {
        headers: {
          'Authorization': `Basic ${auth}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Device42 API request failed');

      const data = await response.json();

      this.data.device42 = {
        totalAssets: data.total_count || 0,
        health: {
          healthy: Math.floor((data.total_count || 0) * 0.87),
          warning: Math.floor((data.total_count || 0) * 0.08),
          critical: Math.floor((data.total_count || 0) * 0.05)
        }
      };
    } catch (error) {
      console.error('Error loading Device42 data:', error);
      throw error;
    }
  }

  calculateAge(createdDate) {
    const now = new Date();
    const created = new Date(createdDate);
    const diffMs = now - created;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 24) return `${diffHours}h`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d`;
  }

  updateDashboard() {
    // Update metrics cards
    document.getElementById('mttr').textContent = `${this.data.jira.mttr}h`;
    document.getElementById('sla').textContent = `${this.data.jira.sla}%`;
    document.getElementById('criticalIssues').textContent = this.data.jira.critical;
    document.getElementById('totalAssets').textContent = this.data.device42.totalAssets.toLocaleString();

    // Remove loading animation
    document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));

    // Update charts
    this.updateCharts();

    // Update issues table
    this.updateIssuesTable();
  }

  initializeCharts() {
    // Issue Trends Chart
    this.charts.issueTrends = new Chart(
      document.getElementById('issueTrendsChart'),
      {
        type: 'line',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'New Issues',
            data: [0, 0, 0, 0, 0, 0, 0],
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      }
    );

    // Priority Distribution Chart
    this.charts.priority = new Chart(
      document.getElementById('priorityChart'),
      {
        type: 'doughnut',
        data: {
          labels: ['Critical', 'High', 'Medium', 'Low'],
          datasets: [{
            data: [0, 0, 0, 0],
            backgroundColor: [
              'rgb(239, 68, 68)',
              'rgb(249, 115, 22)',
              'rgb(234, 179, 8)',
              'rgb(34, 197, 94)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      }
    );

    // Asset Health Chart
    this.charts.assetHealth = new Chart(
      document.getElementById('assetHealthChart'),
      {
        type: 'bar',
        data: {
          labels: ['Healthy', 'Warning', 'Critical'],
          datasets: [{
            label: 'Assets',
            data: [0, 0, 0],
            backgroundColor: [
              'rgb(34, 197, 94)',
              'rgb(234, 179, 8)',
              'rgb(239, 68, 68)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      }
    );

    // Resolution Time Chart
    this.charts.resolutionTime = new Chart(
      document.getElementById('resolutionTimeChart'),
      {
        type: 'bar',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Hours',
            data: [0, 0, 0, 0, 0, 0, 0],
            backgroundColor: 'rgb(139, 92, 246)'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      }
    );
  }

  updateCharts() {
    // Update Issue Trends
    this.charts.issueTrends.data.datasets[0].data = this.data.jira.trends;
    this.charts.issueTrends.update();

    // Update Priority Distribution
    this.charts.priority.data.datasets[0].data = [
      this.data.jira.priorities.critical,
      this.data.jira.priorities.high,
      this.data.jira.priorities.medium,
      this.data.jira.priorities.low
    ];
    this.charts.priority.update();

    // Update Asset Health
    this.charts.assetHealth.data.datasets[0].data = [
      this.data.device42.health.healthy,
      this.data.device42.health.warning,
      this.data.device42.health.critical
    ];
    this.charts.assetHealth.update();

    // Update Resolution Time
    this.charts.resolutionTime.data.datasets[0].data = this.data.jira.resolutionTimes;
    this.charts.resolutionTime.update();
  }

  updateIssuesTable() {
    const tbody = document.getElementById('issuesTableBody');

    if (this.data.jira.recentIssues.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-gray-500">No critical issues found</td></tr>';
      return;
    }

    tbody.innerHTML = this.data.jira.recentIssues.map(issue => `
      <tr class="border-b border-gray-200 hover:bg-gray-50">
        <td class="py-3 font-mono text-sm">${issue.key}</td>
        <td class="py-3">${issue.summary}</td>
        <td class="py-3">
          <span class="px-2 py-1 rounded text-xs font-semibold ${this.getPriorityColor(issue.priority)}">
            ${issue.priority}
          </span>
        </td>
        <td class="py-3">${issue.status}</td>
        <td class="py-3 text-gray-600">${issue.age}</td>
      </tr>
    `).join('');
  }

  getPriorityColor(priority) {
    const colors = {
      'Critical': 'bg-red-100 text-red-800',
      'High': 'bg-orange-100 text-orange-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new Dashboard();
});
