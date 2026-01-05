/**
 * Risk assessment details and recommendations.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { apiService } from '../services/api';
import config from '../config';

const RiskAssessment = () => {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAssessments();
      // Sort by risk score descending
      const sorted = response.data.sort((a, b) => b.risk_score - a.risk_score);
      setAssessments(sorted);
      setError(null);
    } catch (err) {
      setError('Failed to load risk assessments');
      console.error(err);
    } finally {
      setLoading(false);
    }
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

  const getRiskIcon = (riskLevel) => {
    if (riskLevel === 'critical' || riskLevel === 'high') {
      return <WarningIcon color="error" />;
    }
    return null;
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

  const criticalCount = assessments.filter(a => a.risk_level === 'critical').length;
  const highCount = assessments.filter(a => a.risk_level === 'high').length;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Risk Assessment
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Risk assessment based on industry-standard hardware failure rates (bathtub curve model),
        age analysis, support status, and incident history.
      </Alert>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Risk
              </Typography>
              <Typography variant="h3" color="error">
                {criticalCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Risk
              </Typography>
              <Typography variant="h3" color="warning.main">
                {highCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assessment Details */}
      <Typography variant="h6" gutterBottom>
        Detailed Assessments ({assessments.length} assets)
      </Typography>

      {assessments.map((assessment) => (
        <Accordion key={assessment.asset_id}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              {getRiskIcon(assessment.risk_level)}
              <Typography sx={{ flexGrow: 1 }}>
                <strong>{assessment.hostname}</strong>
              </Typography>
              {getRiskChip(assessment.risk_level)}
              <Typography variant="body2" sx={{ mr: 2 }}>
                Score: {assessment.risk_score.toFixed(1)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Risk Factors */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Risk Factors
                </Typography>
                <List dense>
                  {Object.entries(assessment.factors).map(([factor, score]) => (
                    <ListItem key={factor}>
                      <ListItemText
                        primary={factor.replace(/_/g, ' ').toUpperCase()}
                        secondary={`Score: ${score.toFixed(1)}/100`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>

              {/* Recommendations */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Recommendations
                </Typography>
                {assessment.recommendations.length > 0 ? (
                  <List dense>
                    {assessment.recommendations.map((rec, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={rec} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    No specific recommendations
                  </Typography>
                )}
              </Grid>
            </Grid>

            <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
              Assessed: {new Date(assessment.assessed_at).toLocaleString()}
            </Typography>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default RiskAssessment;
