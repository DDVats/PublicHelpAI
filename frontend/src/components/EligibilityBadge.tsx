import type { EligibilityInfo } from '../api';
import { CheckCircle, AlertCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface Props {
  eligibility: EligibilityInfo;
  compact?: boolean;
}

const STATUS_CONFIG = {
  potentially_eligible: {
    icon: CheckCircle,
    badge: 'badge-eligible',
    label: 'Potentially Eligible',
    color: 'text-civic-600',
  },
  needs_more_info: {
    icon: AlertCircle,
    badge: 'badge-needs-info',
    label: 'More Info Needed',
    color: 'text-amber-600',
  },
  not_eligible: {
    icon: XCircle,
    badge: 'badge-not-eligible',
    label: 'Criteria Not Met',
    color: 'text-red-600',
  },
};

export default function EligibilityBadge({ eligibility, compact = false }: Props) {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[eligibility.status] || STATUS_CONFIG.needs_more_info;
  const Icon = cfg.icon;

  if (compact) {
    return (
      <span className={cfg.badge}>
        <Icon className="w-3 h-3" />
        {cfg.label}
      </span>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2">
          <Icon className={`w-5 h-5 ${cfg.color}`} />
          <span className="font-medium text-sm">{cfg.label}</span>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 border-t border-gray-100 bg-gray-50 space-y-2 text-xs">
          <p className="text-gray-600 mt-2">{eligibility.explanation}</p>

          {eligibility.matched_rules.length > 0 && (
            <div>
              <p className="font-medium text-civic-700 mb-1">Criteria matched:</p>
              <ul className="space-y-0.5">
                {eligibility.matched_rules.map((r, i) => (
                  <li key={i} className="flex gap-1.5">
                    <CheckCircle className="w-3 h-3 text-civic-500 mt-0.5 shrink-0" />
                    <span className="text-gray-600">{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {eligibility.failed_rules.length > 0 && (
            <div>
              <p className="font-medium text-red-700 mb-1">Criteria not met:</p>
              <ul className="space-y-0.5">
                {eligibility.failed_rules.map((r, i) => (
                  <li key={i} className="flex gap-1.5">
                    <XCircle className="w-3 h-3 text-red-500 mt-0.5 shrink-0" />
                    <span className="text-gray-600">{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {eligibility.unknown_rules.length > 0 && (
            <div>
              <p className="font-medium text-amber-700 mb-1">Information needed:</p>
              <ul className="space-y-0.5">
                {eligibility.unknown_rules.map((r, i) => (
                  <li key={i} className="flex gap-1.5">
                    <AlertCircle className="w-3 h-3 text-amber-500 mt-0.5 shrink-0" />
                    <span className="text-gray-600">{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
