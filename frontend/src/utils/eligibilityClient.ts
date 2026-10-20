/**
 * Lightweight client-side eligibility stub.
 * Full assessment is done by the backend; this is a fallback for detail page when
 * the scheme was loaded directly (not via a recommend call).
 */
import type { UserProfile, EligibilityInfo } from '../api';

export function assess_eligibility_client(
  scheme: Record<string, unknown>,
  profile: UserProfile
): EligibilityInfo | null {
  if (Object.keys(profile).length === 0) return null;

  const matched: string[] = [];
  const failed: string[] = [];
  const unknown: string[] = [];

  const minAge = scheme['parsed_min_age'] as number | null;
  const maxAge = scheme['parsed_max_age'] as number | null;
  const parsedGender = scheme['parsed_gender'] as string | null;
  const incomeMax = scheme['parsed_income_max'] as number | null;
  const isCentral = Boolean(scheme['parsed_is_central']);
  const stateMinistry = (scheme['state_ministry'] as string) || '';

  if (minAge || maxAge) {
    if (!profile.age) {
      unknown.push(`Age requirement (${minAge ?? '?'}–${maxAge ?? '?'}) — not provided`);
    } else {
      if (minAge && profile.age < minAge) failed.push(`Age ${profile.age} below minimum ${minAge}`);
      else if (maxAge && profile.age > maxAge) failed.push(`Age ${profile.age} above maximum ${maxAge}`);
      else matched.push(`Age ${profile.age} meets requirement`);
    }
  }

  if (parsedGender && parsedGender !== 'all') {
    if (!profile.gender) unknown.push(`Gender requirement (${parsedGender}) — not provided`);
    else if (profile.gender !== parsedGender && profile.gender !== 'other')
      failed.push(`Gender mismatch`);
    else matched.push(`Gender matches`);
  }

  if (incomeMax) {
    if (!profile.annual_income) unknown.push(`Income ceiling ≤₹${incomeMax.toLocaleString()} — not provided`);
    else if (profile.annual_income > incomeMax) failed.push(`Income ₹${profile.annual_income.toLocaleString()} exceeds ceiling`);
    else matched.push(`Income within ceiling`);
  }

  if (!isCentral && stateMinistry && profile.state) {
    if (!profile.state.toLowerCase().includes(stateMinistry.toLowerCase()) &&
        !stateMinistry.toLowerCase().includes(profile.state.toLowerCase())) {
      failed.push(`State mismatch: scheme for ${stateMinistry}`);
    } else {
      matched.push(`State match`);
    }
  }

  let status: EligibilityInfo['status'];
  let score: number;
  if (failed.length > 0) { status = 'not_eligible'; score = 0; }
  else if (unknown.length > 0) { status = 'needs_more_info'; score = matched.length / (matched.length + unknown.length); }
  else if (matched.length > 0) { status = 'potentially_eligible'; score = 1; }
  else { status = 'needs_more_info'; score = 0.5; unknown.push('No structured rules available'); }

  const parts = [];
  if (matched.length) parts.push('Matched: ' + matched.join('; '));
  if (failed.length) parts.push('Not met: ' + failed.join('; '));
  if (unknown.length) parts.push('Unknown: ' + unknown.join('; '));

  return {
    status,
    score: Math.round(score * 1000) / 1000,
    matched_rules: matched,
    failed_rules: failed,
    unknown_rules: unknown,
    explanation: parts.join(' | ') || 'No structured eligibility data available.',
  };
}
