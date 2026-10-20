import { useEffect, useState } from 'react';
import { getSaved } from '../api';
import { useProfile } from '../App';
import SchemeCard from '../components/SchemeCard';
import { Bookmark, Loader2 } from 'lucide-react';
import type { SchemeCard as SchemeCardType } from '../api';

export default function Saved() {
  const { sessionId, savedIds } = useProfile();
  const [schemes, setSchemes] = useState<SchemeCardType[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (savedIds.size === 0) { setSchemes([]); return; }
    setLoading(true);
    getSaved(sessionId)
      .then(r => setSchemes(r.data.schemes || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [savedIds, sessionId]);

  return (
    <div className="page-container py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="section-title mb-2 flex items-center gap-2">
          <Bookmark className="w-6 h-6 text-saffron-500" /> Saved Schemes
        </h1>
        <p className="text-gray-500 text-sm mb-6">
          {savedIds.size} scheme(s) saved in this session. Saved schemes are stored in memory only and reset when you close the tab.
        </p>

        {loading && <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-civic-600" /></div>}

        {!loading && schemes.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <Bookmark className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">No saved schemes yet</p>
            <p className="text-sm mt-1">Click the bookmark icon on any scheme card to save it here.</p>
          </div>
        )}

        <div className="space-y-4">
          {schemes.map(s => (
            <SchemeCard key={s.id} scheme={s} />
          ))}
        </div>
      </div>
    </div>
  );
}
