'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import api from '@/lib/api';

const threatLevels = ['critical', 'high', 'medium', 'low'];
const protocols = ['http', 'https', 'tcp', 'udp', 'dns', 'socks'];

const defaultForm = {
  domain: '',
  ip_address: '',
  hostname: '',
  port: '',
  protocol: 'http',
  c2_family: '',
  malware_family: '',
  country: '',
  asn: '',
  threat_level: 'medium',
  is_active: true,
  notes: '',
};

export default function ShareC2Page() {
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
        domain: formData.domain.trim() || null,
        ip_address: formData.ip_address.trim() || null,
        hostname: formData.hostname.trim() || null,
        protocol: formData.protocol,
        c2_family: formData.c2_family.trim() || null,
        malware_family: formData.malware_family.trim() || null,
        country: formData.country.trim() || null,
        asn: formData.asn.trim() || null,
        threat_level: formData.threat_level,
        is_active: formData.is_active,
        metadata: formData.notes ? { notes: formData.notes.trim() } : {},
      };

      if (formData.port) {
        payload.port = Number(formData.port);
      }

      await api.post('/threats/c2-servers/', payload);
      setSuccess('C2 server shared successfully!');
      setTimeout(() => router.push('/dashboard/c2'), 1200);
    } catch (err: any) {
      const message =
        err?.response?.data && typeof err.response.data === 'object'
          ? Object.entries(err.response.data)
              .map(([key, val]) => `${key}: ${val}`)
              .join('\n')
          : 'Failed to share C2 server. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Share C2 Server</h1>
          <p className="text-gray-400 mt-1">List new infrastructure so defenders can block it quickly.</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-600 rounded-lg hover:bg-gray-700 transition"
        >
          ← Back to C2 Dashboard
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
            <label className="block text-sm font-medium text-gray-300 mb-1">Domain</label>
            <input
              type="text"
              value={formData.domain}
              onChange={(e) => updateField('domain', e.target.value)}
              placeholder="malicious.example.com"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">IP address</label>
            <input
              type="text"
              value={formData.ip_address}
              onChange={(e) => updateField('ip_address', e.target.value)}
              placeholder="192.0.2.10"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Hostname</label>
            <input
              type="text"
              value={formData.hostname}
              onChange={(e) => updateField('hostname', e.target.value)}
              placeholder="box01"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Port</label>
            <input
              type="number"
              min={1}
              max={65535}
              value={formData.port}
              onChange={(e) => updateField('port', e.target.value)}
              placeholder="443"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Protocol</label>
            <select
              value={formData.protocol}
              onChange={(e) => updateField('protocol', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-indigo-500"
            >
              {protocols.map((option) => (
                <option key={option} value={option}>
                  {option.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">C2 family</label>
            <input
              type="text"
              value={formData.c2_family}
              onChange={(e) => updateField('c2_family', e.target.value)}
              placeholder="Cobalt Strike, Sliver…"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Malware family</label>
            <input
              type="text"
              value={formData.malware_family}
              onChange={(e) => updateField('malware_family', e.target.value)}
              placeholder="Ransomware group, botnet…"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Country</label>
            <input
              type="text"
              value={formData.country}
              onChange={(e) => updateField('country', e.target.value)}
              placeholder="Netherlands"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">ASN</label>
            <input
              type="text"
              value={formData.asn}
              onChange={(e) => updateField('asn', e.target.value)}
              placeholder="AS12345"
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Threat level</label>
            <select
              value={formData.threat_level}
              onChange={(e) => updateField('threat_level', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-indigo-500"
            >
              {threatLevels.map((level) => (
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
                checked={formData.is_active}
                onChange={(e) => updateField('is_active', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Infrastructure is currently active
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Notes / detection details</label>
          <textarea
            rows={4}
            value={formData.notes}
            onChange={(e) => updateField('notes', e.target.value)}
            placeholder="Add beacon pattern, certificate fingerprint, campaign info…"
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="pt-4 flex flex-wrap gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl hover:from-indigo-500 hover:to-purple-500 disabled:opacity-60"
          >
            {submitting ? 'Sharing…' : 'Share C2 Server'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/dashboard/c2')}
            className="px-6 py-3 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

