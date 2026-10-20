import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, SlidersHorizontal, Loader2, AlertCircle, X, MessageSquare, ArrowRight, ExternalLink, Sparkles } from 'lucide-react';
import { recommend, askQuestion, getFilters } from '../api';
import type { SchemeCard as SchemeCardType, RecommendResponse, QAAnswer } from '../api';
import SchemeCard from '../components/SchemeCard';
import ProfileForm from '../components/ProfileForm';
import { useProfile } from '../App';

const EXAMPLE_QA_PROMPTS = [
  "What documents are needed for PM Awas Yojana?",
  "How to apply for Pragati scholarship for girls?",
  "What is the income ceiling for OBC Post-Matric scholarship?",
  "Who is eligible for Ayushman Bharat PM-JAY?",
];

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { profile } = useProfile();

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [inputVal, setInputVal] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState<SchemeCardType[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelUsed, setModelUsed] = useState('');
  const [compareIds, setCompareIds] = useState<Set<number>>(new Set());

  // Filters
  const [filters, setFilters] = useState<{ state?: string; level?: string; category?: string }>({});
  const [availableStates, setAvailableStates] = useState<string[]>([]);
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // QA mode
  const [qaMode, setQaMode] = useState(false);
  const [qaAnswers, setQaAnswers] = useState<QAAnswer[]>([]);
  const [qaNote, setQaNote] = useState('');

  const PAGE_SIZE = 10;
  const lastSearchRef = useRef<string>('');

  useEffect(() => {
    getFilters().then(r => {
      setAvailableStates(r.data.states);
      setAvailableCategories(r.data.categories.slice(0, 50));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q !== null && q !== undefined) {
      setQuery(q);
      setInputVal(q);
    }
  }, [searchParams]);

  const doSearch = useCallback(async (q: string, pg = 1, isQa = qaMode) => {
    setLoading(true);
    setError('');
    setPage(pg);
    try {
      if (isQa) {
        if (!q.trim()) {
          setLoading(false);
          setQaAnswers([]);
          return;
        }
        const r = await askQuestion(q.trim());
        setQaAnswers(r.data.answers || []);
        setQaNote(r.data.note || '');
        setResults([]);
        setTotal(0);
      } else {
        const r = await recommend({
          query: q,
          profile: Object.keys(profile).length > 0 ? profile : undefined,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          top_k: PAGE_SIZE,
          page: pg,
        });
        const data: RecommendResponse = r.data;
        if (pg === 1) setResults(data.results);
        else setResults(prev => [...prev, ...data.results]);
        setTotal(data.total);
        setModelUsed(data.model_used);
        setQaAnswers([]);
      }
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Search failed. Please verify the backend connection.');
    } finally {
      setLoading(false);
    }
  }, [profile, filters, qaMode]);

  // Auto-search for scheme recommendations whenever query OR profile OR filters change
  useEffect(() => {
    if (qaMode) return;
    const profileKey = JSON.stringify(profile);
    const filterKey = JSON.stringify(filters);
    const searchKey = `${query}||${profileKey}||${filterKey}||search`;
    if (searchKey === lastSearchRef.current) return;
    lastSearchRef.current = searchKey;

    const timer = setTimeout(() => {
      doSearch(query, 1, false);
    }, query ? 0 : 100);

    return () => clearTimeout(timer);
  }, [query, profile, filters, qaMode, doSearch]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = inputVal.trim();
    setSearchParams(trimmed ? { q: trimmed } : {});
    setQuery(trimmed);
    lastSearchRef.current = `${trimmed}||${JSON.stringify(profile)}||${JSON.stringify(filters)}||${qaMode ? 'qa' : 'search'}`;
    doSearch(trimmed, 1, qaMode);
  };

  const handleSwitchToSearch = () => {
    setQaMode(false);
    setQaAnswers([]);
    lastSearchRef.current = '';
    doSearch(inputVal.trim(), 1, false);
  };

  const handleSwitchToQa = () => {
    setQaMode(true);
    setResults([]);
    lastSearchRef.current = '';
    if (inputVal.trim()) {
      doSearch(inputVal.trim(), 1, true);
    }
  };

  const handleSelectPrompt = (prompt: string) => {
    setInputVal(prompt);
    setQuery(prompt);
    setSearchParams({ q: prompt });
    lastSearchRef.current = `${prompt}||${JSON.stringify(profile)}||${JSON.stringify(filters)}||qa`;
    doSearch(prompt, 1, true);
  };

  const toggleCompare = (id: number) => {
    setCompareIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else if (next.size < 5) next.add(id);
      return next;
    });
  };

  const hasMore = results.length < total;
  const emptyQueryMode = !query.trim();

  return (
    <div className="page-container py-8">
      <div className="max-w-6xl mx-auto">
        {/* Profile form */}
        <div className="mb-6">
          <ProfileForm />
        </div>

        {/* Mode Selector Segmented Tabs */}
        <div className="flex items-center gap-2 mb-4 bg-gray-100 p-1.5 rounded-2xl border border-gray-200">
          <button
            type="button"
            onClick={handleSwitchToSearch}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium text-sm transition-all ${
              !qaMode
                ? 'bg-white text-civic-800 shadow-sm font-semibold'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Scheme Recommendations</span>
          </button>
          <button
            type="button"
            onClick={handleSwitchToQa}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium text-sm transition-all ${
              qaMode
                ? 'bg-white text-blue-700 shadow-sm font-semibold'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Grounded Q&A (Extractive)</span>
          </button>
        </div>

        {/* Mode explanation subtitle */}
        <div className="mb-4 px-1 flex items-center justify-between text-xs text-gray-500">
          <span>
            {qaMode
              ? '💬 Grounded QA: quotes verified scheme descriptions and official links (no hallucinations).'
              : '🔍 Hybrid Search: combines semantic sentence embeddings, TF-IDF, and deterministic eligibility rules.'}
          </span>
          {!qaMode && (
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-2.5 py-1 border rounded-lg transition-colors ${
                showFilters
                  ? 'border-civic-400 text-civic-700 bg-civic-50 font-medium'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters</span>
              {Object.values(filters).filter(Boolean).length > 0 && (
                <span className="bg-civic-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
                  {Object.values(filters).filter(Boolean).length}
                </span>
              )}
            </button>
          )}
        </div>

        {/* Search bar */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="flex gap-2">
            <div className="relative flex-1">
              {qaMode
                ? <MessageSquare className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-blue-500" />
                : <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />}
              <input
                type="text"
                className="w-full pl-11 pr-4 py-3.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-civic-500 focus:border-transparent shadow-sm"
                placeholder={qaMode
                  ? 'Ask a question, e.g. What documents are needed for PM Awas Yojana?'
                  : 'Search schemes, e.g. scholarship for girls, farmer crop insurance, housing...'}
                value={inputVal}
                onChange={e => setInputVal(e.target.value)}
              />
            </div>
            <button type="submit" className={`px-6 py-3.5 rounded-xl font-medium text-sm text-white shadow-sm transition-colors ${
              qaMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-civic-600 hover:bg-civic-700'
            }`}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (qaMode ? 'Ask' : 'Search')}
            </button>
          </div>
        </form>

        {/* Filter panel */}
        {showFilters && !qaMode && (
          <div className="card p-4 mb-6 grid grid-cols-1 sm:grid-cols-3 gap-3 bg-gray-50 border-gray-200">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">State / UT</label>
              <select
                className="input-field"
                value={filters.state || ''}
                onChange={e => setFilters(f => ({ ...f, state: e.target.value || undefined }))}
              >
                <option value="">All states</option>
                {availableStates.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Level</label>
              <select
                className="input-field"
                value={filters.level || ''}
                onChange={e => setFilters(f => ({ ...f, level: e.target.value || undefined }))}
              >
                <option value="">All levels</option>
                <option value="Central Government">Central Government</option>
                <option value="State / UT Government">State / UT Government</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Category</label>
              <select
                className="input-field"
                value={filters.category || ''}
                onChange={e => setFilters(f => ({ ...f, category: e.target.value || undefined }))}
              >
                <option value="">All categories</option>
                {availableCategories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            {Object.values(filters).filter(Boolean).length > 0 && (
              <div className="sm:col-span-3 flex justify-end">
                <button onClick={() => setFilters({})} className="text-xs text-gray-500 hover:text-red-600 flex items-center gap-1 font-medium">
                  <X className="w-3.5 h-3.5" /> Clear active filters
                </button>
              </div>
            )}
          </div>
        )}

        {/* Error notification */}
        {error && (
          <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Scheme search model info */}
        {modelUsed && !qaMode && results.length > 0 && (
          <div className="flex items-center justify-between text-xs text-gray-500 mb-3 px-1">
            <span>
              {emptyQueryMode
                ? `Showing schemes personalized for your profile · ${total} eligible schemes found`
                : `Ranked by: ${modelUsed} · ${total} schemes matched`}
            </span>
          </div>
        )}

        {/* Loading spinner for initial load */}
        {loading && results.length === 0 && qaAnswers.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500">
            <Loader2 className="w-8 h-8 animate-spin text-civic-600 mb-3" />
            <span className="text-sm font-medium">
              {qaMode ? 'Searching verbatim official scheme texts…' : 'Retrieving and evaluating scheme eligibility…'}
            </span>
          </div>
        )}

        {/* Compare tray */}
        {compareIds.size > 0 && (
          <div className="flex items-center gap-3 bg-civic-50 border border-civic-200 rounded-xl p-3 mb-4 shadow-sm">
            <span className="text-sm font-medium text-civic-800">{compareIds.size} scheme(s) selected for side-by-side comparison</span>
            <a href={`/compare?ids=${[...compareIds].join(',')}`} className="btn-primary text-xs py-1.5 px-3">Compare Now</a>
            <button onClick={() => setCompareIds(new Set())} className="ml-auto text-xs text-gray-500 hover:text-red-600">Clear</button>
          </div>
        )}

        {/* QA Results Section */}
        {qaMode && qaAnswers.length > 0 && (
          <div className="space-y-4 mb-6">
            {qaNote && (
              <p className="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-xl p-3 leading-relaxed">
                ℹ️ {qaNote}
              </p>
            )}
            {qaAnswers.map((ans, i) => (
              <div key={i} className="card p-6 border-l-4 border-l-blue-600 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded mr-2">
                      Official Record #{ans.scheme_id}
                    </span>
                    <h3 className="text-lg font-bold text-gray-900 inline">
                      <Link to={`/schemes/${ans.scheme_id}`} className="hover:text-blue-600 hover:underline">
                        {ans.scheme_name}
                      </Link>
                    </h3>
                  </div>
                  <span className="text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full font-medium shrink-0">
                    Confidence: {(ans.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
                <blockquote className="border-l-2 border-blue-300 pl-4 py-1 text-sm text-gray-800 italic mb-4 bg-blue-50/50 rounded-r-lg">
                  "{ans.snippet}"
                </blockquote>
                <div className="flex flex-wrap items-center gap-3 text-xs pt-2 border-t border-gray-100">
                  <Link
                    to={`/schemes/${ans.scheme_id}`}
                    className="inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800"
                  >
                    View Scheme Details <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                  <span className="text-gray-300">•</span>
                  <a
                    href={ans.official_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-gray-600 hover:text-gray-900 hover:underline"
                  >
                    Official Portal <ExternalLink className="w-3 h-3" />
                  </a>
                  {ans.myscheme_url && (
                    <>
                      <span className="text-gray-300">•</span>
                      <a
                        href={ans.myscheme_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 hover:underline"
                      >
                        MyScheme Page <ExternalLink className="w-3 h-3" />
                      </a>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* QA Empty Prompt Helper State */}
        {qaMode && !loading && qaAnswers.length === 0 && (
          <div className="card p-8 text-center my-6 border-dashed border-2 border-gray-200">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-blue-400 opacity-60" />
            <h3 className="text-base font-semibold text-gray-800 mb-1">Grounded Extractive Question Answering</h3>
            <p className="text-xs text-gray-500 max-w-md mx-auto mb-6">
              Ask natural language questions about scheme criteria, required documents, or application procedures. Citations are extracted verbatim from official records.
            </p>
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">Try an example question:</p>
            <div className="flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
              {EXAMPLE_QA_PROMPTS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectPrompt(p)}
                  className="text-xs bg-white border border-gray-200 text-gray-700 hover:border-blue-400 hover:text-blue-700 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1 shadow-2xs"
                >
                  <Sparkles className="w-3 h-3 text-blue-500" />
                  <span>{p}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Scheme Search Results Section */}
        {!qaMode && results.length > 0 && (
          <div className="space-y-4">
            {results.map(scheme => (
              <SchemeCard
                key={scheme.id}
                scheme={scheme}
                compareIds={compareIds}
                onToggleCompare={toggleCompare}
              />
            ))}
            {hasMore && (
              <div className="text-center pt-4">
                <button
                  onClick={() => doSearch(query, page + 1, false)}
                  disabled={loading}
                  className="btn-secondary px-6 py-2.5"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : `Load more (${total - results.length} remaining)`}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Scheme Search No Results State */}
        {!loading && !error && results.length === 0 && !qaMode && (
          <div className="text-center py-16 text-gray-400 card border-dashed">
            <Search className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium text-gray-700">
              {query ? `No schemes found for "${query}"` : 'No matching schemes for your selected profile filters'}
            </p>
            <p className="text-sm mt-1 text-gray-500">
              Try broader keywords (e.g., "scholarship", "farmer", "pension") or clear demographic restrictions.
            </p>
            {Object.values(filters).filter(Boolean).length > 0 && (
              <button
                onClick={() => setFilters({})}
                className="mt-4 text-xs btn-outline px-4 py-2"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
