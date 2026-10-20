import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ArrowRight, Users, Building2, Globe, Cpu, Shield } from 'lucide-react';
import { getStats } from '../api';
import type { Stats } from '../api';

export default function Landing() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    getStats().then(r => setStats(r.data)).catch(() => {});
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-civic-700 via-civic-600 to-civic-800 text-white py-20 px-4">
        <div className="page-container text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur rounded-full px-4 py-1.5 text-sm mb-6 border border-white/20">
            <Cpu className="w-4 h-4 text-emerald-300" />
            <span>Explainable 2-Stage Neural Retrieval · Bi-Encoder & Cross-Attention Architecture</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
            Find the Government Schemes<br />
            <span className="text-saffron-300">You're Eligible For</span>
          </h1>
          <p className="text-xl text-civic-100 mb-8 max-w-2xl mx-auto">
            PublicHelp AI uses explainable hybrid AI to match your profile with
            over {stats ? stats.total_schemes.toLocaleString() : '2,000+'} Indian government schemes — with transparent eligibility explanations.
          </p>

          <form onSubmit={handleSearch} className="flex gap-2 max-w-xl mx-auto mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                className="w-full pl-10 pr-4 py-3 rounded-xl text-gray-900 text-base focus:outline-none focus:ring-2 focus:ring-saffron-400"
                placeholder="e.g. scholarship for SC students, farmer loan, women entrepreneur..."
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
            </div>
            <button type="submit" className="px-5 py-3 bg-saffron-500 hover:bg-saffron-600 text-white font-medium rounded-xl transition-colors flex items-center gap-2">
              Search <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <Link
              to="/recommendations"
              className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-saffron-500 to-amber-500 hover:from-saffron-600 hover:to-amber-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2 text-base"
            >
              <span>Explore Personalized Recommendations</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/search"
              className="w-full sm:w-auto px-5 py-3.5 bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl border border-white/30 backdrop-blur transition-all flex items-center justify-center gap-2 text-sm"
            >
              <Search className="w-4 h-4" />
              <span>Keyword Search & Browse</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      {stats && (
        <section className="bg-white border-b border-gray-200 py-6">
          <div className="page-container">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <StatItem icon={Globe} value={stats.total_schemes.toLocaleString()} label="Total Schemes" />
              <StatItem icon={Building2} value={stats.central_schemes.toLocaleString()} label="Central Govt Schemes" />
              <StatItem icon={Users} value={stats.state_schemes.toLocaleString()} label="State / UT Schemes" />
              <StatItem icon={Globe} value={stats.total_states_uts.toLocaleString()} label="States & Ministries" />
            </div>
          </div>
        </section>
      )}

      {/* How it works */}
      <section className="py-16 px-4">
        <div className="page-container max-w-5xl mx-auto">
          <h2 className="section-title text-center mb-3">How PublicHelp AI Works</h2>
          <p className="text-center text-gray-500 mb-12 max-w-2xl mx-auto">
            A three-layer hybrid system — structured eligibility rules, semantic search, and transparent ranking.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: '01',
                title: 'Set Your Profile',
                desc: 'Enter optional attributes — state, age, income, category. No Aadhaar or bank details required. Stored only in your browser.',
                color: 'bg-saffron-50 border-saffron-200',
                num: 'text-saffron-600',
              },
              {
                step: '02',
                title: 'Describe What You Need',
                desc: 'Type a plain-English query. Our hybrid engine combines TF-IDF keyword matching with semantic sentence embeddings.',
                color: 'bg-civic-50 border-civic-200',
                num: 'text-civic-600',
              },
              {
                step: '03',
                title: 'Get Explained Results',
                desc: 'Each result shows an eligibility assessment (Eligible / Needs Info / Not Eligible) with the specific rule that produced it.',
                color: 'bg-blue-50 border-blue-200',
                num: 'text-blue-600',
              },
            ].map(s => (
              <div key={s.step} className={`rounded-xl border p-6 ${s.color}`}>
                <div className={`text-3xl font-bold mb-3 ${s.num}`}>{s.step}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{s.title}</h3>
                <p className="text-sm text-gray-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Limitations */}
      <section className="py-12 px-4 bg-amber-50 border-y border-amber-200">
        <div className="page-container max-w-4xl mx-auto">
          <div className="flex items-start gap-4">
            <Shield className="w-8 h-8 text-amber-600 shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-amber-900 mb-3">Important Limitations</h2>
              <ul className="space-y-1.5 text-sm text-amber-800 list-disc list-inside">
                <li>This is an <strong>academic prototype</strong>, not an official government service.</li>
                <li>Eligibility assessments are <strong>informational only</strong> — not a legal determination or guarantee of benefit receipt.</li>
                <li>Scheme data is sourced from a public dataset (ingested 2026-10-16) and may not reflect the latest official updates.</li>
                <li>No individual scheme has been manually verified against its official page; always check the official link before applying.</li>
                <li>Eligibility criteria are parsed automatically from free text — extraction may contain errors.</li>
                <li>No personal data is sent to any external server. Your profile lives only in your browser session.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 text-center">
        <h2 className="section-title mb-4">Ready to explore?</h2>
        <p className="text-gray-500 mb-8">Set your profile and search for schemes relevant to you.</p>
        <Link to="/search" className="btn-primary text-base px-8 py-3">
          <Search className="w-5 h-5" />
          Search Schemes
        </Link>
      </section>
    </div>
  );
}

function StatItem({ icon: Icon, value, label }: { icon: React.ElementType; value: string; label: string }) {
  return (
    <div>
      <div className="flex justify-center mb-2">
        <Icon className="w-6 h-6 text-civic-600" />
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}
