/**
 * Main application component.
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Container,
  CssBaseline,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Devices as DevicesIcon,
  Warning as WarningIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import Dashboard from './components/Dashboard';
import AssetList from './components/AssetList';
import RiskAssessment from './components/RiskAssessment';
import Discrepancies from './components/Discrepancies';
import { apiService } from './services/api';

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await apiService.getHealth();
      setHealthStatus(response.data);
      setError(null);
    } catch (err) {
      setError('Cannot connect to backend API. Please ensure the API server is running.');
      console.error('Health check failed:', err);
    }
  };

  const handleRefresh = async () => {
    try {
      await apiService.refreshData(true);
      alert('Data refresh initiated. This may take a few minutes.');
    } catch (err) {
      alert('Failed to initiate data refresh');
    }
  };

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'All Assets', icon: <DevicesIcon />, path: '/assets' },
    { text: 'Risk Assessment', icon: <AssessmentIcon />, path: '/risk' },
    { text: 'Discrepancies', icon: <WarningIcon />, path: '/discrepancies' }
  ];

  return (
    <Router>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed">
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={toggleDrawer(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              d42j - Infrastructure Risk Management
            </Typography>
            {healthStatus && (
              <Typography variant="body2" sx={{ mr: 2 }}>
                Status: {healthStatus.status}
              </Typography>
            )}
            <IconButton color="inherit" onClick={handleRefresh}>
              <RefreshIcon />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
          <Box
            sx={{ width: 250 }}
            role="presentation"
            onClick={toggleDrawer(false)}
            onKeyDown={toggleDrawer(false)}
          >
            <List>
              {menuItems.map((item) => (
                <ListItem button key={item.text} component={Link} to={item.path}>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItem>
              ))}
            </List>
            <Divider />
            <List>
              <ListItem button component={Link} to="/settings">
                <ListItemIcon>
                  <SettingsIcon />
                </ListItemIcon>
                <ListItemText primary="Settings" />
              </ListItem>
            </List>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          <Container maxWidth="xl">
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/assets" element={<AssetList />} />
              <Route path="/risk" element={<RiskAssessment />} />
              <Route path="/discrepancies" element={<Discrepancies />} />
            </Routes>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
