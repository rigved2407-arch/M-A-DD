import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  getDeal, listDocuments, listIssues, askQuestion,
  analyzeDocument, analyzeAll, generateReport, downloadReportUrl,
  updateIssueStatus, uploadDocument,
  Deal, Document, Issue, QASession, Report,
} from '../lib/api'
import {
  ArrowLeft, FileText, AlertTriangle, MessageSquare, Download,
  Upload, Zap, Plus, CheckCircle, XCircle, Loader2,
} from 'lucide-react'

const workstreams = ['legal','financial','commercial','tax','hr','it','environmental','insurance','regulatory','other']

const severityLabels: Record<string, string> = { high: 'Must Fix', medium: 'Should Fix', low: 'Review', info: 'Monitor' }
const severityColors: Record<string, string> = {
  high: 'bg-red-50 border-red-200', medium: 'bg-amber-50 border-amber-200',
  low: 'bg-blue-50 border-blue-200', info: 'bg-slate-50 border-slate-200',
}
const severityBadge: Record<string, string> = {
  high: 'bg-red-100 text-red-800 border-red-300', medium: 'bg-amber-100 text-amber-800 border-amber-300',
  low: 'bg-blue-100 text-blue-800 border-blue-300', info: 'bg-slate-100 text-slate-700 border-slate-300',
}

type Tab = 'dataroom' | 'issues' | 'qa' | 'report'

