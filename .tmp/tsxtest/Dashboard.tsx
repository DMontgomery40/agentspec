import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material';
import { IconButton } from '@mui/material';
import AdminAPIClient from '../api/client';
import type { HealthStatus } from '../api/types';

interface DashboardProps {
  client: AdminAPIClient;
  onNavigate?: (to: number | string) => void;
}

/**
 * ---agentspec
 * what: |
 *   Generates a dashboard UI component for monitoring system health and configuration.
 *     deps:
 *       calls:
 *         - client.getConfig
 *         - client.getHealthStatus
 *         - client.listPlugins
 *         - client.startPolling
 *         - fetchConfig
 *         - fetchHealth
 *         - getStatusColor
 *         - getStatusIcon
 *         - navigator.clipboard.writeText
 *         - new Date(health.timestamp).toLocaleString
 *         - onNavigate
 *         - sessionStorage.getItem
 *         - sessionStorage.removeItem
 *         - setCfg
 *         - setError
 *         - setHealth
 *         - setJustApplied
 *         - setLoading
 *         - setPlugins
 *         - setTimeout
 *         - useEffect
 *         - useState
 *       imports:
 *         - AdminAPIClient
 *         - import AdminAPIClient from '../api/client';
 *         - import type { HealthStatus } from '../api/types';
 *         - import {
 *   Box,
 *   Card,
 *   CardContent,
 *   Typography,
 *   Grid,
 *   Chip,
 *   Button,
 *   CircularProgress,
 *   Alert,
 *   Tooltip,
 * } from '@mui/material';
 *         - import {
 *   Refresh as RefreshIcon,
 *   CheckCircle as CheckCircleIcon,
 *   Warning as WarningIcon,
 *   Error as ErrorIcon,
 *   ContentCopy as ContentCopyIcon,
 * } from '@mui/icons-material';
 *         - import { IconButton } from '@mui/material';
 *         - import { useState, useEffect } from 'react';
 *         - {
 *   Box,
 *   Card,
 *   CardContent,
 *   Typography,
 *   Grid,
 *   Chip,
 *   Button,
 *   CircularProgress,
 *   Alert,
 *   Tooltip,
 * }
 *         - {
 *   Refresh as RefreshIcon,
 *   CheckCircle as CheckCircleIcon,
 *   Warning as WarningIcon,
 *   Error as ErrorIcon,
 *   ContentCopy as ContentCopyIcon,
 * }
 *         - { HealthStatus }
 *         - { IconButton }
 *         - { useState, useEffect }
 *
 *
 * why: |
 *   Provides a structured interface for displaying health status, configuration data, and plugin information. Uses React state management for dynamic updates and error handling.
 *
 * guardrails:
 *   - DO NOT hardcode API endpoints; use client prop for external calls
 *   - DO NOT render sensitive data without proper authorization checks
 *   - ASK USER: Confirm if additional UI components (charts, tables) are needed
 *
 *     changelog:
 *       - "- none yet"
 *     ---/agentspec
 * AGENTSPEC_CONTEXT: function Dashboard documented
 *
 */
