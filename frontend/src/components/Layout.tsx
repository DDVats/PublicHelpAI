import { Outlet, Link, NavLink } from 'react-router-dom';
import { Search, Bookmark, BarChart2, Shield, GitCompare, BookOpen } from 'lucide-react';

const NAV = [
  { to: '/search', icon: Search, label: 'Find Schemes' },
  { to: '/saved', icon: Bookmark, label: 'Saved' },
  { to: '/compare', icon: GitCompare, label: 'Compare' },
  { to: '/ml', icon: BarChart2, label: 'ML & Data' },
  { to: '/privacy', icon: Shield, label: 'Privacy' },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Disclaimer Banner */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center text-xs text-amber-800">
        <strong>Informational tool only.</strong> PublicHelp AI is independent and not affiliated with the Government of India.
        Always verify scheme details at the official source before applying.
      </div>

      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="page-container">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-saffron-500 to-civic-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-white" />
              </div>
              <div>
                <span className="font-bold text-gray-900 text-lg leading-none">PublicHelp AI</span>
                <p className="text-xs text-gray-500 leading-none">Government Scheme Navigator</p>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {NAV.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-civic-50 text-civic-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>

        {/* Mobile nav */}
        <div className="md:hidden border-t border-gray-100 flex overflow-x-auto">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 px-4 py-2 text-xs font-medium whitespace-nowrap ${
                  isActive ? 'text-civic-700 border-b-2 border-civic-600' : 'text-gray-500'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </div>
      </header>

      {/* Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-8 mt-12">
        <div className="page-container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-white font-semibold mb-2">PublicHelp AI</h3>
              <p className="text-sm">An explainable government scheme and benefit navigator. Academic project — not an official government portal.</p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Data</h3>
              <p className="text-sm">Scheme data sourced from the public <a href="https://github.com/Aryan-Pardeshi/gov-myscheme-dataset" className="text-civic-400 hover:underline" target="_blank" rel="noopener noreferrer">gov-myscheme-dataset</a> (2,066 records). Original data from myscheme.gov.in.</p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Disclaimer</h3>
              <p className="text-sm">Eligibility assessments are informational only. No guarantee of benefit receipt. Always apply through official government channels.</p>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-6 pt-4 text-xs text-center">
            PublicHelp AI — AIML Academic Project | Data ingested: 2026-10-16 | 2,066 schemes
          </div>
        </div>
      </footer>
    </div>
  );
}
