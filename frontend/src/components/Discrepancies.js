/**
 * Discrepancies between Device42 and Jira asset registers.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
  Button
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import { apiService } from '../services/api';

const Discrepancies = () => {
  const [discrepancies, setDiscrepancies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTab, setCurrentTab] = useState(0);

  useEffect(() => {
    loadDiscrepancies();
  }, []);

  const loadDiscrepancies = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDiscrepancies();
      setDiscrepancies(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load discrepancies');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const exportToCSV = () => {
    if (!discrepancies) return;

    let csvContent = '';

    // In Device42 but not Jira
    csvContent += 'Assets in Device42 but not in Jira\n';
    discrepancies.in_device42_not_jira.forEach(hostname => {
      csvContent += `${hostname}\n`;
    });

    csvContent += '\nAssets in Jira but not in Device42\n';
    discrepancies.in_jira_not_device42.forEach(hostname => {
      csvContent += `${hostname}\n`;
    });

    csvContent += '\nAssets with Mismatched Data\n';
    discrepancies.mismatched_data.forEach(item => {
      csvContent += `${item}\n`;
    });

    // Create download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `discrepancies_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
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

  if (!discrepancies) {
    return <Alert severity="info">No discrepancy data available</Alert>;
  }

  const totalDiscrepancies =
    discrepancies.in_device42_not_jira.length +
    discrepancies.in_jira_not_device42.length +
    discrepancies.mismatched_data.length;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Asset Register Discrepancies
        </Typography>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={exportToCSV}
        >
          Export CSV
        </Button>
      </Box>

      {totalDiscrepancies === 0 ? (
        <Alert severity="success">
          ✅ No discrepancies found! Device42 and Jira asset registers are in sync.
        </Alert>
      ) : (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Found {totalDiscrepancies} discrepancies between Device42 and Jira asset registers.
          These should be investigated and resolved to maintain data integrity.
        </Alert>
      )}

      <Paper>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab
            label={`In Device42 Only (${discrepancies.in_device42_not_jira.length})`}
          />
          <Tab
            label={`In Jira Only (${discrepancies.in_jira_not_device42.length})`}
          />
          <Tab
            label={`Mismatched Data (${discrepancies.mismatched_data.length})`}
          />
        </Tabs>
        <Divider />

        {/* Tab 0: In Device42 but not Jira */}
        {currentTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="body1" gutterBottom>
              These assets exist in Device42 but are not found in the Jira asset register.
              They may need to be added to Jira or could indicate decommissioned assets.
            </Typography>
            {discrepancies.in_device42_not_jira.length > 0 ? (
              <List>
                {discrepancies.in_device42_not_jira.map((hostname, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={hostname}
                      secondary="Not found in Jira"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                No assets in this category
              </Typography>
            )}
          </Box>
        )}

        {/* Tab 1: In Jira but not Device42 */}
        {currentTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="body1" gutterBottom>
              These assets exist in Jira but are not found in Device42.
              They may have been removed from production or could indicate missing Device42 entries.
            </Typography>
            {discrepancies.in_jira_not_device42.length > 0 ? (
              <List>
                {discrepancies.in_jira_not_device42.map((hostname, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={hostname}
                      secondary="Not found in Device42"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                No assets in this category
              </Typography>
            )}
          </Box>
        )}

        {/* Tab 2: Mismatched Data */}
        {currentTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="body1" gutterBottom>
              These assets exist in both systems but have conflicting data.
              The differences should be investigated and corrected.
            </Typography>
            {discrepancies.mismatched_data.length > 0 ? (
              <List>
                {discrepancies.mismatched_data.map((mismatch, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={mismatch} />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                No mismatched data found
              </Typography>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Discrepancies;
