const BASE = '/api'

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...opts, headers: { ...headers, ...((opts?.headers as Record<string,string>) || {}) } })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || 'Request failed')
  }
  return res.json()
}

export interface Deal {
  id: string; deal_name: string; target_company: string; acquirer?: string
  deal_type: string; description?: string; status: string
  document_count: number; issue_count: number; risk_score?: number
  client_id?: string; created_at: string; updated_at: string
}

export interface Document {
  id: string; deal_id: string; filename: string; file_type?: string
  file_size: number; workstream: string; status: string; summary?: string
  extracted_data?: Record<string,unknown>; red_flags?: unknown[]; created_at: string
}

export interface Issue {
  id: string; deal_id: string; document_id?: string; workstream?: string
  title: string; description?: string; severity: string; status: string
  category?: string; reference_text?: string; recommendation?: string
  assignee?: string; created_at: string; updated_at: string
}

export interface QASession {
  question: string; answer: string; citations: { filename: string; excerpt: string; relevance: string }[]
}

export interface Client {
  id: string; name: string; email?: string; phone?: string; company?: string; created_at: string
}

export interface User {
  id: string; email: string; name: string; role: string; is_active: boolean; created_at: string
}

export interface Report { id: string; deal_id: string; status: string; summary?: string; created_at: string }

// Auth
export const login = (email: string, password: string) =>
  request<{ access_token: string; user: User }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

// Deals
export const listDeals = () => request<Deal[]>('/deals')
export const getDeal = (id: string) => request<Deal>(`/deals/${id}`)
export const createDeal = (data: Partial<Deal>) => request<Deal>('/deals', { method: 'POST', body: JSON.stringify(data) })
export const deleteDeal = (id: string) => request<{ok:boolean}>(`/deals/${id}`, { method: 'DELETE' })

// Documents
export const listDocuments = (dealId: string) => request<Document[]>(`/deals/${dealId}/documents`)
export const uploadDocument = async (dealId: string, file: File): Promise<Document> => {
  const token = localStorage.getItem('token')
  const headers: Record<string,string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const form = new FormData(); form.append('file', file)
  const res = await fetch(`${BASE}/deals/${dealId}/documents/upload`, { method: 'POST', headers, body: form })
  if (!res.ok) { const b = await res.json().catch(()=>({})); throw new Error(b.detail||'Upload failed') }
  return res.json()
}

// Analysis
export const analyzeDocument = (dealId: string, docId: string) =>
  request<{document_id:string;summary:string;red_flags_count:number;issues_created:number}>(`/deals/${dealId}/analysis/documents/${docId}`, { method: 'POST' })
export const analyzeAll = (dealId: string) =>
  request<{total_analyzed:number;total_issues:number;risk_score:number}>(`/deals/${dealId}/analysis/all`, { method: 'POST' })

// Issues
export const listIssues = (dealId: string) => request<Issue[]>(`/deals/${dealId}/issues`)
export const updateIssueStatus = (dealId: string, issueId: string, status: string) =>
  request<{ok:boolean}>(`/deals/${dealId}/issues/${issueId}/status`, { method: 'PATCH', body: JSON.stringify({ status }) })

// Q&A
export const askQuestion = (dealId: string, question: string) =>
  request<QASession>(`/deals/${dealId}/qa`, { method: 'POST', body: JSON.stringify({ question }) })

// Reports
export const generateReport = (dealId: string) =>
  request<{report_id:string;status:string;path:string}>(`/deals/${dealId}/reports/generate`, { method: 'POST' })
export const downloadReportUrl = (dealId: string, reportId: string) =>
  `${BASE}/deals/${dealId}/reports/${reportId}/download`

// Clients
export const listClients = () => request<Client[]>('/clients')
export const createClient = (data: Partial<Client>) => request<Client>('/clients', { method: 'POST', body: JSON.stringify(data) })

// Users
export const listUsers = () => request<User[]>('/users')
export const createUser = (data: { email: string; name: string; role: string; password: string }) =>
  request<User>('/users', { method: 'POST', body: JSON.stringify(data) })
