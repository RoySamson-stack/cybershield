'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

export default function CVEPage() {
  const router = useRouter();
  const [cves, setCves] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [repos, setRepos] = useState<any[]>([]);
  const [reposLoading, setReposLoading] = useState(true);
  const [repoMessage, setRepoMessage] = useState<string | null>(null);
  const [cveRefs, setCveRefs] = useState<any[]>([]);
  const [cveRefsLoading, setCveRefsLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: '',
    has_exploit: '',
    poc_available: '',
    status: '',
    search: '',
  });

  useEffect(() => {
    fetchCVEs();
    fetchStats();
  }, [filters]);

  useEffect(() => {
    let cancelled = false;

    const loadMonitoringData = async () => {
      try {
        await Promise.all([fetchGitHubRepos(), fetchGitHubCVERefs()]);
      } catch (error) {
        // already handled in individual fetchers
      }
    };

    // try once immediately
    loadMonitoringData();

    // retry once if both feeds are empty after a short delay
    const retry = setTimeout(() => {
      if (!cancelled && repos.length === 0 && cveRefs.length === 0) {
        loadMonitoringData();
      }
    }, 3000);

    return () => {
      cancelled = true;
      clearTimeout(retry);
    };
  }, []);

  const fetchCVEs = async () => {
    try {
      const params: any = {};
      if (filters.severity) params.severity = filters.severity;
      if (filters.has_exploit) params.has_exploit = filters.has_exploit;
      if (filters.poc_available) params.poc_available = filters.poc_available;
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;

      const response = await api.get('/cve/cves/', { params });
      setCves(response.data.results || response.data || []);
    } catch (error) {
      console.error('Failed to fetch CVEs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/cve/cves/stats/');
      setStats(response.data || {});
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchGitHubRepos = async () => {
    setReposLoading(true);
    setRepoMessage(null);
    try {
      const response = await api.get('/monitoring/github-repos/', {
        params: { noCache: true },
      });
      setRepos(response.data.results || response.data || []);
    } catch (error) {
      console.error('Failed to fetch GitHub repositories:', error);
      setRepoMessage('Unable to load GitHub repositories right now.');
    } finally {
      setReposLoading(false);
    }
  };

  const fetchGitHubCVERefs = async () => {
    setCveRefsLoading(true);
    try {
      const response = await api.get('/monitoring/github-cve-refs/', {
        params: { page_size: 8, noCache: true },
      });
      setCveRefs(response.data.results || response.data || []);
    } catch (error) {
      console.error('Failed to fetch GitHub CVE references:', error);
    } finally {
      setCveRefsLoading(false);
    }
  };

  const handleTriggerCheck = async (repoId: string) => {
    try {
      await api.post(`/monitoring/github-repos/${repoId}/trigger_check/`);
      setRepoMessage('Check queued successfully. Refresh in a moment to see updates.');
      fetchGitHubRepos();
    } catch (error) {
      console.error('Failed to trigger check:', error);
      setRepoMessage('Failed to queue a new check. Please try again.');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const severityBreakdown = useMemo(() => stats.by_severity || [], [stats]);
  const statusBreakdown = useMemo(() => stats.by_status || [], [stats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading CVEs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">CVE Database</h1>
          <p className="text-gray-400 mt-1">Track and share Common Vulnerabilities and Exposures with PoC exploits</p>
        </div>
        <button
          onClick={() => router.push('/dashboard/cve/share')}
          className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition shadow-lg hover:shadow-xl flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Share CVE
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-5 hover:border-blue-500/50 transition-all hover:shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-blue-500/20 rounded-lg">
              <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 font-medium">Total CVEs</p>
            <p className="text-2xl font-bold text-white">{(stats.total || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-5 hover:border-red-500/50 transition-all hover:shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-red-500/20 rounded-lg">
              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 font-medium">With Exploit</p>
            <p className="text-2xl font-bold text-white">{(stats.with_exploit || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-5 hover:border-purple-500/50 transition-all hover:shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-purple-500/20 rounded-lg">
              <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 font-medium">With PoC</p>
            <p className="text-2xl font-bold text-white">{(stats.with_poc || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-5 hover:border-yellow-500/50 transition-all hover:shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-yellow-500/20 rounded-lg">
              <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 font-medium">Recent (30d)</p>
            <p className="text-2xl font-bold text-white">{(stats.recent_30_days || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-5 hover:border-green-500/50 transition-all hover:shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-green-500/20 rounded-lg">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1 font-medium">Avg CVSS</p>
            <p className="text-2xl font-bold text-white">{stats.average_cvss?.toFixed(1) || '0.0'}</p>
          </div>
        </div>
      </div>

      {/* Quick breakdown instead of heavy charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Severity breakdown</h3>
            <p className="text-sm text-gray-400">Live counts from the API</p>
          </div>
          {severityBreakdown.length ? (
            <ul className="space-y-3">
              {severityBreakdown.map((item: any) => (
                <li key={item.severity} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(item.severity)}`}>
                      {item.severity.toUpperCase()}
                    </span>
                    <span className="text-gray-300">{item.severity_label || item.severity}</span>
                  </div>
                  <span className="text-white font-semibold">{item.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">No severity data yet.</p>
          )}
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Status breakdown</h3>
            <p className="text-sm text-gray-400">Track how CVEs progress</p>
          </div>
          {statusBreakdown.length ? (
            <ul className="space-y-3">
              {statusBreakdown.map((item: any) => (
                <li key={item.status} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{item.status.replace('_', ' ')}</span>
                  <span className="text-white font-semibold">{item.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">No status data yet.</p>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-4 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search CVEs, vendors, products..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="flex-1 min-w-[200px] px-4 py-2.5 border border-gray-600 rounded-lg text-white bg-gray-700/50 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
        />
        <select
          value={filters.severity}
          onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
          className="px-4 py-2.5 border border-gray-600 rounded-lg text-gray-300 bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={filters.has_exploit}
          onChange={(e) => setFilters({ ...filters, has_exploit: e.target.value })}
          className="px-4 py-2.5 border border-gray-600 rounded-lg text-gray-300 bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Exploits</option>
          <option value="true">With Exploit</option>
          <option value="false">No Exploit</option>
        </select>
        <select
          value={filters.poc_available}
          onChange={(e) => setFilters({ ...filters, poc_available: e.target.value })}
          className="px-4 py-2.5 border border-gray-600 rounded-lg text-gray-300 bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All PoCs</option>
          <option value="true">With PoC</option>
          <option value="false">No PoC</option>
        </select>
      </div>

      {/* GitHub Monitored Repositories */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h3 className="text-lg font-semibold text-white">GitHub monitoring</h3>
            <p className="text-sm text-gray-400">Repositories watched for new CVE content</p>
          </div>
          <button
            className="px-4 py-2 bg-gray-700 text-white rounded-lg text-sm hover:bg-gray-600 transition"
            onClick={fetchGitHubRepos}
          >
            Refresh list
          </button>
        </div>
        {repoMessage && (
          <p className="text-sm text-blue-400">{repoMessage}</p>
        )}
        {reposLoading ? (
          <p className="text-gray-500 text-sm">Loading repositories...</p>
        ) : repos.length ? (
          <div className="space-y-4">
            {repos.map((repo: any) => (
              <div key={repo.id} className="p-4 bg-gray-900/40 rounded-lg border border-gray-700 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <a
                      href={repo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-white font-semibold hover:text-blue-400 transition"
                    >
                      {repo.full_name}
                    </a>
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-700 text-gray-300">
                      branch: {repo.default_branch}
                    </span>
                    {repo.check_error && (
                      <span className="text-xs px-2 py-1 rounded-full bg-red-500/20 text-red-300 border border-red-500/30">
                        Needs attention
                      </span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm mt-1">{repo.description || 'No description provided.'}</p>
                  <div className="flex flex-wrap gap-4 text-xs text-gray-500 mt-2">
                    <span>Commits tracked: {repo.total_commits || 0}</span>
                    <span>CVEs found: {repo.total_cves_found || 0}</span>
                    <span>Last check: {repo.last_check_at ? new Date(repo.last_check_at).toLocaleString() : '—'}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleTriggerCheck(repo.id)}
                    className="px-3 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition"
                  >
                    Queue check
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No repositories added yet.</p>
        )}
      </div>

      {/* Recent GitHub CVE references */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h3 className="text-lg font-semibold text-white">Latest GitHub CVE mentions</h3>
            <p className="text-sm text-gray-400">Commits referencing CVE IDs across monitored repos</p>
          </div>
          <button
            className="px-4 py-2 bg-gray-700 text-white rounded-lg text-sm hover:bg-gray-600 transition"
            onClick={fetchGitHubCVERefs}
          >
            Refresh feed
          </button>
        </div>
        {cveRefsLoading ? (
          <p className="text-gray-500 text-sm">Loading commit data…</p>
        ) : cveRefs.length ? (
          <div className="space-y-4">
            {cveRefs.map((ref: any) => (
              <div key={ref.id} className="p-4 bg-gray-900/40 rounded-lg border border-gray-700">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-700 text-gray-300">{ref.cve_id}</span>
                    <span className="text-sm text-gray-400">{ref.repository_name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{ref.commit_date ? new Date(ref.commit_date).toLocaleString() : '—'}</span>
                </div>
                <p className="text-gray-300 text-sm mt-2 line-clamp-2">{ref.commit_message}</p>
                <div className="flex items-center gap-3 text-xs text-blue-400 mt-3">
                  <a href={ref.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    View commit
                  </a>
                  {ref.file_path && (
                    <span className="text-gray-500">Files: {ref.file_path}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No GitHub CVE references found yet.</p>
        )}
      </div>

      {/* CVE List */}
      <div className="space-y-4">
        {cves.length > 0 ? (
          cves.map((cve: any) => (
            <div
              key={cve.id}
              className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 p-6 hover:border-blue-500/50 hover:shadow-xl transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition">
                      {cve.cve_id}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(cve.severity)}`}>
                      {cve.severity.toUpperCase()}
                    </span>
                    {cve.cvss_v3_score && (
                      <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-semibold">
                        CVSS: {cve.cvss_v3_score}
                      </span>
                    )}
                    {cve.has_exploit && (
                      <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-semibold border border-red-500/30">
                        Exploit Available
                      </span>
                    )}
                    {cve.poc_available && (
                      <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-semibold border border-purple-500/30">
                        PoC Available
                      </span>
                    )}
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-2">{cve.title}</h4>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{cve.description}</p>
                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    {cve.vendor && (
                      <div className="flex items-center gap-2 text-gray-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        <span>{cve.vendor}</span>
                      </div>
                    )}
                    {cve.published_date && (
                      <div className="flex items-center gap-2 text-gray-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>{new Date(cve.published_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>{cve.views || 0} views</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                      </svg>
                      <span>{cve.upvotes || 0} upvotes</span>
                    </div>
                  </div>
                  {cve.tags && cve.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {cve.tags.map((tag: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-gray-700/50 text-gray-300 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  {cve.github_repo && (
                    <a
                      href={cve.github_repo}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                    >
                      <svg className="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                      </svg>
                    </a>
                  )}
                  {cve.poc_url && (
                    <a
                      href={cve.poc_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="p-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 rounded-lg transition"
                    >
                      <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-12 text-center">
            <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-gray-400 text-lg mb-2">No CVEs found</p>
            <p className="text-gray-500 text-sm">Try adjusting your filters or share a new CVE</p>
          </div>
        )}
      </div>
    </div>
  );
}

