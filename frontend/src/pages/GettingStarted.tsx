import { Link } from 'react-router-dom'

export default function GettingStarted() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Getting Started Guide</h1>
      <p className="text-sm text-slate-500 mb-8">Everything your firm needs to start using M&A Due Diligence AI</p>

      <div className="space-y-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">1. Create Your Account</h2>
          <p className="text-sm text-slate-600 mb-3">Register your law firm with a name, email, and password. You'll be set up as the admin with full access.</p>
          <Link to="/register" className="text-sm text-brand-600 font-medium hover:underline">Create account &rarr;</Link>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">2. Invite Your Team</h2>
          <p className="text-sm text-slate-600 mb-3">Go to Admin &rarr; Team to invite partners, associates, and reviewers. Assign roles to control access levels.</p>
          <ul className="text-xs text-slate-500 space-y-1 ml-4 list-disc">
            <li><strong>Partner</strong> &mdash; Full access to all deals and settings</li>
            <li><strong>Associate</strong> &mdash; Can create deals, upload docs, run analysis</li>
            <li><strong>Reviewer</strong> &mdash; Read-only access to review findings</li>
            <li><strong>Admin</strong> &mdash; Full access plus user management</li>
          </ul>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">3. Add Clients</h2>
          <p className="text-sm text-slate-600">Navigate to New Deal and create a client profile. Client details carry across all your deals for that client.</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">4. Create a Deal Room</h2>
          <p className="text-sm text-slate-600 mb-3">Set up a new deal with target company details, deal type, and description. Each deal is a secure room for documents and analysis.</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">5. Upload Documents</h2>
          <p className="text-sm text-slate-600 mb-3">Upload PDFs, DOCX, XLSX, and other documents. The system automatically classifies them by workstream (legal, financial, tax, HR, etc.).</p>
          <p className="text-xs text-slate-400">Supported: PDF, DOCX, XLSX, PPTX, CSV, TXT, MD &mdash; up to 100MB per file</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">6. Run AI Analysis</h2>
          <p className="text-sm text-slate-600 mb-3">Click "Analyze All" to run AI analysis across all documents. The system identifies risks, red flags, and compliance gaps across Indian regulatory frameworks.</p>
          <p className="text-xs text-slate-500">Coverage: Companies Act 2013, SEBI, FEMA, Income Tax Act, CGST, DPDP Act 2023, Indian labour laws, and more.</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">7. Review Issues &amp; Q&amp;A</h2>
          <p className="text-sm text-slate-600 mb-3">Review flagged issues in the Issues tab. Use the Q&amp;A tab to ask questions about specific documents — the AI answers based solely on document content.</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-bold text-slate-900 mb-3">8. Generate Reports</h2>
          <p className="text-sm text-slate-600 mb-3">Generate professional DOCX reports with your firm's branding. Reports include executive summary, issue analysis, risk scoring, and compliance checklist.</p>
        </div>
      </div>
    </div>
  )
}
