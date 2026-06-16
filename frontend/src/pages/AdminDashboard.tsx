import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { Users, CreditCard, Shield } from 'lucide-react'

interface OrgUser { id: string; email: string; name: string; role: string; is_active: boolean; last_login_at: string | null }
interface Subscription { plan: string; limits: Record<string, any>; usage: Record<string, any> }

export default function AdminDashboard() {
  const [tab, setTab] = useState<'users' | 'subscription'>('users')
  const [users, setUsers] = useState<OrgUser[]>([])
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [newUser, setNewUser] = useState({ email: '', name: '', role: 'associate' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api<any>('/admin/users').then(setUsers).catch(() => {})
    api<any>('/subscription/current').then(setSubscription).catch(() => {})
  }, [])

  const inviteUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const u = await api<any>('/admin/users', {
        method: 'POST',
        body: JSON.stringify({ ...newUser, org: '' }),
        headers: { 'Content-Type': 'application/json' },
      })
      setUsers([...users, u])
      setNewUser({ email: '', name: '', role: 'associate' })
      setMsg('User invited successfully')
    } catch (err: any) {
      setMsg(err.message || 'Failed to invite user')
    }
  }

  const removeUser = async (id: string) => {
    if (!confirm('Remove this user?')) return
    await api(`/admin/users/${id}`, { method: 'DELETE' })
    setUsers(users.filter((u) => u.id !== id))
  }

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Admin Settings</h1>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('users')} className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${tab === 'users' ? 'bg-brand-600 text-white' : 'bg-white border text-slate-600'}`}><Users className="w-4 h-4" /> Team</button>
        <button onClick={() => setTab('subscription')} className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${tab === 'subscription' ? 'bg-brand-600 text-white' : 'bg-white border text-slate-600'}`}><CreditCard className="w-4 h-4" /> Subscription</button>
      </div>

      {tab === 'users' && (
        <div>
          <form onSubmit={inviteUser} className="bg-white border border-slate-200 rounded-2xl p-6 mb-6">
            <h2 className="font-semibold text-slate-900 mb-4">Invite Team Member</h2>
            <div className="grid sm:grid-cols-4 gap-3">
              <input placeholder="Name" value={newUser.name} onChange={(e) => setNewUser({ ...newUser, name: e.target.value })} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" required />
              <input placeholder="Email" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} className="border border-slate-300 rounded-lg px-3 py-2 text-sm" required />
              <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })} className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="associate">Associate</option>
                <option value="partner">Partner</option>
                <option value="reviewer">Reviewer</option>
                <option value="admin">Admin</option>
              </select>
              <button type="submit" className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700">Invite</button>
            </div>
            {msg && <p className="text-sm text-green-600 mt-2">{msg}</p>}
          </form>

          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-500">
                <tr><th className="px-4 py-3 font-medium">Name</th><th className="px-4 py-3 font-medium">Email</th><th className="px-4 py-3 font-medium">Role</th><th className="px-4 py-3 font-medium">Status</th><th className="px-4 py-3 font-medium"></th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">{u.name}</td>
                    <td className="px-4 py-3 text-slate-600">{u.email}</td>
                    <td className="px-4 py-3"><span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs font-medium">{u.role}</span></td>
                    <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td className="px-4 py-3"><button onClick={() => removeUser(u.id)} className="text-red-500 hover:text-red-700 text-xs font-medium">Remove</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'subscription' && subscription && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center gap-2"><Shield className="w-5 h-5 text-brand-600" /> Current Plan: <span className="uppercase text-brand-600 font-bold">{subscription.plan}</span></h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {Object.entries(subscription.usage).map(([key, val]) => {
              const limit = subscription.limits[key] ?? '-'
              const displayLimit = limit === -1 ? 'Unlimited' : limit
              return (
                <div key={key} className="border border-slate-200 rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase mb-1">{key.replace('_', ' ')}</p>
                  <p className="text-lg font-bold text-slate-900">{String(val)} <span className="text-sm font-normal text-slate-400">/ {displayLimit}</span></p>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