export default function DealDetail() {
  const { id } = useParams<{ id: string }>()
  const [deal, setDeal] = useState<Deal | null>(null)
  const [docs, setDocs] = useState<Document[]>([])
  const [issues, setIssues] = useState<Issue[]>([])
  const [qaHist, setQaHist] = useState<QASession[]>([])
  const [report, setReport] = useState<Report | null>(null)
  const [tab, setTab] = useState<Tab>('dataroom')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [question, setQuestion] = useState('')
  const [qaLoading, setQaLoading] = useState(false)
  const [repLoading, setRepLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    try {
      const [d, docList, issList] = await Promise.all([getDeal(id), listDocuments(id), listIssues(id)])
      setDeal(d); setDocs(docList); setIssues(issList)
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }, [id])

  useEffect(() => { load() }, [load])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file || !id) return
    setUploading(true)
    try { await uploadDocument(id, file); await load() } catch (err: any) { alert(err.message) }
    finally { setUploading(false); e.target.value = '' }
  }

  const handleAnalyze = async (docId: string) => {
    if (!id) return; setAnalyzing(true)
    try { await analyzeDocument(id, docId); await load() } catch (err: any) { alert(err.message) }
    finally { setAnalyzing(false) }
  }

  const handleAnalyzeAll = async () => {
    if (!id) return; setAnalyzing(true)
    try { const r = await analyzeAll(id); alert(`Analysis complete: ${r.total_analyzed} docs, ${r.total_issues} issues found`); await load() }
    catch (err: any) { alert(err.message) } finally { setAnalyzing(false) }
  }

  const handleAsk = async () => {
    if (!id || !question.trim()) return; setQaLoading(true)
    try {
      const res = await askQuestion(id, question)
      setQaHist(prev => [res, ...prev]); setQuestion('')
    } catch (err: any) { alert(err.message) } finally { setQaLoading(false) }
  }

  const handleGenerateReport = async () => {
    if (!id) return; setRepLoading(true)
    try { const r = await generateReport(id); setReport({ id: r.report_id, deal_id: id, status: r.status, created_at: new Date().toISOString() }) }
    catch (err: any) { alert(err.message) } finally { setRepLoading(false) }
  }

  const handleIssueStatus = async (issueId: string, status: string) => {
    if (!id) return
    try { await updateIssueStatus(id, issueId, status); await load() } catch (err: any) { alert(err.message) }
  }

  const byWorkstream = (ws: string) => docs.filter(d => (d.workstream || 'other') === ws)
  const statusColor = (s: string) => s === 'analyzed' ? 'bg-green-100 text-green-700' : s === 'classified' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'

  if (loading) return (
    <div className="flex items-center justify-center py-32">
      <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
    </div>
  )
  if (!deal) return <div className="text-center py-24 text-slate-400">Deal not found</div>

  return (
    <div>
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-5 transition-colors group">
        <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" /> All Deals
      </Link>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2.5 mb-2">
              <span className="px-2.5 py-0.5 bg-slate-100 rounded-lg text-xs font-semibold text-slate-600 uppercase tracking-wider">{deal.deal_type}</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                deal.status === 'active' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}>{deal.status}</span>
              {deal.risk_score != null && (
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                  deal.risk_score > 50 ? 'bg-red-50 text-red-700 border-red-200' : deal.risk_score > 25 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-green-50 text-green-700 border-green-200'
                }`}>Risk {deal.risk_score}%</span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-slate-900">{deal.deal_name}</h1>
            <p className="text-slate-500 mt-1">{deal.target_company}{deal.acquirer ? ` → ${deal.acquirer}` : ''}</p>
            {deal.description && <p className="text-sm text-slate-600 mt-3 max-w-2xl">{deal.description}</p>}
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4 mt-6">
          {[
            { label: 'Documents', value: docs.length, color: 'from-brand-50 to-indigo-50 border-brand-100 text-brand-700' },
            { label: 'Analyzed', value: docs.filter(d => d.status === 'analyzed').length, color: 'from-green-50 to-emerald-50 border-green-100 text-green-700' },
            { label: 'Issues', value: issues.length, color: 'from-amber-50 to-yellow-50 border-amber-100 text-amber-700' },
            { label: 'High Risk', value: issues.filter(i => i.severity === 'high').length, color: 'from-red-50 to-rose-50 border-red-100 text-red-700' },
          ].map(({ label, value, color }) => (
            <div key={label} className={`bg-gradient-to-br ${color} rounded-xl p-4 text-center border`}>
              <p className="text-2xl font-bold">{value}</p>
              <p className="text-xs font-medium mt-1">{label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-1 mb-6 border-b border-slate-200">
        {(['dataroom', 'issues', 'qa', 'report'] as Tab[]).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? 'border-brand-600 text-brand-700' : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}>
            {t === 'dataroom' ? 'Data Room' : t === 'issues' ? 'Issues' : t === 'qa' ? 'Q&A' : 'Report'}
          </button>
        ))}
      </div>

      {tab === 'dataroom' && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2"><FileText className="w-5 h-5 text-slate-500" /> Data Room</h2>
            <div className="flex items-center gap-2">
              {docs.some(d => d.status === 'classified') && (
                <button onClick={handleAnalyzeAll} disabled={analyzing}
                  className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-xs font-semibold hover:from-brand-700 hover:to-brand-800 transition-all disabled:opacity-50">
                  {analyzing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                  Analyze All
                </button>
              )}
              <label className="flex items-center gap-1.5 px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-xl text-xs font-semibold hover:bg-slate-50 cursor-pointer transition-all">
                <Upload className="w-3.5 h-3.5" /> {uploading ? 'Uploading...' : 'Upload'}
                <input type="file" className="hidden" accept=".pdf,.docx,.doc,.xlsx,.xls,.csv,.txt,.pptx" onChange={handleUpload} disabled={uploading} />
              </label>
            </div>
          </div>
          <div className="p-6">
            {docs.length > 0 ? (
              <div className="space-y-5">
                {workstreams.filter(ws => byWorkstream(ws).length > 0).map(ws => (
                  <div key={ws}>
                    <div className="flex items-center gap-2 mb-2.5">
                      <span className={`workstream-badge ws-${ws}`}>{ws.toUpperCase()}</span>
                      <span className="text-xs text-slate-400">{byWorkstream(ws).length} doc(s)</span>
                    </div>
                    <div className="space-y-1.5">
                      {byWorkstream(ws).map(doc => (
                        <div key={doc.id} className="flex items-center justify-between bg-slate-50 rounded-xl px-4 py-3 text-sm border border-slate-200">
                          <div className="flex items-center gap-2.5 min-w-0">
                            <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                            <span className="truncate font-medium text-slate-900">{doc.filename}</span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0 ml-2">
                            <span className={`px-2 py-0.5 rounded-lg text-xs font-semibold ${statusColor(doc.status)}`}>{doc.status}</span>
                            {doc.status !== 'analyzed' && (
                              <button onClick={() => handleAnalyze(doc.id)} disabled={analyzing}
                                className="text-xs font-semibold text-brand-600 hover:text-brand-800 px-2 py-1 hover:bg-brand-50 rounded-lg transition-colors">
                                Analyze
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400">
                <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-medium">No documents uploaded yet</p>
                <p className="text-xs mt-1">Upload contracts, financials, and other DD documents above.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'issues' && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-slate-500" /> Issues &amp; Red Flags</h2>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded-lg font-medium">{issues.length} total</span>
          </div>
          <div className="p-6">
            {issues.length > 0 ? (
              <div className="space-y-2">
                {['high', 'medium', 'low', 'info'].filter(s => issues.some(i => i.severity === s)).map(sev => (
                  issues.filter(i => i.severity === sev).map(issue => (
                    <div key={issue.id} className={`flex items-start gap-3 p-4 rounded-xl border ${severityColors[sev] || severityColors.info}`}>
                      <span className={`px-2 py-0.5 rounded-lg text-xs font-semibold shrink-0 border ${severityBadge[sev] || severityBadge.info}`}>
                        {severityLabels[sev] || sev}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-sm text-slate-900">{issue.title}</span>
                          <select value={issue.status} onChange={e => handleIssueStatus(issue.id, e.target.value)}
                            className="text-xs border border-slate-300 rounded-lg px-2 py-1">
                            <option value="open">Open</option>
                            <option value="in_review">In Review</option>
                            <option value="resolved">Resolved</option>
                            <option value="closed">Closed</option>
                          </select>
                        </div>
                        {issue.description && <p className="text-xs text-slate-600 mt-1">{issue.description}</p>}
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          {issue.workstream && <span className={`workstream-badge ws-${issue.workstream} text-[10px]`}>{issue.workstream}</span>}
                          {issue.recommendation && <span className="text-[10px] text-brand-600 font-medium">Rec: {issue.recommendation.slice(0, 100)}</span>}
                        </div>
                      </div>
                    </div>
                  ))
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-medium">No issues found</p>
                <p className="text-xs mt-1">Run document analysis to auto-detect red flags.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'qa' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl shadow-sm">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-slate-500" />
              <h2 className="text-lg font-bold text-slate-900">AI Q&amp;A</h2>
            </div>
            <div className="p-6">
              <div className="flex gap-2 mb-6">
                <input value={question} onChange={e => setQuestion(e.target.value)}
                  placeholder="Ask about the deal documents..." 
                  className="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 transition-shadow"
                  onKeyDown={e => e.key === 'Enter' && handleAsk()} />
                <button onClick={handleAsk} disabled={qaLoading || !question.trim()}
                  className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-sm font-semibold hover:from-brand-700 hover:to-brand-800 transition-all disabled:opacity-50">
                  {qaLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Ask'}
                </button>
              </div>
              {qaHist.length > 0 ? (
                <div className="space-y-4">
                  {qaHist.map((qa, i) => (
                    <div key={i} className="pb-4 border-b border-slate-100 last:border-0">
                      <p className="text-sm font-semibold text-slate-900"><span className="text-brand-600">Q:</span> {qa.question}</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{qa.answer}</p>
                      {qa.citations.length > 0 && (
                        <div className="mt-2 p-3 bg-slate-50 rounded-lg border border-slate-200">
                          <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-1">Sources</p>
                          {qa.citations.slice(0, 3).map((c, j) => (
                            <p key={j} className="text-[10px] text-brand-600 truncate">{c.filename}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 text-center py-8">Ask a question to get AI-powered answers from your documents with citations.</p>
              )}
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm h-fit">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
              <Download className="w-5 h-5 text-slate-500" />
              <h2 className="text-lg font-bold text-slate-900">DD Report</h2>
            </div>
            <div className="p-6 text-center">
              {report ? (
                <div>
                  <div className="w-14 h-14 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
                    <CheckCircle className="w-7 h-7 text-green-600" />
                  </div>
                  <p className="text-sm font-semibold text-slate-900">Report Generated</p>
                  <a href={downloadReportUrl(deal.id, report.id)}
                    className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-xs font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-sm">
                    <Download className="w-4 h-4" /> Download DOCX
                  </a>
                </div>
              ) : (
                <div>
                  <div className="w-14 h-14 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
                    <FileText className="w-7 h-7 text-slate-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-500 mb-4">Generate a comprehensive DD report</p>
                  <button onClick={handleGenerateReport} disabled={repLoading}
                    className="w-full px-4 py-2.5 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-xs font-semibold hover:from-brand-700 hover:to-brand-800 transition-all disabled:opacity-50">
                    {repLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Generate Report'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === 'report' && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8 text-center">
          {report ? (
            <div>
              <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-2">Report Ready</h2>
              <p className="text-sm text-slate-500 mb-6">Your comprehensive due diligence report has been generated.</p>
              <a href={downloadReportUrl(deal.id, report.id)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-md">
                <Download className="w-5 h-5" /> Download DOCX Report
              </a>
            </div>
          ) : (
            <div>
              <div className="w-16 h-16 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
                <FileText className="w-8 h-8 text-slate-400" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-2">Due Diligence Report</h2>
              <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">Generate a comprehensive, structured DD report covering all workstreams with Indian regulatory analysis.</p>
              <button onClick={handleGenerateReport} disabled={repLoading}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-md disabled:opacity-50">
                {repLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                Generate Report
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
