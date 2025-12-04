'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';

export default function CredentialsPage() {
  const [credentials, setCredentials] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetchCredentials();
    fetchStats();
  }, []);

  const fetchCredentials = async () => {
    try {
      const response = await api.get('/threats/leaked-credentials/');
      setCredentials(response.data.results || response.data || []);
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/threats/leaked-credentials/stats/');
      setStats(response.data || {});
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearching(true);
      await fetchCredentials();
      setSearching(false);
      return;
    }

    setSearching(true);
    try {
      const params: any = {};
      if (searchQuery.includes('@')) {
        params.email = searchQuery.trim();
      } else if (searchQuery.includes('.')) {
        params.domain = searchQuery.trim();
      } else {
        params.username = searchQuery.trim();
      }

      const response = await api.get('/threats/leaked-credentials/search/', { params });
      setCredentials(response.data || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  const topBreaches = useMemo(() => stats.by_breach || [], [stats]);

  const domainHighlights = useMemo(() => {
    const map: Record<string, number> = {};
    credentials.forEach((cred) => {
      const key = cred.domain || 'unknown';
      map[key] = (map[key] || 0) + 1;
    });
    return Object.entries(map)
      .map(([domain, count]) => ({ domain, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);
  }, [credentials]);

  if (loading && !credentials.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading credentials...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Leaked Credentials</h1>
        <p className="text-gray-400 mt-1">Search and share exposed credentials from data breaches</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Credentials</p>
            <p className="text-2xl font-bold text-white">{(stats.total || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-500/20 rounded-lg">
              <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Exposed</p>
            <p className="text-2xl font-bold text-red-400">{(stats.exposed || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-yellow-500/20 rounded-lg">
              <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Recent (30 days)</p>
            <p className="text-2xl font-bold text-white">{(stats.recent || 0).toLocaleString()}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Unique Breaches</p>
            <p className="text-2xl font-bold text-white">{stats.by_breach?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Search Credentials</h3>
        <div className="flex gap-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyUp={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter email, username, or domain"
            className="flex-1 px-4 py-3 border border-gray-600 rounded-lg text-white bg-gray-700 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleSearch}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-xl"
          >
            {searching ? 'Searching…' : 'Search'}
          </button>
        </div>
      </div>

      {/* Quick breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Top breaches</h3>
            <span className="text-sm text-gray-500">{topBreaches.length} sources</span>
          </div>
          {topBreaches.length ? (
            <ul className="space-y-3">
              {topBreaches.slice(0, 6).map((item: any) => (
                <li key={item.breach_source} className="flex items-center justify-between">
                  <span className="text-gray-300">{item.breach_source || 'Unknown'}</span>
                  <span className="text-white font-semibold">{item.count?.toLocaleString?.() || item.count || 0}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No breach data available yet.</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Hot domains</h3>
            <span className="text-sm text-gray-500">{domainHighlights.length} domains</span>
          </div>
          {domainHighlights.length ? (
            <ul className="space-y-3">
              {domainHighlights.map((item) => (
                <li key={item.domain} className="flex items-center justify-between">
                  <span className="text-gray-300">{item.domain}</span>
                  <span className="text-white font-semibold">{item.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No domain data yet.</p>
          )}
        </div>
      </div>

      {/* Credentials Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Leaked Credentials</h3>
              <p className="text-sm text-gray-400 mt-1">Credentials shared by the community</p>
            </div>
            <Link href="/dashboard/credentials/share" className="text-sm text-blue-400 hover:text-blue-200 font-medium">
              Share Credentials →
            </Link>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Username</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Domain</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Breach Source</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Leak Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {credentials.length > 0 ? (
                credentials.map((cred: any) => (
                  <tr key={cred.id} className="hover:bg-gray-700/50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">{cred.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300">{cred.username || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300">{cred.domain || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300">{cred.breach_source || 'Unknown'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {cred.leak_date ? new Date(cred.leak_date).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          cred.is_exposed
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-green-500/20 text-green-400'
                        }`}
                      >
                        {cred.is_exposed ? 'Exposed' : 'Safe'}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    {searchQuery ? 'No credentials found. Try a different search.' : 'No credentials found. Share or search for leaked credentials!'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
