import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Scale, CheckCircle, AlertCircle } from 'lucide-react'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      const body = await res.json()
      if (!res.ok) throw new Error(body.detail || 'Request failed')
      setSent(true)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">Check Your Email</h1>
          <p className="text-brand-200 text-sm">If this email is registered, a password reset link has been sent.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Scale className="w-12 h-12 text-white mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-white">Forgot Password</h1>
          <p className="text-brand-200 text-sm mt-1">Enter your email and we'll send you a reset link</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-8 space-y-5">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              <AlertCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
              className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500"
              placeholder="partner@lawfirm.com" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-sm font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-md disabled:opacity-50">
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
          <p className="text-center text-xs text-slate-500">
            <Link to="/login" className="text-brand-600 hover:text-brand-800 font-medium">Back to Sign In</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
