import { Link } from 'react-router-dom'
import { Shield, Scale, FileCheck, Users, BarChart3, Globe } from 'lucide-react'

const features = [
  { icon: Shield, title: 'AI-Powered Risk Detection', desc: 'Automatically flag red flags, compliance gaps, and hidden liabilities across 10+ workstreams.' },
  { icon: Scale, title: 'Indian Regulatory Coverage', desc: 'Companies Act 2013, SEBI, FEMA, Income Tax Act, CGST, DPDP Act 2023, and Indian labour laws.' },
  { icon: FileCheck, title: 'Automated Compliance Checklists', desc: '50+ Indian compliance items covering corporate, tax, regulatory, employment, data protection, and IP.' },
  { icon: Users, title: 'Multi-User Collaboration', desc: 'Invite partners, associates, and reviewers with role-based access control.' },
  { icon: BarChart3, title: 'Risk Scoring & Reports', desc: 'Severity-weighted risk scores with professional DOCX reports branded to your firm.' },
  { icon: Globe, title: 'White-Label Branding', desc: 'Custom brand name, logo, and firm identity across all client-facing outputs.' },
]

const plans = [
  { name: 'Free', price: '0', deals: '1 deal', users: '3 users', docs: '50 documents', features: ['Basic analysis', 'Basic reports', 'Email support'] },
  { name: 'Starter', price: '29', deals: '5 deals', users: '10 users', docs: '200 documents', features: ['Full analysis', 'Q&A', 'DOCX export', 'Email support'] },
  { name: 'Professional', price: '99', deals: '25 deals', users: '50 users', docs: '1,000 documents', features: ['Everything in Starter', 'Priority support', 'Custom branding', 'API access'] },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <span className="text-xl font-bold text-slate-900">M&A Due Diligence AI</span>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm text-slate-600 hover:text-slate-900">Log in</Link>
            <Link to="/register" className="text-sm bg-brand-600 text-white px-4 py-2 rounded-lg hover:bg-brand-700">Get Started</Link>
          </div>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <h1 className="text-5xl font-bold text-slate-900 leading-tight max-w-3xl mx-auto">
          AI-Powered Due Diligence<br />for Indian Law Firms
        </h1>
        <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto">
          Analyze M&A transactions, identify risks, and generate professional reports — 
          all powered by AI that understands Indian regulatory frameworks.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link to="/register" className="bg-brand-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-brand-700">Start Free Trial</Link>
          <a href="#features" className="border border-slate-300 text-slate-700 px-6 py-3 rounded-lg font-medium hover:bg-slate-50">See Features</a>
          <Link to="/getting-started" className="border border-slate-300 text-slate-700 px-6 py-3 rounded-lg font-medium hover:bg-slate-50">Guide</Link>
        </div>
      </section>

      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">Everything your firm needs</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f) => (
            <div key={f.title} className="bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-brand-50 rounded-xl flex items-center justify-center mb-4"><f.icon className="w-6 h-6 text-brand-600" /></div>
              <h3 className="font-semibold text-slate-900 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-4">Pricing</h2>
        <p className="text-center text-slate-600 mb-12">Start free, upgrade as you grow</p>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((p) => (
            <div key={p.name} className={`bg-white border-2 rounded-2xl p-6 ${p.name === 'Starter' ? 'border-brand-500 shadow-lg' : 'border-slate-200'}`}>
              {p.name === 'Starter' && <span className="text-xs font-semibold text-brand-600 bg-brand-50 px-3 py-1 rounded-full">Most Popular</span>}
              <h3 className="text-xl font-bold text-slate-900 mt-2">{p.name}</h3>
              <p className="mt-2"><span className="text-3xl font-bold text-slate-900">${p.price}</span><span className="text-slate-500">/month</span></p>
              <ul className="mt-6 space-y-3 text-sm text-slate-600">
                <li>✓ {p.deals}</li>
                <li>✓ {p.users}</li>
                <li>✓ {p.docs}</li>
                {p.features.map((f) => <li key={f}>✓ {f}</li>)}
              </ul>
              <Link to="/register" className="mt-8 block text-center bg-brand-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-brand-700">Get Started</Link>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
        <div className="flex justify-center gap-6 mb-4">
          <Link to="/privacy" className="hover:text-slate-700">Privacy</Link>
          <Link to="/terms" className="hover:text-slate-700">Terms</Link>
        </div>
        &copy; {new Date().getFullYear()} M&A Due Diligence AI. All rights reserved.
      </footer>
    </div>
  )
}
