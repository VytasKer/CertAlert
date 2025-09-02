import React, { useState, useEffect } from 'react';

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

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'database', label: 'Database' },
  { key: 'logs', label: 'Logs' },
  { key: 'tables', label: 'Database Tables' },
  { key: 'credits', label: 'App credits' }
];

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
  const [activeTab, setActiveTab] = useState('database');
  const [query, setQuery] = useState('SELECT * FROM users');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleRunQuery = async () => {
    setError('');
    setResult(null);
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
        {activeTab === 'database' && (
          <div>
            <h3>Database Query</h3>
            <textarea value={query} onChange={e => setQuery(e.target.value)} rows={4} style={{ width: '100%', marginBottom: 16, fontSize: 16 }} />
            <button onClick={handleRunQuery} style={{ padding: '10px 32px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600, fontSize: 16 }}>Run Query</button>
            {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
            {result && (
              <div style={{ marginTop: 24 }}>
                <h4>Results:</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr>
                        {result.columns.map(col => (
                          <th key={col} style={{ borderBottom: '1px solid #eee', padding: '8px' }}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, idx) => (
                        <tr key={idx}>
                          {row.map((cell, i) => (
                            <td key={i} style={{ borderBottom: '1px solid #eee', padding: '8px' }}>{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
        {activeTab === 'tables' && <TablesViewer />}
        {activeTab === 'credits' && <AppCredits />}
      </div>
    </div>
  );
}