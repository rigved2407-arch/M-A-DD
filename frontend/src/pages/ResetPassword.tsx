import { useState, FormEvent } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { Scale, CheckCircle, AlertCircle } from 'lucide-react'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (password.length < 8) { setError('Password must be at least 8 characters'); return }
    if (password !== confirm) { setError('Passwords do not match'); return }

    setLoading(true)
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      })
      const body = await res.json()
      if (!res.ok) throw new Error(body.detail || 'Reset failed')
      setDone(true)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">Password Reset</h1>
          <p className="text-brand-200 text-sm mb-6">Your password has been reset successfully.</p>
          <Link to="/login"
            className="inline-flex px-6 py-3 bg-white text-brand-700 rounded-xl font-semibold hover:bg-brand-50 transition-colors">
            Sign In
          </Link>
        </div>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <AlertCircle className="w-16 h-16 text-amber-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">Invalid Reset Link</h1>
          <p className="text-brand-200 text-sm mb-6">This reset link is missing or invalid. Request a new one.</p>
          <Link to="/forgot-password"
            className="inline-flex px-6 py-3 bg-white text-brand-700 rounded-xl font-semibold hover:bg-brand-50 transition-colors">
            Request Reset
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Scale className="w-12 h-12 text-white mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-white">Set New Password</h1>
          <p className="text-brand-200 text-sm mt-1">Enter your new password below</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-8 space-y-5">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              <AlertCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">New Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
              className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500"
              placeholder="At least 8 characters" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Confirm Password</label>
            <input type="password" required value={confirm} onChange={e => setConfirm(e.target.value)}
              className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500"
              placeholder="Repeat your password" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-700 text-white rounded-xl text-sm font-semibold hover:from-brand-700 hover:to-brand-800 transition-all shadow-md disabled:opacity-50">
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
