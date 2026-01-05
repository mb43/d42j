/**
 * Asset list with filtering and sorting.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { apiService } from '../services/api';
import config from '../config';

const AssetList = () => {
  const [assets, setAssets] = useState([]);
  const [filteredAssets, setFilteredAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  useEffect(() => {
    loadAssets();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [assets, searchTerm, typeFilter, riskFilter]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAssets();
      setAssets(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load assets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...assets];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (asset) =>
          asset.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
          asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (asset.ip_address && asset.ip_address.includes(searchTerm))
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter((asset) => asset.asset_type === typeFilter);
    }

    // Risk filter
    if (riskFilter !== 'all') {
      filtered = filtered.filter((asset) => asset.risk_level === riskFilter);
    }

    setFilteredAssets(filtered);
    setPage(0);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getRiskChip = (riskLevel) => {
    const color = config.RISK_COLORS[riskLevel] || '#999';
    return (
      <Chip
        label={riskLevel.toUpperCase()}
        size="small"
        sx={{
          bgcolor: color,
          color: 'white',
          fontWeight: 'bold'
        }}
      />
    );
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

  const paginatedAssets = filteredAssets.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Infrastructure Assets
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search (hostname, name, IP)"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Asset Type</InputLabel>
              <Select
                value={typeFilter}
                label="Asset Type"
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                {Object.entries(config.ASSET_TYPE_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={riskFilter}
                label="Risk Level"
                onChange={(e) => setRiskFilter(e.target.value)}
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        <Typography variant="body2" sx={{ mt: 2 }}>
          Showing {filteredAssets.length} of {assets.length} assets
        </Typography>
      </Paper>

      {/* Asset Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Hostname</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Manufacturer</TableCell>
              <TableCell>Model</TableCell>
              <TableCell>Age (Years)</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Jira Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedAssets.map((asset) => (
              <TableRow key={asset.id} hover>
                <TableCell>
                  <strong>{asset.hostname}</strong>
                  <br />
                  <Typography variant="caption" color="textSecondary">
                    {asset.ip_address}
                  </Typography>
                </TableCell>
                <TableCell>{config.ASSET_TYPE_LABELS[asset.asset_type]}</TableCell>
                <TableCell>{asset.manufacturer || 'N/A'}</TableCell>
                <TableCell>{asset.model || 'N/A'}</TableCell>
                <TableCell>
                  {asset.age_years ? asset.age_years.toFixed(1) : 'N/A'}
                </TableCell>
                <TableCell>{getRiskChip(asset.risk_level)}</TableCell>
                <TableCell>{asset.risk_score.toFixed(1)}</TableCell>
                <TableCell>
                  {asset.jira_matched ? (
                    <Chip label="Matched" color="success" size="small" />
                  ) : (
                    <Chip label="Unmatched" color="error" size="small" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredAssets.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      </TableContainer>
    </Box>
  );
};

export default AssetList;
