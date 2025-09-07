import Header from '../components/Header';
import Footer from '../components/Footer';
import { useNavigate } from 'react-router-dom';
import { usePageTitle } from '../hooks/usePageTitle';

export default function SubscribeProcessing() {
  usePageTitle('CertAlert - Processing Payment');
  
  const navigate = useNavigate();
  return (
    <div className="start-page">
      <Header showButtons={true} dashboardButton={true} onDashboard={() => navigate('/dashboard')} />
      <div style={{ minHeight: 'calc(100vh - 180px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: 32, paddingBottom: 32 }}>
        <h2 style={{ marginBottom: 32 }}>Subscription Payment Processing</h2>
        <div style={{ marginBottom: 24, fontSize: 18, color: '#2563eb', textAlign: 'center' }}>
          Your payment is being processed.<br />
          You can check your subscription status in your profile.<br />
          If you have any issues, please contact support.
        </div>
        <button
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
          onClick={() => navigate('/dashboard')}
        >
          Go to Dashboard
        </button>
      </div>
      <Footer />
    </div>
  );
}
