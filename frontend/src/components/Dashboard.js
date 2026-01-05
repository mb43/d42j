/**
 * Main dashboard with summary statistics and visualizations.
 */
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { apiService } from '../services/api';
import config from '../config';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [criticalAssets, setCriticalAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryRes, criticalRes] = await Promise.all([
        apiService.getSummary(),
        apiService.getCriticalAssets()
      ]);

      setSummary(summaryRes.data);
      setCriticalAssets(criticalRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!summary) {
    return <Alert severity="info">No data available</Alert>;
  }

  // Prepare data for charts
  const riskData = Object.entries(summary.by_risk_level || {}).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: count,
    color: config.RISK_COLORS[level]
  }));

  const typeData = Object.entries(summary.by_type || {}).map(([type, count]) => ({
    name: config.ASSET_TYPE_LABELS[type] || type,
    count: count
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Infrastructure Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Assets
              </Typography>
              <Typography variant="h3">
                {summary.total_assets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Risk
              </Typography>
              <Typography variant="h3" color="error">
                {summary.critical_risk_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Expired Support
              </Typography>
              <Typography variant="h3" color="warning.main">
                {summary.expired_support_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Age (Years)
              </Typography>
              <Typography variant="h3">
                {summary.avg_age_years.toFixed(1)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Risk Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Assets by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#2196f3" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Jira Integration Status
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">
                Matched: <strong>{summary.jira_matched_count}</strong>
              </Typography>
              <Typography variant="body1" color="error">
                Unmatched: <strong>{summary.jira_unmatched_count}</strong>
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {((summary.jira_matched_count / summary.total_assets) * 100).toFixed(1)}%
                of assets matched with Jira
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom color="error">
              Critical Risk Assets ({criticalAssets.length})
            </Typography>
            <Box sx={{ maxHeight: 250, overflow: 'auto' }}>
              {criticalAssets.slice(0, 10).map((asset) => (
                <Box key={asset.id} sx={{ py: 1, borderBottom: '1px solid #eee' }}>
                  <Typography variant="body2">
                    <strong>{asset.hostname}</strong>
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {config.ASSET_TYPE_LABELS[asset.asset_type]} - Age: {asset.age_years?.toFixed(1)}y
                    - Risk Score: {asset.risk_score.toFixed(1)}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Age Distribution Warning */}
      {summary.avg_age_years > 5 && (
        <Alert severity="warning" sx={{ mt: 3 }}>
          ⚠️ Average infrastructure age ({summary.avg_age_years.toFixed(1)} years) exceeds recommended
          threshold. Consider infrastructure modernization planning.
        </Alert>
      )}

      {summary.critical_risk_count > 0 && (
        <Alert severity="error" sx={{ mt: 2 }}>
          🔴 {summary.critical_risk_count} assets at critical risk level. Immediate action required.
        </Alert>
      )}
    </Box>
  );
};

export default Dashboard;
