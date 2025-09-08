import './App.css'
import { Routes, Route, Navigate } from 'react-router-dom'
import Start from './pages/Start'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import ResetPassword from './pages/ResetPassword'
import TermsOfService from './pages/TermsOfService'
import PrivacyPolicy from './pages/PrivacyPolicy'
import ContactUs from './pages/ContactUs'
import Subscribe from './pages/Subscribe';
import SubscribeProcessing from './pages/SubscribeProcessing';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
// OAuth pages
import OAuthSuccess from './pages/OAuth/OAuthSuccess';
import OAuthError from './pages/OAuth/OAuthError';
import OAuthLinkAccount from './pages/OAuth/OAuthLinkAccount';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Start />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/profile" element={<Profile />} />
  <Route path="/subscribe" element={<Subscribe />} />
  <Route path="/subscribe-processing" element={<SubscribeProcessing />} />
  <Route path="/reset-password" element={<ResetPassword />} />
  <Route path="/terms-of-service" element={<TermsOfService />} />
  <Route path="/privacy-policy" element={<PrivacyPolicy />} />
  <Route path="/contact-us" element={<ContactUs />} />
  <Route path="/admin/login" element={<AdminLogin />} />
  <Route path="/admin/dashboard" element={<AdminDashboard />} />
  {/* OAuth routes */}
  <Route path="/oauth/success" element={<OAuthSuccess />} />
  <Route path="/oauth/error" element={<OAuthError />} />
  <Route path="/oauth/link-account" element={<OAuthLinkAccount />} />
  {/* Catch-all route for unknown URLs */}
  <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App