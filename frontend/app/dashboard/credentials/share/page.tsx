'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import api from '@/lib/api';

const defaultForm = {
  email: '',
  username: '',
  domain: '',
  breach_source: '',
  leak_date: '',
  data_types: '',
  is_exposed: true,
  is_verified: false,
  source_url: '',
  notes: '',
};

export default function ShareCredentialPage() {
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
        email: formData.email.trim(),
        username: formData.username.trim() || null,
        domain: formData.domain.trim() || null,
        breach_source: formData.breach_source.trim() || null,
        is_exposed: formData.is_exposed,
        is_verified: formData.is_verified,
        source_url: formData.source_url.trim() || null,
        metadata: formData.notes ? { notes: formData.notes.trim() } : {},
      };

      if (formData.leak_date) {
        payload.leak_date = formData.leak_date;
      }

      if (formData.data_types) {
        payload.data_types = formData.data_types
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean);
      }

      await api.post('/threats/leaked-credentials/', payload);
      setSuccess('Credential shared successfully!');
      setTimeout(() => router.push('/dashboard/credentials'), 1200);
    } catch (err: any) {
      const message =
        err?.response?.data && typeof err.response.data === 'object'
          ? Object.entries(err.response.data)
              .map(([key, val]) => `${key}: ${val}`)
              .join('\n')
          : 'Failed to share credential. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Share Leaked Credential</h1>
          <p className="text-gray-400 mt-1">Help the community stay ahead of exposed accounts.</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-600 rounded-lg hover:bg-gray-700 transition"
        >
          ← Back to Credentials
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Email *</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => updateField('email', e.target.value)}
              placeholder="analyst@example.com"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => updateField('username', e.target.value)}
              placeholder="user123"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Domain</label>
            <input
              type="text"
              value={formData.domain}
              onChange={(e) => updateField('domain', e.target.value)}
              placeholder="example.com"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Breach source</label>
            <input
              type="text"
              value={formData.breach_source}
              onChange={(e) => updateField('breach_source', e.target.value)}
              placeholder="Collection #1, Ransomware leak..."
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Leak date</label>
            <input
              type="date"
              value={formData.leak_date}
              onChange={(e) => updateField('leak_date', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Data types (comma separated)</label>
            <input
              type="text"
              value={formData.data_types}
              onChange={(e) => updateField('data_types', e.target.value)}
              placeholder="password, phone, address"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3 bg-gray-900/40 border border-gray-700 rounded-xl p-4">
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.is_exposed}
                onChange={(e) => updateField('is_exposed', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Credential is publicly exposed
            </label>
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.is_verified}
                onChange={(e) => updateField('is_verified', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Verified by analyst
            </label>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Source URL</label>
            <input
              type="url"
              value={formData.source_url}
              onChange={(e) => updateField('source_url', e.target.value)}
              placeholder="https://leak.example.com/post"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Notes for reviewers</label>
          <textarea
            rows={4}
            value={formData.notes}
            onChange={(e) => updateField('notes', e.target.value)}
            placeholder="Add context, validation steps, or remediation guidance..."
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="pt-4 flex flex-wrap gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl hover:from-blue-500 hover:to-purple-500 disabled:opacity-60"
          >
            {submitting ? 'Sharing…' : 'Share Credential'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/dashboard/credentials')}
            className="px-6 py-3 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

