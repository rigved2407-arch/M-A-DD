import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listDeals, Deal } from '../lib/api'
import { FileText, AlertTriangle, Activity, PlusCircle } from 'lucide-react'

const statusColors: Record<string, string> = {
  active: 'bg-green-50 text-green-700 border-green-200',
  completed: 'bg-blue-50 text-blue-700 border-blue-200',
  closed: 'bg-slate-100 text-slate-600 border-slate-200',
}

const riskColor = (s?: number) => {
  if (s == null) return ''
  if (s > 50) return 'text-red-600'
  if (s > 25) return 'text-amber-600'
  return 'text-green-600'
}

export default function Dashboard() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listDeals().then(setDeals).catch(console.error).finally(() => setLoading(false))
  }, [])

  const totalDocs = deals.reduce((a, d) => a + (d.document_count || 0), 0)
  const totalIssues = deals.reduce((a, d) => a + (d.issue_count || 0), 0)
  const avgRisk = deals.length ? Math.round(deals.reduce((a, d) => a + (d.risk_score || 0), 0) / deals.length) : 0

  if (loading) return (
    <div className="flex items-center justify-center py-32">
      <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
    </div>
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Deal Rooms</h1>
          <p className="text-sm text-slate-500 mt-1">{deals.length} deal(s) &middot; Indian M&A practice</p>
        </div>
        <Link to="/deals/new"
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-sm font-medium hover:from-brand-700 hover:to-brand-800 transition-all shadow-md shadow-brand-200">
          <PlusCircle className="w-4 h-4" /> New Deal
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Documents', value: totalDocs, icon: FileText, color: 'from-brand-50 to-indigo-50 border-brand-100 text-brand-700' },
          { label: 'Issues', value: totalIssues, icon: AlertTriangle, color: 'from-amber-50 to-yellow-50 border-amber-100 text-amber-700' },
          { label: 'Avg Risk', value: `${avgRisk}%`, icon: Activity, color: 'from-red-50 to-rose-50 border-red-100 text-red-700' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className={`bg-gradient-to-br ${color} rounded-xl p-4 text-center border`}>
            <Icon className="w-5 h-5 mx-auto mb-1" />
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs font-medium mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {deals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {deals.map(deal => (
            <Link key={deal.id} to={`/deals/${deal.id}`}
              className="group bg-white border border-slate-200 rounded-2xl p-5 hover:border-brand-300 hover:shadow-lg transition-all shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-brand-100 to-indigo-100 rounded-xl flex items-center justify-center shadow-inner">
                  <FileText className="w-5 h-5 text-brand-700" />
                </div>
                <span className={`px-2.5 py-0.5 rounded-lg text-xs font-semibold border ${statusColors[deal.status] || statusColors.active}`}>
                  {deal.status}
                </span>
              </div>
              <h2 className="font-bold text-slate-900 group-hover:text-brand-700 transition-colors">{deal.deal_name}</h2>
              <p className="text-sm text-slate-500 mt-1">{deal.target_company}{deal.acquirer ? ` → ${deal.acquirer}` : ''}</p>
              <div className="flex items-center gap-3 mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5" /> {deal.document_count || 0} docs
                </span>
                <span className="flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> {deal.issue_count || 0} issues
                </span>
                {deal.risk_score != null && (
                  <span className={`ml-auto flex items-center gap-1 font-semibold ${riskColor(deal.risk_score)}`}>
                    <Activity className="w-3.5 h-3.5" /> {deal.risk_score}%
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="text-center py-24 text-slate-400">
            <div className="w-16 h-16 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
              <FileText className="w-8 h-8 text-slate-400" />
            </div>
            <p className="text-lg font-semibold text-slate-600 mb-2">No deals yet</p>
            <p className="text-sm mb-6 max-w-md mx-auto leading-relaxed">Create your first M&A deal room to start due diligence. Upload documents, analyze red flags, generate reports — all under Indian regulatory frameworks.</p>
            <Link to="/deals/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl font-medium hover:from-brand-700 hover:to-brand-800 transition-all shadow-md shadow-brand-200">
              <PlusCircle className="w-4 h-4" /> Create a Deal
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
