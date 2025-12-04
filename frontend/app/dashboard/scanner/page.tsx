'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '@/lib/api';

export default function ScannerPage() {
  const [targets, setTargets] = useState<any[]>([]);
  const [scans, setScans] = useState<any[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScannerData();
  }, []);

  const fetchScannerData = async () => {
    const isDemo = localStorage.getItem('is_demo') === 'true';
    
    if (isDemo) {
      setTargets([
        { id: '1', target_url: 'https://example.com', target_type: 'website', status: 'active', last_scan: new Date().toISOString() },
        { id: '2', target_url: '192.168.1.1', target_type: 'ip', status: 'active', last_scan: new Date().toISOString() },
      ]);
      setScans([
        { id: '1', target: 'example.com', scan_type: 'vulnerability', status: 'completed', vulnerabilities_found: 5, started_at: new Date().toISOString() },
        { id: '2', target: '192.168.1.1', scan_type: 'port', status: 'running', vulnerabilities_found: 0, started_at: new Date().toISOString() },
      ]);
      setVulnerabilities([
        { id: '1', title: 'SQL Injection', severity: 'high', target: 'example.com', discovered_at: new Date().toISOString() },
        { id: '2', title: 'XSS Vulnerability', severity: 'medium', target: 'example.com', discovered_at: new Date().toISOString() },
      ]);
      setStats({
        total_targets: 45,
        total_scans: 234,
        total_vulnerabilities: 89,
        by_severity: [
          { severity: 'Critical', count: 12 },
          { severity: 'High', count: 28 },
          { severity: 'Medium', count: 35 },
          { severity: 'Low', count: 14 },
        ],
      });
      setLoading(false);
      return;
    }
    
    try {
      const [targetsRes, scansRes, vulnsRes] = await Promise.all([
        api.get('/scanner/targets/').catch(() => ({ data: { results: [] } })),
        api.get('/scanner/scans/').catch(() => ({ data: { results: [] } })),
        api.get('/scanner/vulnerabilities/').catch(() => ({ data: { results: [] } })),
      ]);

      setTargets(targetsRes.data.results || targetsRes.data || []);
      setScans(scansRes.data.results || scansRes.data || []);
      setVulnerabilities(vulnsRes.data.results || vulnsRes.data || []);
    } catch (error) {
      console.error('Failed to fetch scanner data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading scanner data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Security Scanner</h1>
        <p className="text-gray-400 mt-1">Scan targets and share vulnerability findings</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Scan Targets</p>
            <p className="text-2xl font-bold text-white">{stats.total_targets || targets.length}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Scans</p>
            <p className="text-2xl font-bold text-white">{stats.total_scans || scans.length}</p>
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
            <p className="text-sm text-gray-400 mb-1">Vulnerabilities</p>
            <p className="text-2xl font-bold text-white">{stats.total_vulnerabilities || vulnerabilities.length}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-500/20 rounded-lg">
              <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Active Scans</p>
            <p className="text-2xl font-bold text-white">{scans.filter((s: any) => s.status === 'running').length}</p>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white">Vulnerabilities by Severity</h3>
          <p className="text-sm text-gray-400">Distribution of discovered vulnerabilities</p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats.by_severity || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="severity" stroke="#9ca3af" fontSize={12} />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#f3f4f6'
              }} 
            />
            <Bar dataKey="count" fill="#ef4444" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Scans */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Recent Scans</h3>
              <p className="text-sm text-gray-400 mt-1">Latest security scans shared by the community</p>
            </div>
            <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">
              New Scan →
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Target</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Scan Type</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Vulnerabilities</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Started</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {scans.length > 0 ? (
                scans.map((scan: any) => (
                  <tr key={scan.id} className="hover:bg-gray-700/50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{scan.target || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 capitalize">{scan.scan_type || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{scan.vulnerabilities_found || 0}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          scan.status === 'completed'
                            ? 'bg-green-500/20 text-green-400'
                            : scan.status === 'running'
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'bg-gray-500/20 text-gray-400'
                        }`}
                      >
                        {scan.status || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {scan.started_at ? new Date(scan.started_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    No scans found. Start a new security scan!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Vulnerabilities */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Discovered Vulnerabilities</h3>
          <p className="text-sm text-gray-400 mt-1">Vulnerabilities found and shared by the community</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Vulnerability</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Target</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Discovered</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {vulnerabilities.length > 0 ? (
                vulnerabilities.map((vuln: any) => (
                  <tr key={vuln.id} className="hover:bg-gray-700/50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{vuln.title || 'Unknown'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{vuln.target || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          vuln.severity === 'critical'
                            ? 'bg-red-500/20 text-red-400'
                            : vuln.severity === 'high'
                            ? 'bg-orange-500/20 text-orange-400'
                            : vuln.severity === 'medium'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}
                      >
                        {vuln.severity || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {vuln.discovered_at ? new Date(vuln.discovered_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                    No vulnerabilities found. Share your scan results!
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

