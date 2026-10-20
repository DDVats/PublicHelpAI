import { useState } from 'react';
import { useProfile } from '../App';
import { User, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

const STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat',
  'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
  'Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan',
  'Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
  'Delhi','Puducherry','Chandigarh','Jammu and Kashmir','Ladakh',
  'Andaman and Nicobar Islands','Lakshadweep',
];

const DEMO_PROFILES = [
  {
    label: 'Priya — Student (SC, Rajasthan)',
    profile: { state: 'Rajasthan', age: 20, gender: 'female' as const, caste_category: 'SC' as const, annual_income: 150000, is_rural: true, education: 'undergraduate', occupation: 'student' },
  },
  {
    label: 'Ramesh — Farmer (OBC, Gujarat)',
    profile: { state: 'Gujarat', age: 45, gender: 'male' as const, caste_category: 'OBC' as const, annual_income: 80000, is_rural: true, education: 'primary', occupation: 'farmer' },
  },
  {
    label: 'Meena — Entrepreneur (General, Delhi)',
    profile: { state: 'Delhi', age: 35, gender: 'female' as const, caste_category: 'General' as const, annual_income: 400000, is_rural: false, education: 'graduate', occupation: 'self-employed' },
  },
  {
    label: 'Suresh — Senior Citizen (ST, Kerala)',
    profile: { state: 'Kerala', age: 68, gender: 'male' as const, caste_category: 'ST' as const, annual_income: 50000, is_rural: false, education: 'primary', occupation: 'retired' },
  },
];

export default function ProfileForm() {
  const { profile, setProfile } = useProfile();
  const [open, setOpen] = useState(true);

  return (
    <div className="card">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors"
      >
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-civic-600" />
          <span className="font-semibold text-gray-900">Your Profile</span>
          {Object.keys(profile).length > 0 && (
            <span className="text-xs bg-civic-100 text-civic-700 px-2 py-0.5 rounded-full">
              {Object.keys(profile).filter(k => profile[k as keyof typeof profile] !== undefined).length} fields set
            </span>
          )}
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-4 border-t border-gray-100 pt-4">
          {/* Demo profiles */}
          <div>
            <p className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Demo profiles (fictional — for demonstration only)
            </p>
            <div className="flex flex-wrap gap-2">
              {DEMO_PROFILES.map(dp => (
                <button
                  key={dp.label}
                  onClick={() => setProfile(dp.profile)}
                  className="text-xs px-3 py-1.5 border border-gray-200 rounded-full hover:border-civic-400 hover:text-civic-700 transition-colors"
                >
                  {dp.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {/* State */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">State / UT</label>
              <select
                className="input-field"
                value={profile.state || ''}
                onChange={e => setProfile({ ...profile, state: e.target.value || undefined })}
              >
                <option value="">Any state</option>
                {STATES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            {/* Age */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Age</label>
              <input
                type="number"
                className="input-field"
                placeholder="e.g. 28"
                min={0} max={120}
                value={profile.age ?? ''}
                onChange={e => setProfile({ ...profile, age: e.target.value ? parseInt(e.target.value) : undefined })}
              />
            </div>

            {/* Gender */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Gender</label>
              <select
                className="input-field"
                value={profile.gender || ''}
                onChange={e => setProfile({ ...profile, gender: (e.target.value as 'male' | 'female' | 'other') || undefined })}
              >
                <option value="">Prefer not to say</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Caste */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Category</label>
              <select
                className="input-field"
                value={profile.caste_category || ''}
                onChange={e => setProfile({ ...profile, caste_category: (e.target.value as 'SC' | 'ST' | 'OBC' | 'EWS' | 'General') || undefined })}
              >
                <option value="">Not specified</option>
                <option value="SC">Scheduled Caste (SC)</option>
                <option value="ST">Scheduled Tribe (ST)</option>
                <option value="OBC">Other Backward Class (OBC)</option>
                <option value="EWS">Economically Weaker Section (EWS)</option>
                <option value="General">General / Unreserved</option>
              </select>
            </div>

            {/* Income */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Annual Income (₹)</label>
              <input
                type="number"
                className="input-field"
                placeholder="e.g. 250000"
                min={0}
                value={profile.annual_income ?? ''}
                onChange={e => setProfile({ ...profile, annual_income: e.target.value ? parseInt(e.target.value) : undefined })}
              />
            </div>

            {/* Residence */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Residence</label>
              <select
                className="input-field"
                value={profile.is_rural === undefined ? '' : profile.is_rural ? 'rural' : 'urban'}
                onChange={e => setProfile({ ...profile, is_rural: e.target.value === '' ? undefined : e.target.value === 'rural' })}
              >
                <option value="">Not specified</option>
                <option value="rural">Rural</option>
                <option value="urban">Urban</option>
              </select>
            </div>

            {/* Occupation */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Occupation</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. farmer, student, labourer"
                value={profile.occupation || ''}
                onChange={e => setProfile({ ...profile, occupation: e.target.value || undefined })}
              />
            </div>

            {/* Education */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Education</label>
              <select
                className="input-field"
                value={profile.education || ''}
                onChange={e => setProfile({ ...profile, education: e.target.value || undefined })}
              >
                <option value="">Not specified</option>
                <option value="none">No formal education</option>
                <option value="primary">Primary school</option>
                <option value="secondary">Secondary / 10th</option>
                <option value="higher_secondary">Higher secondary / 12th</option>
                <option value="graduate">Graduate / Degree</option>
                <option value="postgraduate">Post-graduate</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2 pt-1">
            <button
              onClick={() => setProfile({})}
              className="text-xs text-gray-500 hover:text-red-600 transition-colors"
            >
              Clear profile
            </button>
            <span className="text-gray-300">|</span>
            <p className="text-xs text-gray-400">Profile is stored only in your browser session.</p>
          </div>
        </div>
      )}
    </div>
  );
}
