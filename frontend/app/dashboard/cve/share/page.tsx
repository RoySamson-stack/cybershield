'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import api from '@/lib/api';

const severityOptions = ['critical', 'high', 'medium', 'low', 'info'];
const statusOptions = ['new', 'analyzing', 'exploited', 'patched', 'disputed'];
const exploitMaturityOptions = [
  'unproven',
  'proof_of_concept',
  'functional',
  'high',
  'not_defined',
];

export default function ShareCVEPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    cve_id: '',
    title: '',
    description: '',
    severity: 'medium',
    status: 'new',
    cvss_v3_score: '',
    vendor: '',
    cwe_id: '',
    affected_products: '',
    affected_versions: '',
    has_exploit: false,
    exploit_available: false,
    poc_available: false,
    poc_url: '',
    github_repo: '',
    exploit_maturity: 'not_defined',
    published_date: '',
    references: '',
    tags: '',
  });

  const updateField = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const payload: Record<string, any> = {
        cve_id: formData.cve_id.trim(),
        title: formData.title.trim(),
        description: formData.description.trim(),
        severity: formData.severity,
        status: formData.status,
        exploit_maturity: formData.exploit_maturity,
        vendor: formData.vendor.trim() || null,
        cwe_id: formData.cwe_id.trim() || null,
        poc_url: formData.poc_url.trim() || null,
        github_repo: formData.github_repo.trim() || null,
        has_exploit: formData.has_exploit,
        exploit_available: formData.exploit_available,
        poc_available: formData.poc_available,
        affected_products: formData.affected_products
          ? formData.affected_products.split(',').map((item) => item.trim()).filter(Boolean)
          : [],
        affected_versions: formData.affected_versions
          ? formData.affected_versions.split(',').map((item) => item.trim()).filter(Boolean)
          : [],
        references: formData.references
          ? formData.references
              .split('\n')
              .map((item) => item.trim())
              .filter(Boolean)
          : [],
        tags: formData.tags
          ? formData.tags.split(',').map((item) => item.trim()).filter(Boolean)
          : [],
      };

      if (formData.cvss_v3_score) {
        payload.cvss_v3_score = parseFloat(formData.cvss_v3_score);
      }
      if (formData.published_date) {
        payload.published_date = new Date(formData.published_date).toISOString();
      }

      await api.post('/cve/cves/', payload);
      setSuccess('CVE shared successfully!');
      setTimeout(() => router.push('/dashboard/cve'), 1200);
    } catch (err: any) {
      const message =
        err?.response?.data && typeof err.response.data === 'object'
          ? Object.entries(err.response.data)
              .map(([key, val]) => `${key}: ${val}`)
              .join('\n')
          : 'Failed to share CVE. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Share a CVE</h1>
          <p className="text-gray-400 mt-1">
            Provide as much detail as possible so the community can act quickly.
          </p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-600 rounded-lg hover:bg-gray-700 transition"
        >
          ← Back to CVE Dashboard
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        className="bg-gray-800 border border-gray-700 rounded-2xl p-6 space-y-6"
      >
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
            <label className="block text-sm font-medium text-gray-300 mb-1">CVE ID *</label>
            <input
              type="text"
              required
              placeholder="CVE-2024-1234"
              value={formData.cve_id}
              onChange={(e) => updateField('cve_id', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Vendor</label>
            <input
              type="text"
              placeholder="Apache, Microsoft…"
              value={formData.vendor}
              onChange={(e) => updateField('vendor', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Title *</label>
          <input
            type="text"
            required
            placeholder="Remote Code Execution in …"
            value={formData.title}
            onChange={(e) => updateField('title', e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Description *</label>
          <textarea
            required
            rows={5}
            placeholder="Explain the vulnerability, impact, exploitation steps…"
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Severity</label>
            <select
              value={formData.severity}
              onChange={(e) => updateField('severity', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            >
              {severityOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Status</label>
            <select
              value={formData.status}
              onChange={(e) => updateField('status', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            >
              {statusOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">CVSS v3 Score</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="10"
              placeholder="Optional"
              value={formData.cvss_v3_score}
              onChange={(e) => updateField('cvss_v3_score', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Affected Products (comma-separated)
            </label>
            <input
              type="text"
              placeholder="Apache Struts, Linux Kernel"
              value={formData.affected_products}
              onChange={(e) => updateField('affected_products', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Affected Versions (comma-separated)
            </label>
            <input
              type="text"
              placeholder="2.0-2.5, 5.0-6.0"
              value={formData.affected_versions}
              onChange={(e) => updateField('affected_versions', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-900/40 border border-gray-700 rounded-xl p-4 space-y-3">
            <p className="text-sm font-semibold text-white">Exploit information</p>
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.has_exploit}
                onChange={(e) => updateField('has_exploit', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Evidence of exploitation in the wild
            </label>
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.exploit_available}
                onChange={(e) => updateField('exploit_available', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Exploit publicly available
            </label>
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input
                type="checkbox"
                checked={formData.poc_available}
                onChange={(e) => updateField('poc_available', e.target.checked)}
                className="rounded border-gray-600 bg-gray-800"
              />
              Proof-of-concept published
            </label>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">PoC URL</label>
              <input
                type="url"
                placeholder="https://github.com/example/poc"
                value={formData.poc_url}
                onChange={(e) => updateField('poc_url', e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">GitHub Repo</label>
              <input
                type="url"
                placeholder="https://github.com/owner/repo"
                value={formData.github_repo}
                onChange={(e) => updateField('github_repo', e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Exploit maturity</label>
              <select
                value={formData.exploit_maturity}
                onChange={(e) => updateField('exploit_maturity', e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
              >
                {exploitMaturityOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Published date</label>
            <input
              type="date"
              value={formData.published_date}
              onChange={(e) => updateField('published_date', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">CWE ID</label>
            <input
              type="text"
              placeholder="CWE-79"
              value={formData.cwe_id}
              onChange={(e) => updateField('cwe_id', e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            References (one per line)
          </label>
          <textarea
            rows={4}
            placeholder="https://advisory.com/example"
            value={formData.references}
            onChange={(e) => updateField('references', e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            placeholder="rce, web, linux"
            value={formData.tags}
            onChange={(e) => updateField('tags', e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="pt-4 flex flex-wrap gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl hover:from-blue-500 hover:to-purple-500 disabled:opacity-60"
          >
            {submitting ? 'Sharing…' : 'Share CVE'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/dashboard/cve')}
            className="px-6 py-3 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}


