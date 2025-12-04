'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import api from '@/lib/api';

const threatTypes = [
  'ransomware',
  'data_breach',
  'phishing',
  'c2',
  'malware',
  'apt',
  'vulnerability',
  'other',
];

const severities = ['critical', 'high', 'medium', 'low'];

const defaultForm = {
  threat_type: 'ransomware',
  title: '',
  description: '',
  severity: 'medium',
  indicators: '',
  affected_countries: '',
  affected_industries: '',
  first_seen: '',
  last_seen: '',
  source: '',
  source_url: '',
  is_verified: false,
};

export default function ShareThreatPage() {
  const router = useRouter();
  const [formData, setFormData] = useState(defaultForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const updateField = (field: keyof typeof defaultForm, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const payload: Record<string, any> = {
        threat_type: formData.threat_type,
        title: formData.title.trim(),
        description: formData.description.trim(),
        severity: formData.severity,
        source: formData.source.trim() || null,
        source_url: formData.source_url.trim() || null,
        is_verified: formData.is_verified,
      };

      if (formData.indicators) {
        try {
          payload.indicators = JSON.parse(formData.indicators);
        } catch (parseError) {
          throw new Error('Indicators must be valid JSON (e.g. {"ips": ["1.1.1.1"]}).');
        }
      }

      if (formData.affected_countries) {
        payload.affected_countries = formData.affected_countries
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean);
      }

      if (formData.affected_industries) {
        payload.affected_industries = formData.affected_industries
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean);
      }

      if (formData.first_seen) {
        payload.first_seen = new Date(formData.first_seen).toISOString();
      }
      if (formData.last_seen) {
        payload.last_seen = new Date(formData.last_seen).toISOString();
      }

      await api.post('/threats/threat-intelligence/', payload);
      setSuccess('Threat shared successfully!');
      setTimeout(() => router.push('/dashboard/threats'), 1200);
    } catch (err: any) {
      const message =
        typeof err?.message === 'string' && err.message.includes('Indicators must be')
          ? err.message
          : err?.response?.data && typeof err.response.data === 'object'
          ? Object.entries(err.response.data)
              .map(([key, val]) => `${key}: ${val}`)
              .join('\n')
          : 'Failed to share threat. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Share Threat Intelligence</h1>
          <p className="text-gray-400 mt-1">Add new campaigns, indicators, or insights for the community.</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-600 rounded-lg hover:bg-gray-700 transition"
        >
          ← Back to Threats
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-gray-800 border border-gray-700 rounded-2xl p-6 space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/40 text-red-200 px-4 py-3 rounded-lg text-sm whitespace-pre-line">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500/10 border border-green-500/40 text-green-200 px-4 py-3 rounded-lg text-sm">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Threat type</label>
            <select
              value={formData.threat_type}
              onChange={(e) => updateField('threat_type', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            >
              {threatTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Severity</label>
            <select
              value={formData.severity}
              onChange={(e) => updateField('severity', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            >
              {severities.map((level) => (
                <option key={level} value={level}>
                  {level.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-3 bg-gray-900/40 border border-gray-700 rounded-xl p-4">
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.is_verified}
                onChange={(e) => updateField('is_verified', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Analyst verified
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => updateField('title', e.target.value)}
            placeholder="New ALPHV ransomware leak"
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Description *</label>
          <textarea
            required
            rows={5}
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            placeholder="Summarize the threat, behavior, and impact..."
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Affected countries (comma separated)</label>
            <input
              type="text"
              value={formData.affected_countries}
              onChange={(e) => updateField('affected_countries', e.target.value)}
              placeholder="US, UK, DE"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Industries targeted</label>
            <input
              type="text"
              value={formData.affected_industries}
              onChange={(e) => updateField('affected_industries', e.target.value)}
              placeholder="Healthcare, Government…"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">First seen</label>
            <input
              type="datetime-local"
              value={formData.first_seen}
              onChange={(e) => updateField('first_seen', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Last seen</label>
            <input
              type="datetime-local"
              value={formData.last_seen}
              onChange={(e) => updateField('last_seen', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Indicators (JSON)</label>
          <textarea
            rows={4}
            value={formData.indicators}
            onChange={(e) => updateField('indicators', e.target.value)}
            placeholder='{"ips": ["1.1.1.1"], "domains": ["bad.example"]}'
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white font-mono text-sm focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-2 text-xs text-gray-500">
            Provide valid JSON so teams can ingest directly. Leave empty if not available.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Source</label>
            <input
              type="text"
              value={formData.source}
              onChange={(e) => updateField('source', e.target.value)}
              placeholder="Blog, private feed, announcement..."
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Source URL</label>
            <input
              type="url"
              value={formData.source_url}
              onChange={(e) => updateField('source_url', e.target.value)}
              placeholder="https://researcher.blog/threat"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="pt-4 flex flex-wrap gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl hover:from-blue-500 hover:to-purple-500 disabled:opacity-60"
          >
            {submitting ? 'Sharing…' : 'Share Threat'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/dashboard/threats')}
            className="px-6 py-3 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

