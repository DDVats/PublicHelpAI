import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { compareSchemes } from '../api';
import type { SchemeDetail } from '../api';
import { ExternalLink, Loader2 } from 'lucide-react';
import EligibilityBadge from '../components/EligibilityBadge';
import { useProfile } from '../App';

export default function Compare() {
  const [searchParams] = useSearchParams();
  const { profile } = useProfile();
  const [schemes, setSchemes] = useState<SchemeDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const idsParam = searchParams.get('ids');
  const ids = idsParam ? idsParam.split(',').map(Number).filter(Boolean) : [];

  useEffect(() => {
    if (ids.length < 2) return;
    setLoading(true);
    compareSchemes(ids, Object.keys(profile).length > 0 ? profile : undefined)
      .then(r => setSchemes(r.data.schemes))
      .catch(() => setError('Failed to load schemes for comparison.'))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsParam]);

  if (ids.length < 2) return (
    <div className="page-container py-12 text-center text-gray-500">
      <p className="text-lg font-medium mb-2">No schemes selected for comparison</p>
      <p className="text-sm">Use the compare button on scheme cards in the search results.</p>
    </div>
  );

  if (loading) return <div className="flex justify-center py-24"><Loader2 className="w-8 h-8 animate-spin text-civic-600" /></div>;
  if (error) return <div className="page-container py-12 text-center text-red-600">{error}</div>;

  const ROWS = [
    { label: 'Level', key: 'level' },
    { label: 'State / Ministry', key: 'state_ministry' },
    { label: 'Application Mode', key: 'application_mode' },
    { label: 'Benefits', key: 'benefits' },
    { label: 'Documents Required', key: 'documents_required' },
  ];

  return (
    <div className="page-container py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="section-title mb-2">Scheme Comparison</h1>
        <p className="text-gray-500 text-sm mb-6">Comparing {schemes.length} schemes side by side.</p>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="w-32 p-3 text-left text-xs font-medium text-gray-500 bg-gray-50 border border-gray-200">Feature</th>
                {schemes.map(s => (
                  <th key={s.id} className="p-3 text-left text-sm font-semibold text-gray-900 bg-white border border-gray-200 min-w-48">
                    <a href={`/schemes/${s.id}`} className="hover:text-civic-700">{s.name}</a>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Eligibility row */}
              <tr>
                <td className="p-3 text-xs font-medium text-gray-500 bg-gray-50 border border-gray-200">Eligibility</td>
                {schemes.map(s => (
                  <td key={s.id} className="p-3 border border-gray-200">
                    {s.eligibility
                      ? <EligibilityBadge eligibility={s.eligibility as Parameters<typeof EligibilityBadge>[0]['eligibility']} compact />
                      : <span className="text-xs text-gray-400">—</span>}
                  </td>
                ))}
              </tr>

              {/* Description */}
              <tr className="bg-gray-50">
                <td className="p-3 text-xs font-medium text-gray-500 border border-gray-200">Description</td>
                {schemes.map(s => (
                  <td key={s.id} className="p-3 text-xs text-gray-700 border border-gray-200">
                    <p className="line-clamp-4">{s.description}</p>
                  </td>
                ))}
              </tr>

              {ROWS.map((row, i) => (
                <tr key={row.key} className={i % 2 === 0 ? '' : 'bg-gray-50'}>
                  <td className="p-3 text-xs font-medium text-gray-500 bg-gray-50 border border-gray-200">{row.label}</td>
                  {schemes.map(s => (
                    <td key={s.id} className="p-3 text-xs text-gray-700 border border-gray-200">
                      <p className="line-clamp-3">{((s as unknown) as Record<string, unknown>)[row.key] as string || '—'}</p>
                    </td>
                  ))}
                </tr>
              ))}

              {/* Source */}
              <tr>
                <td className="p-3 text-xs font-medium text-gray-500 bg-gray-50 border border-gray-200">Official Source</td>
                {schemes.map(s => (
                  <td key={s.id} className="p-3 border border-gray-200">
                    <a href={s.official_link} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-civic-600 hover:underline flex items-center gap-1">
                      Official link <ExternalLink className="w-3 h-3" />
                    </a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
