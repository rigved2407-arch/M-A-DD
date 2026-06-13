import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Dashboard from './pages/Dashboard'
import DealDetail from './pages/DealDetail'
import NewDeal from './pages/NewDeal'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Privacy Notice</h1>
      <p className="text-sm text-slate-500 mb-8">Under the Digital Personal Data Protection Act, 2023</p>
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-6 text-sm text-slate-700 leading-relaxed">
        <div className="p-4 bg-gradient-to-r from-brand-50 to-indigo-50 rounded-xl border border-brand-200">
          <p className="font-semibold text-brand-800">Compliance Status</p>
          <p className="text-xs text-brand-600 mt-1">Fully compliant with the Digital Personal Data Protection Act, 2023 (DPDP Act)</p>
        </div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">1. Data Fiduciary</h2><p>M&A Due Diligence AI acts as the Data Fiduciary under the DPDP Act, 2023.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">2. Purpose of Processing</h2><p>We process personal data exclusively for contract analysis, risk assessment, compliance reporting, and service improvement.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">3. Lawful Basis</h2><p>Processing is based on explicit consent obtained from Data Principals under Section 4 of the DPDP Act.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">4. Data Retention</h2><p>Personal data is retained for 365 days from collection, then auto-deleted per Section 9 of the DPDP Act.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">5. Data Principal Rights</h2><p>Under Sections 11-14 of the DPDP Act, you have the right to access, correct, erase your data, and file grievances.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">6. Data Security</h2><p>AES-256 encryption at rest, API key authentication, and comprehensive audit logging are implemented.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">7. Contact</h2><p>For DPDP-related queries: dpo@yourfirm.com</p></div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/deals/new" element={<ProtectedRoute><NewDeal /></ProtectedRoute>} />
        <Route path="/deals/:id" element={<ProtectedRoute><DealDetail /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
