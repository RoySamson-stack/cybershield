'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

export default function ThreatsPage() {
  const router = useRouter();
  const [threats, setThreats] = useState<any[]>([]);
  const [mapData, setMapData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    threat_type: '',
    severity: '',
  });

  useEffect(() => {
    fetchThreats();
    fetchMapData();
  }, [filters]);

  const fetchThreats = async () => {
    try {
      const params: any = {};
      if (filters.threat_type) params.threat_type = filters.threat_type;
      if (filters.severity) params.severity = filters.severity;

      const response = await api.get('/threats/threat-intelligence/', { params });
      setThreats(response.data.results || response.data || []);
    } catch (error) {
      console.error('Failed to fetch threats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMapData = async () => {
    try {
      const response = await api.get('/threats/threat-intelligence/map_data/');
      setMapData(response.data || []);
    } catch (error) {
      console.error('Failed to fetch map data:', error);
    }
  };

  const severityBreakdown = useMemo(() => {
    const counts: Record<string, number> = {};
    threats.forEach((threat) => {
      const key = threat.severity || 'unknown';
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts).map(([severity, count]) => ({ severity, count }));
  }, [threats]);

  const typeBreakdown = useMemo(() => {
    const counts: Record<string, number> = {};
    threats.forEach((threat) => {
      const key = threat.threat_type || 'other';
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count);
  }, [threats]);

  const topCountries = useMemo(() => (mapData || []).slice(0, 6), [mapData]);

  const timelineActivity = useMemo(() => {
    const bucket: Record<string, number> = {};
    threats.forEach((threat) => {
      if (!threat.first_seen) return;
      const label = new Date(threat.first_seen).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      bucket[label] = (bucket[label] || 0) + 1;
    });
    return Object.entries(bucket)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 7);
  }, [threats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading threats...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Threat Intelligence</h1>
          <p className="text-gray-400 mt-1">Threats shared and discussed by the cybersecurity community</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 flex flex-wrap gap-4">
        <select
          value={filters.threat_type}
          onChange={(e) => setFilters({ ...filters, threat_type: e.target.value })}
          className="px-4 py-2 border border-gray-600 rounded-lg text-gray-300 bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Types</option>
          <option value="ransomware">Ransomware</option>
          <option value="data_breach">Data Breach</option>
          <option value="phishing">Phishing</option>
          <option value="c2">C2 Server</option>
          <option value="malware">Malware</option>
          <option value="apt">APT</option>
        </select>
        <select
          value={filters.severity}
          onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
          className="px-4 py-2 border border-gray-600 rounded-lg text-gray-300 bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <Link
          href="/dashboard/threats/share"
          className="ml-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition text-center"
        >
          Share Threat →
        </Link>
      </div>

      {/* Quick breakdowns instead of heavy charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Severity breakdown</h3>
            <span className="text-sm text-gray-500">{severityBreakdown.length} levels</span>
          </div>
          {severityBreakdown.length ? (
            <ul className="space-y-3">
              {severityBreakdown.map((item) => (
                <li key={item.severity} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{item.severity}</span>
                  <span className="text-white font-semibold">{item.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No severity data yet.</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Threat types</h3>
            <span className="text-sm text-gray-500">{typeBreakdown.length} categories</span>
          </div>
          {typeBreakdown.length ? (
            <ul className="space-y-3">
              {typeBreakdown.slice(0, 6).map((item) => (
                <li key={item.type} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{item.type.replace('_', ' ')}</span>
                  <span className="text-white font-semibold">{item.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No threat type data yet.</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Top countries</h3>
            <span className="text-sm text-gray-500">{topCountries.length} entries</span>
          </div>
          {topCountries.length ? (
            <ul className="space-y-3">
              {topCountries.map((country) => (
                <li key={country.country} className="flex items-center justify-between">
                  <div>
                    <p className="text-white text-sm">{country.country}</p>
                    <p className="text-xs text-gray-500">
                      Critical: {country.critical || 0} · High: {country.high || 0}
                    </p>
                  </div>
                  <span className="text-white font-semibold">{country.threats || country.count || 0}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No country data yet.</p>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Recent timeline</h3>
            <p className="text-sm text-gray-400">Days with the most shared threats</p>
          </div>
          <button
            className="text-sm text-gray-400 hover:text-gray-200"
            onClick={() => {
              setLoading(true);
              fetchThreats();
            }}
          >
            Refresh data
          </button>
        </div>
        {timelineActivity.length ? (
          <div className="flex flex-wrap gap-4">
            {timelineActivity.map((item) => (
              <div key={item.date} className="flex-1 min-w-[120px] bg-gray-900/40 border border-gray-700 rounded-lg p-3">
                <p className="text-sm text-gray-400">{item.date}</p>
                <p className="text-2xl font-semibold text-white">{item.count}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No timeline data yet.</p>
        )}
      </div>

      {/* Threats Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">All Threats</h3>
              <p className="text-sm text-gray-400 mt-1">Threat intelligence shared by the community</p>
            </div>
            <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">
              Export →
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Threat</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Countries</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {threats.length > 0 ? (
                threats.map((threat: any) => (
                  <tr
                    key={threat.id}
                    className="hover:bg-gray-700/50 transition cursor-pointer"
                    onClick={() => router.push(`/dashboard/threats/${threat.id}`)}
                  >
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-white">{threat.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-300 capitalize">{threat.threat_type?.replace('_', ' ')}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          threat.severity === 'critical'
                            ? 'bg-red-500/20 text-red-400'
                            : threat.severity === 'high'
                            ? 'bg-orange-500/20 text-orange-400'
                            : threat.severity === 'medium'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}
                      >
                        {threat.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300">
                        {threat.affected_countries?.slice(0, 3).join(', ') || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(threat.first_seen || threat.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                        View →
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No threats found. Be the first to share one!
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