function Dashboard({ client, onNavigate }: DashboardProps) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [justApplied, setJustApplied] = useState<boolean>(false);
  const [cfg, setCfg] = useState<any | null>(null);
  const [plugins, setPlugins] = useState<any[] | null>(null);

  /**
   * ---agentspec
   * what: |
   *   Fetches health status from client and updates state
   *     deps:
   *       calls:
   *         - client.getConfig
   *         - client.getHealthStatus
   *         - client.listPlugins
   *         - client.startPolling
   *         - fetchConfig
   *         - fetchHealth
   *         - getStatusColor
   *         - getStatusIcon
   *         - navigator.clipboard.writeText
   *         - new Date(health.timestamp).toLocaleString
   *         - onNavigate
   *         - sessionStorage.getItem
   *         - sessionStorage.removeItem
   *         - setCfg
   *         - setError
   *         - setHealth
   *         - setJustApplied
   *         - setLoading
   *         - setPlugins
   *         - setTimeout
   *         - useEffect
   *         - useState
   *       imports:
   *         - AdminAPIClient
   *         - import AdminAPIClient from '../api/client';
   *         - import type { HealthStatus } from '../api/types';
   *         - import {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * } from '@mui/material';
   *         - import {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * } from '@mui/icons-material';
   *         - import { IconButton } from '@mui/material';
   *         - import { useState, useEffect } from 'react';
   *         - {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * }
   *         - {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * }
   *         - { HealthStatus }
   *         - { IconButton }
   *         - { useState, useEffect }
   *
   *
   * why: |
   *   Provides health information to UI components; handles errors gracefully
   *
   * guardrails:
   *   - DO NOT modify client.getHealthStatus() call; maintain API contract
   *   - ASK USER: Confirm client implementation before changing
   *
   *     changelog:
   *       - "- none yet"
   *     ---/agentspec
   * AGENTSPEC_CONTEXT: function fetchHealth documented
   *
   */
  const fetchHealth = async () => {
    try {
      setError(null);
      const data = await client.getHealthStatus();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health status');
    } finally {
      setLoading(false);
    }
  };

  /**
   * ---agentspec
   * what: |
   *   Fetches configuration and plugins list when v3 plugins are enabled
   *     deps:
   *       calls:
   *         - client.getConfig
   *         - client.getHealthStatus
   *         - client.listPlugins
   *         - client.startPolling
   *         - fetchConfig
   *         - fetchHealth
   *         - getStatusColor
   *         - getStatusIcon
   *         - navigator.clipboard.writeText
   *         - new Date(health.timestamp).toLocaleString
   *         - onNavigate
   *         - sessionStorage.getItem
   *         - sessionStorage.removeItem
   *         - setCfg
   *         - setError
   *         - setHealth
   *         - setJustApplied
   *         - setLoading
   *         - setPlugins
   *         - setTimeout
   *         - useEffect
   *         - useState
   *       imports:
   *         - AdminAPIClient
   *         - import AdminAPIClient from '../api/client';
   *         - import type { HealthStatus } from '../api/types';
   *         - import {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * } from '@mui/material';
   *         - import {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * } from '@mui/icons-material';
   *         - import { IconButton } from '@mui/material';
   *         - import { useState, useEffect } from 'react';
   *         - {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * }
   *         - {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * }
   *         - { HealthStatus }
   *         - { IconButton }
   *         - { useState, useEffect }
   *
   *
   * why: |
   *   Implements conditional plugin loading based on configuration. Uses async/await for API calls and handles nested error cases. Follows pattern of lazy-loading plugins only when needed.
   *
   * guardrails:
   *   - DO NOT assume client methods exist without checking; validate client API surface
   *   - DO NOT hardcode plugin list fetching; respect config-driven enabling
   *
   *     changelog:
   *       - "- none yet"
   *     ---/agentspec
   * AGENTSPEC_CONTEXT: function fetchConfig documented
   *
   */
  const fetchConfig = async () => {
    try {
      const c = await client.getConfig();
      setCfg(c);
      // Lazy-load plugins list only when v3 plugins are enabled
      if (c?.v3_plugins?.enabled) {
        try {
          const list = await client.listPlugins();
          setPlugins(list?.items || []);
        } catch {
          setPlugins([]);
        }
      } else {
        setPlugins(null);
      }
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchHealth();
    if (sessionStorage.getItem('fb_admin_applied') === '1') {
      setJustApplied(true);
      sessionStorage.removeItem('fb_admin_applied');
      setTimeout(() => setJustApplied(false), 4000);
    }
    
    // Start polling
    /**
     * ---agentspec
     * what: |
     *   Polls client for health data and fetches config on updates.
     *     deps:
     *       calls:
     *         - client.getConfig
     *         - client.getHealthStatus
     *         - client.listPlugins
     *         - client.startPolling
     *         - fetchConfig
     *         - fetchHealth
     *         - getStatusColor
     *         - getStatusIcon
     *         - navigator.clipboard.writeText
     *         - new Date(health.timestamp).toLocaleString
     *         - onNavigate
     *         - sessionStorage.getItem
     *         - sessionStorage.removeItem
     *         - setCfg
     *         - setError
     *         - setHealth
     *         - setJustApplied
     *         - setLoading
     *         - setPlugins
     *         - setTimeout
     *         - useEffect
     *         - useState
     *       imports:
     *         - AdminAPIClient
     *         - import AdminAPIClient from '../api/client';
     *         - import type { HealthStatus } from '../api/types';
     *         - import {
     *   Box,
     *   Card,
     *   CardContent,
     *   Typography,
     *   Grid,
     *   Chip,
     *   Button,
     *   CircularProgress,
     *   Alert,
     *   Tooltip,
     * } from '@mui/material';
     *         - import {
     *   Refresh as RefreshIcon,
     *   CheckCircle as CheckCircleIcon,
     *   Warning as WarningIcon,
     *   Error as ErrorIcon,
     *   ContentCopy as ContentCopyIcon,
     * } from '@mui/icons-material';
     *         - import { IconButton } from '@mui/material';
     *         - import { useState, useEffect } from 'react';
     *         - {
     *   Box,
     *   Card,
     *   CardContent,
     *   Typography,
     *   Grid,
     *   Chip,
     *   Button,
     *   CircularProgress,
     *   Alert,
     *   Tooltip,
     * }
     *         - {
     *   Refresh as RefreshIcon,
     *   CheckCircle as CheckCircleIcon,
     *   Warning as WarningIcon,
     *   Error as ErrorIcon,
     *   ContentCopy as ContentCopyIcon,
     * }
     *         - { HealthStatus }
     *         - { IconButton }
     *         - { useState, useEffect }
     *
     *
     * why: |
     *   Maintains real-time health status and config synchronization. Uses startPolling for continuous updates.
     *
     * guardrails:
     *   - "DO NOT modify polling interval without explicit user confirmation; default is 5s"
     *   - "DO NOT call fetchConfig() on error; only on successful health updates"
     *
     *     changelog:
     *       - "- none yet"
     *     ---/agentspec
     * AGENTSPEC_CONTEXT: function cleanup documented
     *
     */
    const cleanup = client.startPolling((data) => {
      setHealth(data);
      setError(null);
      fetchConfig();
    });
    
    return cleanup;
  }, [client]);

  /**
   * ---agentspec
   * what: |
   *   Generates status indicators with color and icon based on health status
   *     deps:
   *       calls:
   *         - client.getConfig
   *         - client.getHealthStatus
   *         - client.listPlugins
   *         - client.startPolling
   *         - fetchConfig
   *         - fetchHealth
   *         - getStatusColor
   *         - getStatusIcon
   *         - navigator.clipboard.writeText
   *         - new Date(health.timestamp).toLocaleString
   *         - onNavigate
   *         - sessionStorage.getItem
   *         - sessionStorage.removeItem
   *         - setCfg
   *         - setError
   *         - setHealth
   *         - setJustApplied
   *         - setLoading
   *         - setPlugins
   *         - setTimeout
   *         - useEffect
   *         - useState
   *       imports:
   *         - AdminAPIClient
   *         - import AdminAPIClient from '../api/client';
   *         - import type { HealthStatus } from '../api/types';
   *         - import {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * } from '@mui/material';
   *         - import {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * } from '@mui/icons-material';
   *         - import { IconButton } from '@mui/material';
   *         - import { useState, useEffect } from 'react';
   *         - {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * }
   *         - {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * }
   *         - { HealthStatus }
   *         - { IconButton }
   *         - { useState, useEffect }
   *
   *
   * why: |
   *   Provides visual feedback for system health states using consistent styling and icons
   *
   * guardrails:
   *   - DO NOT change color scheme without explicit user confirmation
   *   - DO NOT modify icon set without explicit user confirmation
   *
   *     changelog:
   *       - "- none yet"
   *     ---/agentspec
   * AGENTSPEC_CONTEXT: function getStatusColor documented
   *
   */
  const getStatusColor = (healthy: boolean) => {
    return healthy ? 'success' : 'error';
  };

  /**
   * ---agentspec
   * what: |
   *   Renders loading state with centered CircularProgress spinner
   *     deps:
   *       calls:
   *         - client.getConfig
   *         - client.getHealthStatus
   *         - client.listPlugins
   *         - client.startPolling
   *         - fetchConfig
   *         - fetchHealth
   *         - getStatusColor
   *         - getStatusIcon
   *         - navigator.clipboard.writeText
   *         - new Date(health.timestamp).toLocaleString
   *         - onNavigate
   *         - sessionStorage.getItem
   *         - sessionStorage.removeItem
   *         - setCfg
   *         - setError
   *         - setHealth
   *         - setJustApplied
   *         - setLoading
   *         - setPlugins
   *         - setTimeout
   *         - useEffect
   *         - useState
   *       imports:
   *         - AdminAPIClient
   *         - import AdminAPIClient from '../api/client';
   *         - import type { HealthStatus } from '../api/types';
   *         - import {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * } from '@mui/material';
   *         - import {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * } from '@mui/icons-material';
   *         - import { IconButton } from '@mui/material';
   *         - import { useState, useEffect } from 'react';
   *         - {
   *   Box,
   *   Card,
   *   CardContent,
   *   Typography,
   *   Grid,
   *   Chip,
   *   Button,
   *   CircularProgress,
   *   Alert,
   *   Tooltip,
   * }
   *         - {
   *   Refresh as RefreshIcon,
   *   CheckCircle as CheckCircleIcon,
   *   Warning as WarningIcon,
   *   Error as ErrorIcon,
   *   ContentCopy as ContentCopyIcon,
   * }
   *         - { HealthStatus }
   *         - { IconButton }
   *         - { useState, useEffect }
   *
   *
   * why: |
   *   Handles asynchronous data loading by displaying a visual indicator
   *   while waiting for data to load. Uses Material-UI components for
   *   consistent styling and responsive layout.
   *
   * guardrails:
   *   - DO NOT remove CircularProgress without replacement; loading state is required
   *   - DO NOT change minHeight from 200px; maintains consistent UI spacing
   *
   *     changelog:
   *       - "- none yet"
   *     ---/agentspec
   * AGENTSPEC_CONTEXT: function getStatusIcon documented
   *
   */
  const getStatusIcon = (healthy: boolean) => {
    return healthy ? <CheckCircleIcon /> : <ErrorIcon />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {justApplied && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Configuration applied successfully.
        </Alert>
      )}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchHealth}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {health && (
        <Grid container spacing={{ xs: 2, md: 3 }}>
          {/* System Status */}
          <Grid item xs={12} sm={6} lg={3}>
            <Tooltip title="Click to view detailed diagnostics" arrow>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'rgba(59, 160, 255, 0.08)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => onNavigate?.('tools/diagnostics')}
              >
              <CardContent sx={{ pb: { xs: 1, sm: 2 } }}>
                <Box display="flex" alignItems="center" mb={{ xs: 1, sm: 2 }}>
                  {getStatusIcon(health.backend_healthy)}
                  <Typography variant="h6" component="h2" sx={{ ml: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                    System Status
                  </Typography>
                </Box>
                <Chip
                  label={health.backend_healthy ? 'Healthy' : 'Unhealthy'}
                  color={getStatusColor(health.backend_healthy)}
                  variant="outlined"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Backend: {health.backend}
                </Typography>
              </CardContent>
              </Card>
            </Tooltip>
          </Grid>

          {/* Job Queue */}
          <Grid item xs={12} sm={6} lg={3}>
            <Tooltip title="Click to view all jobs" arrow>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'rgba(59, 160, 255, 0.08)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => onNavigate?.(2)} // Navigate to Jobs tab (index 2)
              >
              <CardContent sx={{ pb: { xs: 1, sm: 2 } }}>
                <Typography variant="h6" component="h2" gutterBottom sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                  Job Queue
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Queued:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {health.jobs.queued}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">In Progress:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {health.jobs.in_progress}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Recent Failures:</Typography>
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={health.jobs.recent_failures > 0 ? 'error' : 'text.primary'}
                    >
                      {health.jobs.recent_failures}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
              </Card>
            </Tooltip>
          </Grid>

          {/* Inbound Status */}
          <Grid item xs={12} sm={6} lg={3}>
            <Tooltip title="Click to view inbound faxes" arrow>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'rgba(59, 160, 255, 0.08)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => onNavigate?.(3)} // Navigate to Inbound tab (index 3)
              >
                <CardContent sx={{ pb: { xs: 1, sm: 2 } }}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                    Inbound Fax
                  </Typography>
                  <Chip
                    label={health.inbound_enabled ? 'Enabled' : 'Disabled'}
                    color={health.inbound_enabled ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </CardContent>
              </Card>
            </Tooltip>
          </Grid>

          {/* Security Status */}
          <Grid item xs={12} sm={6} lg={3}>
            <Tooltip title="Click to view security settings" arrow>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'rgba(59, 160, 255, 0.08)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => onNavigate?.('settings/security')}
              >
                <CardContent sx={{ pb: { xs: 1, sm: 2 } }}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                    Security
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <Box display="flex" alignItems="center">
                      {health.require_auth ? <CheckCircleIcon color="success" /> : <WarningIcon color="warning" />}
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {health.require_auth ? 'Auth Required' : 'Auth Optional'}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                      {health.api_keys_configured ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />}
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {health.api_keys_configured ? 'API Keys Configured' : 'No API Keys'}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Tooltip>
          </Grid>

          {/* Config Overview */}
          <Grid item xs={12} md={6}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => onNavigate?.('settings/settings')}>
              <CardContent>
                <Typography variant="h6" gutterBottom>Config Overview</Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}><Typography variant="body2" color="text.secondary">Backend</Typography></Grid>
                  <Grid item xs={6}><Chip size="small" label={cfg?.backend || health.backend} /></Grid>
                  <Grid item xs={6}><Typography variant="body2" color="text.secondary">Storage</Typography></Grid>
                  <Grid item xs={6}><Chip size="small" label={cfg?.storage?.backend || 'local'} /></Grid>
                  <Grid item xs={6}><Typography variant="body2" color="text.secondary">Require API Key</Typography></Grid>
                  <Grid item xs={6}><Chip size="small" label={(cfg?.require_api_key ? 'Enabled' : 'Disabled')} color={cfg?.require_api_key ? 'success' : 'default'} variant="outlined" /></Grid>
                  <Grid item xs={6}><Typography variant="body2" color="text.secondary">Enforce HTTPS</Typography></Grid>
                  <Grid item xs={6}><Chip size="small" label={(cfg?.enforce_public_https ? 'Enabled' : 'Disabled')} color={cfg?.enforce_public_https ? 'success' : 'default'} variant="outlined" /></Grid>
                  <Grid item xs={6}><Typography variant="body2" color="text.secondary">v3 Plugins</Typography></Grid>
                  <Grid item xs={6}><Chip size="small" label={(cfg?.v3_plugins?.enabled ? `Enabled (${cfg?.v3_plugins?.active_outbound || '-'})` : 'Disabled')} color={cfg?.v3_plugins?.enabled ? 'success' : 'default'} variant="outlined" /></Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* MCP Overview */}
          <Grid item xs={12} md={6}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => onNavigate?.('settings/mcp')}>
              <CardContent>
                <Typography variant="h6" gutterBottom>MCP Overview</Typography>
                <Grid container spacing={1} alignItems="center">
                  <Grid item xs={4}><Typography variant="body2" color="text.secondary">SSE</Typography></Grid>
                  <Grid item xs={8}>
                    <Chip size="small" label={cfg?.mcp?.sse_enabled ? 'Enabled' : 'Disabled'} color={cfg?.mcp?.sse_enabled ? 'success' : 'default'} variant="outlined" />
                    {cfg?.mcp?.sse_enabled && (
                      <Tooltip title="Copy SSE URL">
                        <IconButton size="small" sx={{ ml: 1 }} onClick={() => navigator.clipboard.writeText(`${window.location.origin}${cfg?.mcp?.sse_path || '/mcp/sse'}`)}>
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Grid>
                  <Grid item xs={4}><Typography variant="body2" color="text.secondary">HTTP</Typography></Grid>
                  <Grid item xs={8}>
                    <Chip size="small" label={cfg?.mcp?.http_enabled ? 'Enabled' : 'Disabled'} color={cfg?.mcp?.http_enabled ? 'success' : 'default'} variant="outlined" />
                    {cfg?.mcp?.http_enabled && (
                      <Tooltip title="Copy HTTP URL">
                        <IconButton size="small" sx={{ ml: 1 }} onClick={() => navigator.clipboard.writeText(`${window.location.origin}${cfg?.mcp?.http_path || '/mcp/http'}`)}>
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Grid>
                  <Grid item xs={4}><Typography variant="body2" color="text.secondary">OAuth</Typography></Grid>
                  <Grid item xs={8}><Chip size="small" label={cfg?.mcp?.require_oauth ? 'Required' : 'Optional'} variant="outlined" /></Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Plugins (feature-gated) */}
          {cfg?.v3_plugins?.enabled && (
            <Grid item xs={12} md={6}>
              <Card sx={{ cursor: 'pointer' }} onClick={() => onNavigate?.('tools/plugins')}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Plugins</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Outbound: {cfg?.v3_plugins?.active_outbound || '-'} • Installed: {plugins?.length ?? 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Manifest warnings appear under Diagnostics.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* SDK & Quickstart */}
          <Grid item xs={12} md={cfg?.v3_plugins?.enabled ? 6 : 12}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => onNavigate?.('send')}>
              <CardContent>
                <Typography variant="h6" gutterBottom>SDK & Quickstart</Typography>
                <Typography variant="body2">Base URL: {window.location.origin}</Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>Header: X-API-Key: &lt;your key&gt;</Typography>
                <Typography variant="body2" color="text.secondary">Node:</Typography>
                <Box component="pre" sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1, overflow: 'auto' }}>{`npm i faxbot@1.0.2
node -e "(async()=>{const FaxbotClient=require('faxbot');const c=new FaxbotClient('${window.location.origin}','<key>');const r=await c.sendFax('+15551234567','/path/to/file.pdf');console.log(r)})()"`}</Box>
                <Typography variant="body2" color="text.secondary">Python:</Typography>
                <Box component="pre" sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1, overflow: 'auto' }}>{`pip install faxbot==1.0.2
python - <<'PY'
from faxbot import FaxbotClient
c=FaxbotClient('${window.location.origin}','<key>')
print(c.send_fax('+15551234567','/path/to/file.pdf'))
PY`}</Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Last Updated */}
          <Grid item xs={12}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => onNavigate?.('tools/diagnostics')}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Last updated: {new Date(health.timestamp).toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Auto-refreshing every 5 seconds
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default Dashboard;
