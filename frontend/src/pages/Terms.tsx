import { Link } from 'react-router-dom'

export default function Terms() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Terms of Service</h1>
      <p className="text-sm text-slate-500 mb-8">Last updated: June 2026</p>
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-6 text-sm text-slate-700 leading-relaxed">
        <div><h2 className="text-base font-bold text-slate-900 mb-2">1. Acceptance of Terms</h2><p>By accessing or using M&A Due Diligence AI, you agree to be bound by these Terms of Service. If you do not agree, do not use the service.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">2. Description of Service</h2><p>M&A Due Diligence AI provides AI-powered document analysis, risk assessment, and compliance reporting for M&A transactions. The service is intended for use by licensed legal professionals.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">3. User Responsibilities</h2><p>You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account. You agree not to use the service for any unlawful purpose.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">4. Intellectual Property</h2><p>All content, features, and functionality of the service are owned by M&A Due Diligence AI and are protected by applicable intellectual property laws.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">5. Limitation of Liability</h2><p>The service is provided 'as is'. M&A Due Diligence AI shall not be liable for any indirect, incidental, or consequential damages arising from use of the service.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">6. Termination</h2><p>We reserve the right to suspend or terminate access to the service for violation of these terms or for non-payment.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">7. Governing Law</h2><p>These terms shall be governed by the laws of India.</p></div>
        <div><h2 className="text-base font-bold text-slate-900 mb-2">8. Contact</h2><p>For questions about these terms: support@yourfirm.com</p></div>
      </div>
    </div>
  )
}
