import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Users, Package, MapPin, Bookmark, CheckCircle, AlertCircle, ArrowRight, Loader2, SlidersHorizontal, RefreshCw, FileText, ExternalLink, HelpCircle } from 'lucide-react';
import { getPersonalizedFeed, getPersonas } from '../api';
import type { SchemeCard as SchemeCardType, ComplementaryBundle, PersonaItem, PersonalizedFeedResponse, UserProfile } from '../api';
import SchemeCardComponent from '../components/SchemeCard';
import ProfileForm from '../components/ProfileForm';
import { useProfile } from '../App';

export default function Recommendations() {
  const { profile, setProfile, savedIds } = useProfile();
  const [feed, setFeed] = useState<PersonalizedFeedResponse | null>(null);
  const [personas, setPersonas] = useState<PersonaItem[]>([]);
  const [activePersonaId, setActivePersonaId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [showProfileDrawer, setShowProfileDrawer] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'top' | 'bundles' | 'state' | 'saved'>('top');

  // Load personas on mount
  useEffect(() => {
    getPersonas()
      .then(res => setPersonas(res.data.personas || []))
      .catch(() => {});
  }, []);

  // Fetch personalized feed whenever profile or saved items change
  useEffect(() => {
    setLoading(true);
    setError('');
    getPersonalizedFeed({
      profile: Object.keys(profile).length > 0 ? profile : undefined,
      saved_ids: Array.from(savedIds),
      top_k: 8,
    })
      .then(res => {
        setFeed(res.data);
      })
      .catch(() => {
        setError('Failed to generate personalized recommendations. Ensure backend is running.');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [profile, savedIds]);

  const selectPersona = (p: PersonaItem) => {
    setActivePersonaId(p.persona_id);
    setProfile(p.profile);
  };

  const clearPersona = () => {
    setActivePersonaId(null);
    setProfile({});
  };

  const hasProfile = Object.keys(profile).length > 0;

  return (
    <div className="page-container py-8">
      {/* Header */}
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-civic-100 text-civic-800 rounded-full text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-civic-600" />
              <span>AI Recommender System · Multi-Tier Demographic & Utility Matching</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
              Personalized Recommendations
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Data-backed welfare scheme recommendations and curated civic benefit bundles personalized to your demographics.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowProfileDrawer(prev => !prev)}
              className="btn-secondary text-sm flex items-center gap-2"
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>{showProfileDrawer ? 'Hide Profile' : 'Edit My Profile'}</span>
            </button>
            {hasProfile && (
              <button
                onClick={clearPersona}
                className="px-3 py-2 text-xs text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                title="Reset profile"
              >
                Clear Profile
              </button>
            )}
          </div>
        </div>

        {/* 1-Click Persona Simulator (Presentation & Viva Demo) */}
        <div className="card p-5 mb-8 bg-gradient-to-r from-gray-50 via-civic-50/30 to-amber-50/30 border border-gray-200">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600 flex items-center gap-1.5">
              <Users className="w-4 h-4 text-civic-600" />
              Interactive Citizen Persona Simulator (1-Click Viva Demo)
            </span>
            <span className="text-xs text-gray-500">
              Select a persona to test dynamic real-time recommendation shifts:
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {personas.map(p => {
              const isSelected = activePersonaId === p.persona_id;
              return (
                <button
                  key={p.persona_id}
                  onClick={() => selectPersona(p)}
                  className={`p-3 text-left rounded-xl transition-all border ${
                    isSelected
                      ? 'bg-white border-civic-600 shadow-md ring-2 ring-civic-500/20'
                      : 'bg-white/80 hover:bg-white border-gray-200 hover:border-gray-300 shadow-2xs'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{p.avatar}</span>
                    <span className="font-semibold text-sm text-gray-900 leading-tight">
                      {p.name}
                    </span>
                  </div>
                  <p className="text-xs text-civic-700 font-medium mb-1">
                    {p.tagline}
                  </p>
                  <p className="text-[11px] text-gray-500 line-clamp-2">
                    {p.description}
                  </p>
                </button>
              );
            })}
          </div>

          {feed?.active_profile_summary && (
            <div className="mt-3 pt-3 border-t border-gray-200/80 flex items-center justify-between text-xs text-gray-600 flex-wrap gap-2">
              <span className="flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                Active Profile Context: <strong>{feed.active_profile_summary}</strong>
              </span>
              <span className="text-[11px] bg-white border border-gray-200 px-2 py-0.5 rounded-md text-gray-500">
                Algorithm: {feed.algorithm_info.architecture}
              </span>
            </div>
          )}
        </div>

        {/* Profile Drawer */}
        {showProfileDrawer && (
          <div className="card p-6 mb-8 border-civic-200 bg-white shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-civic-600" />
                Configure Custom Citizen Profile
              </h2>
              <button
                onClick={() => setShowProfileDrawer(false)}
                className="text-xs text-gray-500 hover:text-gray-800"
              >
                Close
              </button>
            </div>
            <ProfileForm />
          </div>
        )}

        {/* Shelf Tabs */}
        <div className="flex border-b border-gray-200 mb-6 gap-2 overflow-x-auto">
          {[
            { id: 'top', label: `Top Matches (${feed?.top_matches?.length || 0})`, icon: Sparkles },
            { id: 'bundles', label: `Welfare Packages (${feed?.bundles?.length || 0})`, icon: Package },
            { id: 'state', label: `State Spotlight (${feed?.state_spotlight?.length || 0})`, icon: MapPin },
            { id: 'saved', label: `Based on Saved (${feed?.similar_to_saved?.length || 0})`, icon: Bookmark },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap ${
                  isActive
                    ? 'border-civic-600 text-civic-700 bg-civic-50/50'
                    : 'border-transparent text-gray-500 hover:text-gray-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-civic-600 mb-2" />
            <p className="text-sm text-gray-500">Computing personalized recommendations and benefit pathways...</p>
          </div>
        )}

        {/* Error state */}
        {!loading && error && (
          <div className="card p-6 text-center text-red-600 my-8">
            <AlertCircle className="w-8 h-8 mx-auto mb-2" />
            <p>{error}</p>
          </div>
        )}

        {/* Tab 1: Top Recommendations */}
        {!loading && activeTab === 'top' && feed && (
          <div>
            <div className="mb-4 flex items-center justify-between text-xs text-gray-500">
              <span>Showing highest-ranking schemes evaluated against your demographic parameters</span>
              <span>Sorted by Multi-Objective Utility Score</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {feed.top_matches.map(scheme => (
                <SchemeCardComponent key={scheme.id} scheme={scheme} />
              ))}
            </div>
            {feed.top_matches.length === 0 && (
              <div className="card p-8 text-center text-gray-500">
                <HelpCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                No schemes found matching the criteria. Try adjusting your demographic profile.
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Curated Welfare Benefit Bundles */}
        {!loading && activeTab === 'bundles' && feed && (
          <div className="space-y-6">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 mb-4">
              <strong>Complementary Benefit Bundles:</strong> Government programs are designed to be complementary.
              Each scheme is independently evaluated for eligibility; qualifying for one does not automatically guarantee eligibility for another.
            </div>

            <div className="grid grid-cols-1 gap-6">
              {feed.bundles.map(bundle => (
                <div key={bundle.bundle_id} className="card p-6 border-l-4 border-l-civic-600">
                  <div className="flex items-start justify-between gap-4 mb-3 flex-wrap">
                    <div>
                      <div className="inline-block px-2.5 py-0.5 bg-civic-100 text-civic-800 rounded text-xs font-semibold mb-1">
                        {bundle.target_persona}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900">{bundle.title}</h3>
                      <p className="text-xs text-gray-600 mt-0.5">{bundle.description}</p>
                    </div>
                  </div>

                  {/* Schemes in this bundle */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                    {bundle.schemes.map(item => {
                      const isEligible = item.eligibility.status === 'potentially_eligible';
                      return (
                        <div key={item.id} className="p-4 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-white transition-colors flex flex-col justify-between">
                          <div>
                            <div className="flex items-center justify-between gap-2 mb-1.5">
                              <span className="text-[11px] font-bold text-civic-700 uppercase tracking-wider bg-civic-100/70 px-2 py-0.5 rounded">
                                {item.benefit_role}
                              </span>
                              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                                isEligible ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {isEligible ? 'Potentially Eligible' : 'Needs Verification'}
                              </span>
                            </div>
                            <Link to={`/schemes/${item.id}`} className="font-semibold text-sm text-gray-900 hover:text-civic-600 line-clamp-1">
                              {item.name}
                            </Link>
                            <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                              {item.rationale}
                            </p>
                          </div>

                          <div className="mt-3 pt-2 border-t border-gray-200 flex items-center justify-between text-xs">
                            <Link to={`/schemes/${item.id}`} className="text-civic-600 hover:underline font-medium">
                              View scheme details →
                            </Link>
                            <a href={item.official_link || item.myscheme_url} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-gray-600 flex items-center gap-1">
                              Source <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: State Spotlight */}
        {!loading && activeTab === 'state' && feed && (
          <div>
            <div className="mb-4 text-xs text-gray-500">
              Schemes specifically enacted by state ministries for local residents.
            </div>
            {feed.state_spotlight.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {feed.state_spotlight.map(scheme => (
                  <SchemeCardComponent key={scheme.id} scheme={scheme} />
                ))}
              </div>
            ) : (
              <div className="card p-8 text-center text-gray-500">
                <MapPin className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p>No state selected in profile.</p>
                <p className="text-xs mt-1">Select a state above to view local state government welfare schemes.</p>
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Similar to Saved */}
        {!loading && activeTab === 'saved' && feed && (
          <div>
            <div className="mb-4 text-xs text-gray-500">
              Content-Based nearest neighbors retrieved using 384-dimensional dense semantic embeddings.
            </div>
            {feed.similar_to_saved.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {feed.similar_to_saved.map(scheme => (
                  <SchemeCardComponent key={scheme.id} scheme={scheme} />
                ))}
              </div>
            ) : (
              <div className="card p-8 text-center text-gray-500">
                <Bookmark className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p>No saved schemes yet.</p>
                <p className="text-xs mt-1">Bookmark any scheme to see related content-based recommendations here.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
