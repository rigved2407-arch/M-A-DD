import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Scale, FolderOpen, PlusCircle, Shield, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'

const nav = [
  { label: 'Deals', path: '/', icon: FolderOpen },
  { label: 'New Deal', path: '/deals/new', icon: PlusCircle },
  { label: 'Privacy', path: '/privacy', icon: Shield },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const user = localStorage.getItem('userName')
  const token = localStorage.getItem('token')

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    localStorage.removeItem('userRole')
    navigate('/login')
  }

  if (!token) return <>{children}</>

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <nav className="bg-gradient-to-r from-brand-700 to-brand-900 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-lg font-bold text-white tracking-tight">
            <Scale className="w-5 h-5" /> M&amp;A Due Diligence AI
          </Link>
          <div className="hidden md:flex items-center gap-1 text-sm">
            {nav.map(({ label, path, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1.5 ${
                  pathname === path ? 'bg-white/15 text-white' : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                <Icon className="w-3.5 h-3.5" /> {label}
              </Link>
            ))}
            {user && (
              <span className="ml-3 pl-3 border-l border-white/20 text-white/70 text-xs">{user}</span>
            )}
            <button onClick={handleLogout} className="ml-1 p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
          <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden text-white p-1">
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
        {mobileOpen && (
          <div className="md:hidden px-4 pb-3 space-y-1">
            {nav.map(({ label, path, icon: Icon }) => (
              <Link key={path} to={path} onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  pathname === path ? 'bg-white/15 text-white' : 'text-white/80 hover:bg-white/10'
                }`}>
                <Icon className="w-4 h-4" /> {label}
              </Link>
            ))}
            {user && <div className="text-white/50 text-xs px-3 pt-2 border-t border-white/10 mt-2">{user}</div>}
            <button onClick={handleLogout} className="flex items-center gap-2 px-3 py-2 text-sm text-white/60 hover:text-white w-full">Logout</button>
          </div>
        )}
      </nav>
      <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">{children}</main>
      <footer className="border-t border-slate-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-xs text-slate-400">
          M&amp;A Due Diligence AI &mdash; Built for Indian M&A practice
        </div>
      </footer>
    </div>
  )
}
