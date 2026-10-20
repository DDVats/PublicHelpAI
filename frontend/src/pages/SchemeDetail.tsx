import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ExternalLink, Bookmark, BookmarkCheck, ArrowLeft, CheckCircle, AlertCircle, FileText, ClipboardList, HelpCircle, Building2, MapPin, Loader2 } from 'lucide-react';
import { getSchemeById } from '../api';
import type { SchemeDetail } from '../api';
import EligibilityBadge from '../components/EligibilityBadge';
import { useProfile } from '../App';
import { assess_eligibility_client } from '../utils/eligibilityClient';

export default function SchemeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [scheme, setScheme] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { savedIds, toggleSaved, profile } = useProfile();

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getSchemeById(parseInt(id))
      .then(r => setScheme(r.data))
      .catch(() => setError('Scheme not found.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="w-8 h-8 animate-spin text-civic-600" />
    </div>
  );

  if (error || !scheme) return (
    <div className="page-container py-12 text-center text-red-600">
      <AlertCircle className="w-8 h-8 mx-auto mb-2" />
      {error || 'Scheme not found'}
      <div className="mt-4"><Link to="/search" className="btn-secondary text-sm">← Back to search</Link></div>
    </div>
  );

  const isSaved = savedIds.has(scheme.id);
  const eligibility = (scheme as unknown as { eligibility?: Parameters<typeof EligibilityBadge>[0]['eligibility'] }).eligibility
    || assess_eligibility_client((scheme as unknown) as Record<string, unknown>, profile);
  const cats = scheme.categories_list || [];

  return (
    <div className="page-container py-8">
      <div className="max-w-4xl mx-auto">
        {/* Breadcrumb */}
        <Link to="/search" className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to search
        </Link>

        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{scheme.name}</h1>
              <div className="flex flex-wrap gap-3 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {scheme.level}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {scheme.state_ministry}
                </span>
                {scheme.application_mode && (
                  <span className="bg-gray-100 px-2 py-0.5 rounded-full text-xs">
                    {scheme.application_mode}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => toggleSaved(scheme.id)}
              className={`p-2.5 rounded-xl transition-colors shrink-0 ${isSaved ? 'bg-saffron-50 text-saffron-600 border border-saffron-200' : 'bg-gray-50 text-gray-400 border border-gray-200 hover:border-saffron-300'}`}
            >
              {isSaved ? <BookmarkCheck className="w-5 h-5" /> : <Bookmark className="w-5 h-5" />}
            </button>
          </div>

          {cats.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {cats.map(c => (
                <span key={c} className="text-xs px-2.5 py-1 bg-civic-50 text-civic-700 rounded-full border border-civic-200">{c}</span>
              ))}
            </div>
          )}

          <p className="text-gray-700 leading-relaxed">{scheme.description}</p>
        </div>

        {/* Eligibility */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-civic-600" /> Eligibility Assessment
          </h2>
          {eligibility ? (
            <EligibilityBadge eligibility={eligibility} />
          ) : (
            <p className="text-sm text-gray-500">Set your profile to see eligibility assessment.</p>
          )}

          <div className="mt-4 border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-700 mb-2">Full eligibility criteria:</p>
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{scheme.eligibility_text || scheme.eligibility_general || 'Not available'}</p>
            {scheme.exclusions_text && (
              <div className="mt-3 p-3 bg-red-50 rounded-lg border border-red-100">
                <p className="text-xs font-medium text-red-700 mb-1">Exclusions / Who is NOT eligible:</p>
                <p className="text-sm text-red-700">{scheme.exclusions_text}</p>
              </div>
            )}
          </div>
        </div>

        {/* Benefits */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-saffron-500" /> Benefits
          </h2>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{scheme.benefits}</p>
        </div>

        {/* Documents */}
        {scheme.documents_required && (
          <div className="card p-6 mb-6">
            <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-500" /> Documents Required
            </h2>
            {scheme.required_documents && scheme.required_documents.length > 0 && (
              <div className="mb-4 p-4 bg-amber-50/70 border border-amber-200 rounded-xl">
                <p className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-2">Standard Document Checklist:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {scheme.required_documents.map(d => (
                    <div key={d} className="flex items-center gap-2 text-xs font-semibold text-amber-900 bg-white px-3 py-2 rounded-lg border border-amber-200 shadow-2xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{scheme.documents_required}</p>
          </div>
        )}

        {/* Application Process */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-gray-500" /> How to Apply
          </h2>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{scheme.application_process}</p>
        </div>

        {/* FAQs */}
        {scheme.faqs && (
          <div className="card p-6 mb-6">
            <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-gray-500" /> Frequently Asked Questions
            </h2>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{scheme.faqs}</p>
          </div>
        )}

        {/* Source + metadata */}
        <div className="card p-6 mb-6 bg-gray-50">
          <h2 className="font-semibold text-gray-900 mb-4">Source Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-xs text-gray-500 mb-1">Official Source</p>
              <a href={scheme.official_link} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1 text-civic-600 hover:underline break-all">
                {scheme.official_link} <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">MyScheme Portal</p>
              <a href={scheme.myscheme_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1 text-civic-600 hover:underline break-all">
                {scheme.myscheme_url} <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Data Source</p>
              <p className="text-gray-700">{scheme.source_dataset} (public dataset)</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Data Ingested</p>
              <p className="text-gray-700">{new Date(scheme.ingested_at).toLocaleDateString('en-IN')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Individually Verified</p>
              <p className={scheme.verified ? 'text-civic-700' : 'text-amber-700'}>
                {scheme.verified ? 'Yes' : 'No — check official source'}
              </p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              <strong>Disclaimer:</strong> This information is sourced from a public dataset and may not reflect the latest official updates.
              Always verify eligibility and apply through the official government channel.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
