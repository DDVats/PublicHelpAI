import { Shield, Lock, Database, Eye, Trash2, ExternalLink } from 'lucide-react';

export default function Privacy() {
  return (
    <div className="page-container py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="section-title mb-2 flex items-center gap-2">
          <Shield className="w-6 h-6 text-civic-600" /> Privacy & Data Policy
        </h1>
        <p className="text-gray-500 text-sm mb-8">Last updated: 2026-10-16</p>

        <div className="space-y-6">
          {[
            {
              icon: Lock,
              title: 'No Data Sent to External Servers',
              content: 'Your profile (age, income, state, category, etc.) is stored only in your browser\'s session memory (React state). It is never sent to any third-party server, analytics platform, or advertising network. The only server your browser contacts is the local PublicHelp AI backend running on your own machine (localhost:8000).',
            },
            {
              icon: Eye,
              title: 'What We Do NOT Collect',
              content: 'PublicHelp AI never asks for and never stores:\n• Aadhaar number\n• PAN card number\n• Bank account or financial details\n• Passwords or credentials\n• Real name or contact information\n• Precise location',
            },
            {
              icon: Database,
              title: 'Local Session Storage',
              content: 'A random session ID (e.g. "local-session-abc123") is stored in localStorage to allow the "Saved Schemes" feature to work within your browser session. This ID contains no personal information. Saved schemes are stored in the backend\'s in-memory store and reset when the backend server restarts. No scheme saves are persisted to disk.',
            },
            {
              icon: Trash2,
              title: 'Clearing Your Data',
              content: 'You can clear all profile data by clicking "Clear profile" in the profile form. Your browser session ID can be cleared by opening Developer Tools → Application → Local Storage and deleting the "sid" key. The backend session cache resets automatically on server restart.',
            },
            {
              icon: Shield,
              title: 'Scheme Data Sources',
              content: 'Scheme information is sourced from the public gov-myscheme-dataset (github.com/Aryan-Pardeshi/gov-myscheme-dataset), which aggregates data from myscheme.gov.in. This data is not individually verified and may be outdated. Always check the official link on any scheme detail page before taking action.',
            },
            {
              icon: ExternalLink,
              title: 'External Links',
              content: 'Scheme detail pages link to official government portals (myscheme.gov.in and state government sites). These are external websites with their own privacy policies. PublicHelp AI is not responsible for the content or privacy practices of these sites.',
            },
          ].map(({ icon: Icon, title, content }) => (
            <div key={title} className="card p-6">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-civic-50 rounded-lg flex items-center justify-center shrink-0">
                  <Icon className="w-4 h-4 text-civic-600" />
                </div>
                <div>
                  <h2 className="font-semibold text-gray-900 mb-2">{title}</h2>
                  <p className="text-sm text-gray-600 whitespace-pre-line">{content}</p>
                </div>
              </div>
            </div>
          ))}

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
            <h2 className="font-semibold text-amber-900 mb-2">Disclaimer</h2>
            <p className="text-sm text-amber-800">
              PublicHelp AI is an independent academic prototype. It is <strong>not affiliated with, endorsed by, or an official service of</strong> the Government of India, any state government, or any ministry. Eligibility assessments are informational only and do not constitute a legal determination, guarantee of benefit receipt, or official advice. Always apply for schemes through official government channels.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
