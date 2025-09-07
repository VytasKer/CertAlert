import React, { useState, useEffect } from 'react';
import { usePageTitle } from '../hooks/usePageTitle';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

function LogViewer() {
  const [log, setLog] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLog = async () => {
    setLoading(true);
    setError('');
    try {
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/logs/app-log`, {
        headers: {
          'x-api-key': apiKey
        }
      });
      if (!res.ok) {
        setError('Failed to fetch log: ' + (await res.text()));
        setLoading(false);
        return;
      }
      const data = await res.json();
      setLog(data.log);
    } catch (err) {
      setError('Failed to fetch log');
    }
    setLoading(false);
  };

  const downloadLog = () => {
    if (!log) {
      setError('No log data to download. Please refresh first.');
      return;
    }

    // Create a blob with the log content
    const blob = new Blob([log], { type: 'text/plain' });
    
    // Create a download URL
    const url = window.URL.createObjectURL(blob);
    
    // Create a temporary anchor element and trigger download
    const link = document.createElement('a');
    link.href = url;
    
    // Generate filename with current date and time
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
    link.download = `certalert-app-logs-${timestamp}.txt`;
    
    // Trigger the download
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  useEffect(() => {
    fetchLog();
  }, []);

  return (
    <div style={{ textAlign: 'left' }}>
      <h3 style={{ textAlign: 'left' }}>Application Logs</h3>
      <div style={{ marginBottom: 16, display: 'flex', gap: '12px' }}>
        <button 
          onClick={fetchLog} 
          style={{ 
            padding: '8px 24px', 
            background: '#2563eb', 
            color: '#fff', 
            border: 'none', 
            borderRadius: 4, 
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Refresh Log
        </button>
        <button 
          onClick={downloadLog} 
          style={{ 
            padding: '8px 24px', 
            background: '#059669', 
            color: '#fff', 
            border: 'none', 
            borderRadius: 4, 
            fontWeight: 600,
            cursor: 'pointer'
          }}
          disabled={!log || loading}
        >
          Download Log
        </button>
      </div>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
      <pre style={{ background: '#222', color: '#eee', padding: 16, borderRadius: 8, maxHeight: 500, overflowY: 'auto', fontSize: 14, textAlign: 'left' }}>{log}</pre>
    </div>
  );
}

function TrafficAnalytics() {
  const [todayStats, setTodayStats] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [dailyStats, setDailyStats] = useState(null);
  const [availableDates, setAvailableDates] = useState([]);
  const [summaryStats, setSummaryStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTodayStats = async () => {
    try {
      setLoading(true);
      setError('');
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/admin/traffic/stats/today`, {
        headers: { 'x-api-key': apiKey }
      });
      
      if (!res.ok) {
        throw new Error(`Failed to fetch today's stats: ${res.status}`);
      }
      
      const data = await res.json();
      setTodayStats(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching today stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDailyStats = async (date) => {
    try {
      setLoading(true);
      setError('');
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/admin/traffic/stats/${date}`, {
        headers: { 'x-api-key': apiKey }
      });
      
      if (!res.ok) {
        throw new Error(`Failed to fetch stats for ${date}: ${res.status}`);
      }
      
      const data = await res.json();
      setDailyStats(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching daily stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableDates = async () => {
    try {
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/admin/traffic/dates`, {
        headers: { 'x-api-key': apiKey }
      });
      
      if (res.ok) {
        const data = await res.json();
        setAvailableDates(data.available_dates || []);
      }
    } catch (err) {
      console.error('Error fetching available dates:', err);
    }
  };

  const fetchSummaryStats = async () => {
    try {
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/admin/traffic/stats/summary/7`, {
        headers: { 'x-api-key': apiKey }
      });
      
      if (res.ok) {
        const data = await res.json();
        setSummaryStats(data);
      }
    } catch (err) {
      console.error('Error fetching summary stats:', err);
    }
  };

  const downloadRawLogs = async (date) => {
    try {
      const apiKey = import.meta.env.VITE_ADMIN_API_KEY;
      const res = await fetch(`${BACKEND_BASE_URL}/admin/traffic/logs/${date}`, {
        headers: { 'x-api-key': apiKey }
      });
      
      if (!res.ok) {
        setError(`Failed to download logs for ${date}: ${res.status}`);
        return;
      }
      
      const logData = await res.text();
      
      // Create download
      const blob = new Blob([logData], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `traffic-${date}.log`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(err.message);
      console.error('Error downloading logs:', err);
    }
  };

  useEffect(() => {
    fetchTodayStats();
    fetchAvailableDates();
    fetchSummaryStats();
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchDailyStats(selectedDate);
    }
  }, [selectedDate]);

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  const StatCard = ({ title, value, subtitle, color = '#2563eb' }) => (
    <div style={{
      background: '#fff',
      borderRadius: 8,
      padding: 20,
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      textAlign: 'center',
      border: `2px solid ${color}`,
      minWidth: 140
    }}>
      <div style={{ fontSize: 24, fontWeight: 'bold', color, marginBottom: 4 }}>
        {formatNumber(value)}
      </div>
      <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>
        {title}
      </div>
      {subtitle && (
        <div style={{ fontSize: 12, color: '#666' }}>
          {subtitle}
        </div>
      )}
    </div>
  );

  return (
    <div style={{ textAlign: 'left' }}>
      <h3 style={{ textAlign: 'left', marginBottom: 24 }}>Traffic Analytics</h3>
      
      {error && (
        <div style={{ color: 'red', background: '#fee', padding: 12, borderRadius: 4, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {loading && <div style={{ marginBottom: 16 }}>Loading...</div>}

      {/* Today's Stats */}
      <div style={{ marginBottom: 32 }}>
        <h4 style={{ marginBottom: 16 }}>Today's Traffic</h4>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <StatCard 
            title="Total Requests" 
            value={todayStats?.total_requests} 
            subtitle="Today"
            color="#2563eb"
          />
          <StatCard 
            title="Unique Visitors" 
            value={todayStats?.unique_visitors} 
            subtitle="Unique IPs"
            color="#059669"
          />
          <StatCard 
            title="Avg Response Time" 
            value={todayStats?.avg_response_time} 
            subtitle="milliseconds"
            color="#dc2626"
          />
        </div>
      </div>

      {/* 7-Day Summary */}
      {summaryStats && (
        <div style={{ marginBottom: 32 }}>
          <h4 style={{ marginBottom: 16 }}>Last 7 Days Summary</h4>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <StatCard 
              title="Total Requests" 
              value={summaryStats.total_requests} 
              subtitle="7 days"
              color="#7c3aed"
            />
            <StatCard 
              title="Unique Visitors" 
              value={summaryStats.unique_visitors} 
              subtitle="7 days"
              color="#ea580c"
            />
            <StatCard 
              title="Daily Average" 
              value={summaryStats.avg_daily_requests} 
              subtitle="requests/day"
              color="#0891b2"
            />
          </div>
        </div>
      )}

      {/* Date Selector & Daily Stats */}
      <div style={{ marginBottom: 32 }}>
        <h4 style={{ marginBottom: 16 }}>Daily Analytics</h4>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
          <label>Date:</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{ padding: 8, border: '1px solid #ccc', borderRadius: 4 }}
          />
          <button
            onClick={() => downloadRawLogs(selectedDate)}
            style={{
              padding: '8px 16px',
              background: '#059669',
              color: '#fff',
              border: 'none',
              borderRadius: 4,
              fontWeight: 600,
              cursor: 'pointer'
            }}
            disabled={!dailyStats?.total_requests}
          >
            Download Logs
          </button>
        </div>

        {dailyStats && (
          <div style={{ background: '#fff', borderRadius: 8, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
            <h5 style={{ marginBottom: 16 }}>Statistics for {selectedDate}</h5>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 24 }}>
              <div>
                <strong>Total Requests:</strong> {formatNumber(dailyStats.total_requests)}
              </div>
              <div>
                <strong>Unique Visitors:</strong> {formatNumber(dailyStats.unique_visitors)}
              </div>
              <div>
                <strong>Avg Response Time:</strong> {dailyStats.avg_response_time}ms
              </div>
            </div>

            {/* Top Pages */}
            {dailyStats.top_pages?.length > 0 && (
              <div style={{ marginBottom: 24 }}>
                <h6 style={{ marginBottom: 12 }}>Top Pages</h6>
                <div style={{ background: '#f8f9fa', padding: 16, borderRadius: 8 }}>
                  {dailyStats.top_pages.slice(0, 10).map((page, index) => (
                    <div key={index} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontFamily: 'monospace', fontSize: 14 }}>{page.path}</span>
                      <span style={{ fontWeight: 'bold' }}>{formatNumber(page.count)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Status Codes */}
            {Object.keys(dailyStats.status_codes || {}).length > 0 && (
              <div style={{ marginBottom: 24 }}>
                <h6 style={{ marginBottom: 12 }}>HTTP Status Codes</h6>
                <div style={{ background: '#f8f9fa', padding: 16, borderRadius: 8 }}>
                  {Object.entries(dailyStats.status_codes).map(([status, count]) => (
                    <div key={status} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ 
                        color: status.startsWith('2') ? '#059669' : status.startsWith('4') ? '#dc2626' : '#ea580c'
                      }}>
                        {status}
                      </span>
                      <span>{formatNumber(count)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* HTTP Methods */}
            {Object.keys(dailyStats.methods || {}).length > 0 && (
              <div>
                <h6 style={{ marginBottom: 12 }}>HTTP Methods</h6>
                <div style={{ background: '#f8f9fa', padding: 16, borderRadius: 8 }}>
                  {Object.entries(dailyStats.methods).map(([method, count]) => (
                    <div key={method} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{method}</span>
                      <span>{formatNumber(count)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Available Dates */}
      {availableDates.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 16 }}>Available Log Dates</h4>
          <div style={{ background: '#f8f9fa', padding: 16, borderRadius: 8 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {availableDates.slice(0, 14).map(date => (
                <button
                  key={date}
                  onClick={() => setSelectedDate(date)}
                  style={{
                    padding: '6px 12px',
                    background: selectedDate === date ? '#2563eb' : '#fff',
                    color: selectedDate === date ? '#fff' : '#333',
                    border: '1px solid #ccc',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 12
                  }}
                >
                  {date}
                </button>
              ))}
            </div>
            {availableDates.length > 14 && (
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                ... and {availableDates.length - 14} more dates
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'database', label: 'Database' },
  { key: 'logs', label: 'Logs' },
  { key: 'traffic', label: 'Traffic Analytics' },
  { key: 'tables', label: 'Database Tables' },
  { key: 'parameters', label: 'Parameters' },
  { key: 'credits', label: 'App Credits' }
];

function ParametersTab() {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState({});

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/admin/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) {
        setError('Failed to fetch settings: ' + (await res.text()));
        return;
      }
      const data = await res.json();
      setSettings(data);
    } catch (e) {
      setError('Failed to fetch settings');
    }
    setLoading(false);
  };

  const updateSetting = async (key, value) => {
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/admin/settings/${key}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ value })
      });
      if (!res.ok) {
        setError('Failed to update setting: ' + (await res.text()));
        return;
      }
      const updatedSetting = await res.json();
      setSettings(prev => ({
        ...prev,
        [key]: updatedSetting
      }));
    } catch (e) {
      setError('Failed to update setting');
    }
  };

  const saveSetting = async (key) => {
    setSaving(prev => ({ ...prev, [key]: true }));
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/admin/settings/${key}/save`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) {
        setError('Failed to save setting: ' + (await res.text()));
        return;
      }
      const savedSetting = await res.json();
      setSettings(prev => ({
        ...prev,
        [key]: savedSetting
      }));
    } catch (e) {
      setError('Failed to save setting');
    } finally {
      setSaving(prev => ({ ...prev, [key]: false }));
    }
  };

  const resetSetting = async (key) => {
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/admin/settings/${key}/reset`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) {
        setError('Failed to reset setting: ' + (await res.text()));
        return;
      }
      const resetSetting = await res.json();
      setSettings(prev => ({
        ...prev,
        [key]: resetSetting
      }));
    } catch (e) {
      setError('Failed to reset setting');
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
        <div style={{ fontSize: 18 }}>Loading settings...</div>
      </div>
    );
  }

  return (
    <div>
      <h3>System Parameters</h3>
      <p style={{ color: '#6b7280', marginBottom: 24 }}>
        Configure system-wide parameters. Changes are applied after saving.
      </p>
      
      {error && (
        <div style={{ 
          background: '#fef2f2', 
          border: '1px solid #fecaca', 
          color: '#dc2626', 
          padding: '12px 16px', 
          borderRadius: 8, 
          marginBottom: 24 
        }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {Object.entries(settings).map(([key, setting]) => (
          <div key={key} style={{ 
            background: '#fff', 
            border: '1px solid #e5e7eb', 
            borderRadius: 8, 
            padding: '20px' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <h4 style={{ margin: 0, marginBottom: 4, fontSize: 16, fontWeight: 600 }}>
                  {setting.description}
                </h4>
                <div style={{ fontSize: 14, color: '#6b7280' }}>
                  Parameter: <code style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: 4 }}>{key}</code>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {setting.saved ? (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '4px', 
                    color: '#059669', 
                    fontSize: 14,
                    fontWeight: 500
                  }}>
                    <span style={{ fontSize: 16 }}>✓</span>
                    Saved
                  </div>
                ) : (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '4px', 
                    color: '#d97706', 
                    fontSize: 14,
                    fontWeight: 500
                  }}>
                    <span style={{ fontSize: 16 }}>●</span>
                    Not Saved
                  </div>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: 16 }}>
              <input
                type="number"
                value={setting.current_value}
                min={setting.min}
                max={setting.max}
                onChange={(e) => updateSetting(key, e.target.value)}
                style={{
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: 4,
                  width: '120px',
                  fontSize: 14
                }}
              />
              <span style={{ fontSize: 14, color: '#6b7280' }}>
                (Range: {setting.min} - {setting.max})
              </span>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => saveSetting(key)}
                disabled={setting.saved || saving[key]}
                style={{
                  padding: '8px 16px',
                  background: setting.saved ? '#9ca3af' : '#059669',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: setting.saved ? 'not-allowed' : 'pointer'
                }}
              >
                {saving[key] ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => resetSetting(key)}
                style={{
                  padding: '8px 16px',
                  background: '#6b7280',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Reset to Default
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AppCredits() {
  const appName = 'CertAlert';
  const developer = 'VytasKer';
  const version = import.meta.env.VITE_APP_VERSION || '0.0.1-alpha';
  return (
    <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 32, maxWidth: 400, margin: '40px auto' }}>
      <h3>App Credits</h3>
      <table style={{ width: '100%', fontSize: 18 }}>
        <tbody>
          <tr><td style={{ fontWeight: 600 }}>App name:</td><td>{appName}</td></tr>
          <tr><td style={{ fontWeight: 600 }}>Developer:</td><td>{developer}</td></tr>
          <tr><td style={{ fontWeight: 600 }}>Version:</td><td>{version}</td></tr>
        </tbody>
      </table>
    </div>
  );
}
function OverviewViewer() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchOverview = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/database/overview`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        setError('Failed to fetch overview: ' + (await res.text()));
        setLoading(false);
        return;
      }
      setOverview(await res.json());
    } catch (err) {
      setError('Failed to fetch overview');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  return (
    <div style={{ textAlign: 'left' }}>
      <h3>Database Overview</h3>
      <button onClick={fetchOverview} style={{ marginBottom: 16, padding: '8px 24px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600 }}>Refresh</button>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
      {overview && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 32 }}>
          {/* Users */}
          <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 24 }}>
            <h4>Users</h4>
            <div>Total: {overview.users.total}</div>
            <table style={{ marginTop: 8, width: '100%' }}>
              <thead><tr><th>Level</th><th>Count</th></tr></thead>
              <tbody>
                {Object.entries(overview.users.by_level).map(([level, count]) => (
                  <tr key={level}><td>{level}</td><td>{count}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Subscriptions */}
          <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 24 }}>
            <h4>Subscriptions</h4>
            <div>Total: {overview.subscriptions.total}</div>
            <table style={{ marginTop: 8, width: '100%' }}>
              <thead><tr><th>Status</th><th>Count</th></tr></thead>
              <tbody>
                {Object.entries(overview.subscriptions.by_status).map(([status, count]) => (
                  <tr key={status}><td>{status}</td><td>{count}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Certificates */}
          <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 24 }}>
            <h4>Certificates</h4>
            <div>Total: {overview.certificates.total}</div>
          </div>
          {/* Stripe Checkouts */}
          <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 24 }}>
            <h4>Stripe Checkouts</h4>
            <div>Total: {overview.stripe_checkouts.total}</div>
            <table style={{ marginTop: 8, width: '100%' }}>
              <thead><tr><th>Status</th><th>Count</th></tr></thead>
              <tbody>
                {Object.entries(overview.stripe_checkouts.by_status).map(([status, count]) => (
                  <tr key={status}><td>{status}</td><td>{count}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Stripe Webhooks */}
          <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: 24 }}>
            <h4>Stripe Webhooks</h4>
            <div>Total: {overview.stripe_webhooks.total}</div>
            <table style={{ marginTop: 8, width: '100%' }}>
              <thead><tr><th>Type</th><th>Count</th></tr></thead>
              <tbody>
                {Object.entries(overview.stripe_webhooks.by_type).map(([type, count]) => (
                  <tr key={type}><td>{type}</td><td>{count}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
function TablesViewer() {
  const [tables, setTables] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTables = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/database/tables-info`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        setError('Failed to fetch tables: ' + (await res.text()));
        setLoading(false);
        return;
      }
      setTables(await res.json());
    } catch (err) {
      setError('Failed to fetch tables');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTables();
  }, []);

  return (
    <div style={{ textAlign: 'left' }}>
      <h3>Database Tables & Columns</h3>
      <button onClick={fetchTables} style={{ marginBottom: 16, padding: '8px 24px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600 }}>Refresh</button>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
      {tables && Object.keys(tables).map(table => (
        <div key={table} style={{ marginBottom: 32 }}>
          <h4 style={{ marginBottom: 8 }}>{table}</h4>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Type</th>
                <th>NotNull</th>
                <th>Default</th>
                <th>PK</th>
              </tr>
            </thead>
            <tbody>
              {tables[table].map((col, idx) => (
                <tr key={idx}>
                  <td>{col[0]}</td>
                  <td>{col[1]}</td>
                  <td>{col[2]}</td>
                  <td>{col[3]}</td>
                  <td>{col[4]}</td>
                  <td>{col[5]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

export default function AdminDashboard() {
  usePageTitle('CertAlert - Admin Dashboard');
  
  const [activeTab, setActiveTab] = useState('database');
  const [query, setQuery] = useState('SELECT * FROM users');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleRunQuery = async () => {
    setError('');
    setResult(null);
    setCurrentPage(1); // Reset to first page on new query
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/database/run-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query })
      });
      if (!res.ok) {
        setError('Query failed: ' + (await res.text()));
        return;
      }
      setResult(await res.json());
    } catch (e) {
      setError('Query failed');
    }
  };

  const downloadCSV = () => {
    if (!result || !result.rows.length) return;

    setIsDownloading(true);
    try {
      // Create CSV content
      const csvHeaders = result.columns.join(',');
      const csvRows = result.rows.map(row => 
        row.map(cell => {
          // Handle JSON objects and null values
          if (cell === null || cell === undefined) return '';
          if (typeof cell === 'object') return `"${JSON.stringify(cell).replace(/"/g, '""')}"`;
          if (typeof cell === 'string' && (cell.includes(',') || cell.includes('"') || cell.includes('\n'))) {
            return `"${cell.replace(/"/g, '""')}"`;
          }
          return cell;
        }).join(',')
      );
      
      const csvContent = [csvHeaders, ...csvRows].join('\n');
      
      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `query_results_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error('Failed to download CSV:', e);
      setError('Failed to download CSV file');
    } finally {
      setIsDownloading(false);
    }
  };

  // Pagination logic
  const getPaginatedRows = () => {
    if (!result || !result.rows) return [];
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return result.rows.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    if (!result || !result.rows) return 0;
    return Math.ceil(result.rows.length / rowsPerPage);
  };

  const handleLogout = () => {
    localStorage.removeItem('certalert_jwt');
    window.location.href = '/admin/login';
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f7f7fa' }}>
      {/* Sidebar Tabs */}
      <div style={{ width: '20vw', minWidth: '200px', maxWidth: '400px', background: '#fff', boxShadow: '2px 0 8px rgba(0,0,0,0.04)', padding: '32px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100vh', position: 'fixed', left: 0, top: 0, zIndex: 2 }}>
        <h2 style={{ marginBottom: 32 }}>Admin Panel</h2>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              width: '80%',
              padding: '12px 0',
              marginBottom: 16,
              background: activeTab === tab.key ? '#2563eb' : '#f7f7fa',
              color: activeTab === tab.key ? '#fff' : '#222',
              border: 'none',
              borderRadius: 4,
              fontWeight: 600,
              fontSize: 16,
              cursor: 'pointer',
              boxShadow: activeTab === tab.key ? '0 2px 8px rgba(0,0,0,0.07)' : 'none'
            }}
          >
            {tab.label}
          </button>
        ))}
        <button onClick={handleLogout} style={{ width: '80%', padding: '12px 0', marginTop: 32, background: '#e53e3e', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600, fontSize: 16, cursor: 'pointer' }}>Logout</button>
      </div>
      {/* Main Content */}
      <div style={{ marginLeft: '5vw', width: '80vw', maxWidth: '100%', padding: '48px 40px', overflowX: 'auto' }}>
        {activeTab === 'overview' && <OverviewViewer />}
        {activeTab === 'logs' && <LogViewer />}
        {activeTab === 'traffic' && <TrafficAnalytics />}
        {activeTab === 'database' && (
          <div>
            <h3>Database Query</h3>
            <textarea value={query} onChange={e => setQuery(e.target.value)} rows={4} style={{ width: '100%', marginBottom: 16, fontSize: 16 }} />
            <div style={{ display: 'flex', gap: '12px', marginBottom: 16, alignItems: 'center' }}>
              <button onClick={handleRunQuery} style={{ padding: '10px 32px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600, fontSize: 16 }}>Run Query</button>
              {result && result.rows && result.rows.length > 0 && (
                <>
                  <button 
                    onClick={downloadCSV} 
                    disabled={isDownloading}
                    style={{ 
                      padding: '10px 24px', 
                      background: isDownloading ? '#9ca3af' : '#059669', 
                      color: '#fff', 
                      border: 'none', 
                      borderRadius: 4, 
                      fontWeight: 600, 
                      fontSize: 16,
                      cursor: isDownloading ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {isDownloading ? 'Downloading...' : 'Download CSV'}
                  </button>
                  <span style={{ color: '#6b7280', fontSize: 14 }}>
                    Total rows: {result.rows.length}
                  </span>
                </>
              )}
            </div>
            {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
            {result && (
              <div style={{ marginTop: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                  <h4>Results:</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <label style={{ fontSize: 14, color: '#6b7280' }}>
                      Rows per page:
                      <select 
                        value={rowsPerPage} 
                        onChange={e => {
                          setRowsPerPage(Number(e.target.value));
                          setCurrentPage(1);
                        }}
                        style={{ marginLeft: 8, padding: '4px 8px', border: '1px solid #d1d5db', borderRadius: 4 }}
                      >
                        <option value={10}>10</option>
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                    </label>
                  </div>
                </div>
                <div style={{ overflowX: 'auto', border: '1px solid #e5e7eb', borderRadius: 8, marginBottom: 16 }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ background: '#f9fafb' }}>
                        {result.columns.map(col => (
                          <th key={col} style={{ borderBottom: '1px solid #e5e7eb', padding: '12px 8px', textAlign: 'left', fontWeight: 600, color: '#374151' }}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {getPaginatedRows().map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                          {row.map((cell, i) => (
                            <td key={i} style={{ padding: '12px 8px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 14 }}>
                              {cell === null ? (
                                <span style={{ color: '#9ca3af', fontStyle: 'italic' }}>null</span>
                              ) : typeof cell === 'object' ? (
                                <span style={{ color: '#6366f1', cursor: 'pointer' }} title={JSON.stringify(cell, null, 2)}>
                                  {JSON.stringify(cell)}
                                </span>
                              ) : (
                                String(cell)
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {getTotalPages() > 1 && (
                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      style={{
                        padding: '8px 16px',
                        border: '1px solid #d1d5db',
                        borderRadius: 4,
                        background: currentPage === 1 ? '#f9fafb' : '#fff',
                        color: currentPage === 1 ? '#9ca3af' : '#374151',
                        cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
                      }}
                    >
                      Previous
                    </button>
                    <span style={{ padding: '8px 16px', color: '#6b7280' }}>
                      Page {currentPage} of {getTotalPages()}
                    </span>
                    <button
                      onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                      disabled={currentPage === getTotalPages()}
                      style={{
                        padding: '8px 16px',
                        border: '1px solid #d1d5db',
                        borderRadius: 4,
                        background: currentPage === getTotalPages() ? '#f9fafb' : '#fff',
                        color: currentPage === getTotalPages() ? '#9ca3af' : '#374151',
                        cursor: currentPage === getTotalPages() ? 'not-allowed' : 'pointer'
                      }}
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        {activeTab === 'tables' && <TablesViewer />}
        {activeTab === 'parameters' && <ParametersTab />}
        {activeTab === 'credits' && <AppCredits />}
      </div>
    </div>
  );
}