import { Link } from 'react-router-dom';
import { ExternalLink, Bookmark, BookmarkCheck, GitCompare, Building2, MapPin, Tag, FileText, Zap, Sparkles } from 'lucide-react';
import type { SchemeCard } from '../api';
import EligibilityBadge from './EligibilityBadge';
import { useProfile } from '../App';

interface Props {
  scheme: SchemeCard;
  compareIds?: Set<number>;
  onToggleCompare?: (id: number) => void;
}

export default function SchemeCardComponent({ scheme, compareIds, onToggleCompare }: Props) {
  const { savedIds, toggleSaved } = useProfile();
  const isSaved = savedIds.has(scheme.id);
  const isInCompare = compareIds?.has(scheme.id) ?? false;

  const categories = scheme.categories_raw
    ? scheme.categories_raw.split(/[|,]/).slice(0, 3).map(c => c.trim()).filter(Boolean)
    : [];

  return (
    <div className="card p-5 hover:shadow-md transition-shadow group">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/schemes/${scheme.id}`}
            className="font-semibold text-gray-900 hover:text-civic-700 transition-colors line-clamp-2 leading-snug"
          >
            {scheme.name}
          </Link>
          <div className="flex items-center gap-3 mt-1.5 flex-wrap">
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <Building2 className="w-3 h-3" />
              {scheme.level === 'Central Government' ? 'Central' : 'State'}
            </span>
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <MapPin className="w-3 h-3" />
              {scheme.state_ministry}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={() => toggleSaved(scheme.id)}
            className={`p-1.5 rounded-lg transition-colors ${
              isSaved ? 'text-saffron-600 bg-saffron-50' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
            }`}
            title={isSaved ? 'Remove from saved' : 'Save scheme'}
            aria-label={isSaved ? 'Remove from saved' : 'Save scheme'}
          >
            {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
          </button>
          {onToggleCompare && (
            <button
              onClick={() => onToggleCompare(scheme.id)}
              className={`p-1.5 rounded-lg transition-colors ${
                isInCompare ? 'text-civic-600 bg-civic-50' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}
              title={isInCompare ? 'Remove from compare' : 'Add to compare'}
            >
              <GitCompare className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 line-clamp-2 mb-3">{scheme.description}</p>

      {/* Benefits */}
      {scheme.benefits && (
        <div className="bg-civic-50 rounded-lg px-3 py-2 mb-3">
          <p className="text-xs font-medium text-civic-700 mb-0.5">Benefits</p>
          <p className="text-xs text-civic-800 line-clamp-2">{scheme.benefits}</p>
        </div>
      )}

      {/* Tags */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {categories.map(c => (
            <span key={c} className="flex items-center gap-1 text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
              <Tag className="w-2.5 h-2.5" />
              {c}
            </span>
          ))}
        </div>
      )}

      {/* Structured Document Checklist Badges */}
      {scheme.required_documents && scheme.required_documents.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 mb-3 bg-amber-50/70 border border-amber-200/80 rounded-xl px-3 py-2">
          <span className="text-[11px] font-semibold text-amber-900 flex items-center gap-1">
            <FileText className="w-3 h-3 text-amber-600" />
            Documents:
          </span>
          {scheme.required_documents.slice(0, 4).map(doc => (
            <span key={doc} className="text-[10px] bg-white border border-amber-300 text-amber-900 px-2 py-0.5 rounded-md font-medium shadow-2xs">
              {doc}
            </span>
          ))}
          {scheme.required_documents.length > 4 && (
            <span className="text-[10px] text-amber-700 font-semibold">
              +{scheme.required_documents.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Why Recommended Explainability */}
      {scheme.why_recommended && scheme.why_recommended.length > 0 && (
        <div className="mb-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl px-3 py-2 text-xs text-emerald-900">
          <div className="font-semibold flex items-center gap-1 mb-1 text-[11px] text-emerald-800">
            <Sparkles className="w-3 h-3 text-emerald-600" />
            Why Recommended:
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-[11px] text-emerald-900">
            {scheme.why_recommended.map((reason, idx) => (
              <li key={idx} className="leading-snug">{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Eligibility */}
      {scheme.eligibility && (
        <div className="mb-3">
          <EligibilityBadge eligibility={scheme.eligibility} />
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <Link
            to={`/schemes/${scheme.id}`}
            className="text-xs font-medium text-civic-600 hover:text-civic-700"
          >
            View details
          </Link>
          <a
            href={scheme.official_link || scheme.myscheme_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
          >
            Official source <ExternalLink className="w-3 h-3" />
          </a>
        </div>
        <div className="flex items-center gap-2">
          {scheme.cross_encoder_score !== undefined && scheme.cross_encoder_score !== null && (
            <span
              className="text-[10px] bg-purple-50 text-purple-700 border border-purple-200 px-2 py-0.5 rounded-full font-semibold flex items-center gap-0.5"
              title="Deep Cross-Attention Neural Relevance"
            >
              <Zap className="w-2.5 h-2.5 text-purple-600 fill-purple-600" />
              <span>Neural Match: {(scheme.cross_encoder_score * 100).toFixed(0)}%</span>
            </span>
          )}
          {scheme.ranking_score > 0 && (
            <span className="text-xs text-gray-500 font-medium">
              Match: {(scheme.ranking_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
