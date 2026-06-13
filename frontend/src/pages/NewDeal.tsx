import { useState, FormEvent, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { createDeal, listClients, Client } from '../lib/api'
import { ArrowLeft } from 'lucide-react'

export default function NewDeal() {
  const navigate = useNavigate()
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    deal_name: '', target_company: '', acquirer: '',
    deal_type: 'M&A', description: '', client_id: '',
  })

  useEffect(() => { listClients().then(setClients).catch(() => {}) }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!form.deal_name || !form.target_company) return
    setLoading(true)
    try {
      const deal = await createDeal({
        ...form,
        client_id: form.client_id || undefined,
      })
      navigate(`/deals/${deal.id}`)
    } catch (err: any) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-6 transition-colors group">
        <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" /> Back to Deals
      </Link>
      <h1 className="text-2xl font-bold text-slate-900 mb-6">New Deal Room</h1>
      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-5">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Deal Name <span className="text-red-500">*</span></label>
          <input value={form.deal_name} onChange={e => setForm({...form, deal_name: e.target.value})} required
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow"
            placeholder="e.g. Acme Corp Acquisition" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Target Company <span className="text-red-500">*</span></label>
          <input value={form.target_company} onChange={e => setForm({...form, target_company: e.target.value})} required
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500" placeholder="e.g. Acme Corp Pvt Ltd" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Acquirer</label>
          <input value={form.acquirer} onChange={e => setForm({...form, acquirer: e.target.value})}
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500" placeholder="e.g. MegaCorp Inc" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Client</label>
          <select value={form.client_id} onChange={e => setForm({...form, client_id: e.target.value})}
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500">
            <option value="">No client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.name}{c.company ? ` — ${c.company}` : ''}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Deal Type</label>
          <select value={form.deal_type} onChange={e => setForm({...form, deal_type: e.target.value})}
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500">
            <option value="M&A">M&amp;A</option>
            <option value="JV">Joint Venture</option>
            <option value="Investment">Investment</option>
            <option value="IPO">IPO Readiness</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1.5">Description</label>
          <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3}
            className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500"
            placeholder="Brief description of the deal..." />
        </div>
        <button type="submit" disabled={loading}
          className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-sm font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-md shadow-brand-200 disabled:opacity-50">
          {loading ? 'Creating...' : 'Create Deal Room'}
        </button>
      </form>
    </div>
  )
}
