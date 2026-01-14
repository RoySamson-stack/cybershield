'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '@/lib/api';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b'];

export default function DashboardPage() {
  const [stats, setStats] = useState<any>({});
  const [threats, setThreats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      const [threatsRes, c2Res, credentialsRes] = await Promise.all([
        api.get('/threats/threat-intelligence/').catch(() => ({ data: { results: [] } })),
        api.get('/threats/c2-servers/stats/').catch(() => ({ data: {} })),
        api.get('/threats/leaked-credentials/stats/').catch(() => ({ data: {} })),
      ]);

      setThreats(threatsRes.data.results?.slice(0, 10) || []);
      setStats({
        threats: threatsRes.data.count || 0,
        c2: c2Res.data,
        credentials: credentialsRes.data,
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart data
  const threatByType = threats.reduce((acc: any, threat: any) => {
    acc[threat.threat_type] = (acc[threat.threat_type] || 0) + 1;
    return acc;
  }, {});

  const threatChartData = Object.entries(threatByType).map(([name, value]) => ({
    name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value,
  }));

  const severityData = threats.reduce((acc: any, threat: any) => {
    acc[threat.severity] = (acc[threat.severity] || 0) + 1;
    return acc;
  }, {});

  const severityChartData = Object.entries(severityData).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  // Timeline data for area chart
  const timelineData = [
    { date: 'Mon', threats: 45, scans: 12 },
    { date: 'Tue', threats: 52, scans: 18 },
    { date: 'Wed', threats: 38, scans: 15 },
    { date: 'Thu', threats: 61, scans: 22 },
    { date: 'Fri', threats: 48, scans: 19 },
    { date: 'Sat', threats: 35, scans: 10 },
    { date: 'Sun', threats: 42, scans: 14 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Welcome back, here's what the community is sharing</p>
        </div>
        <div className="flex items-center gap-2">
          {['7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                timeRange === range
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-blue-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <span className="text-xs font-medium text-green-400 bg-green-500/20 px-2 py-1 rounded-full">+12.5%</span>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Threats</p>
            <p className="text-2xl font-bold text-white">{stats.threats?.toLocaleString() || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-purple-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-xs font-medium text-red-400 bg-red-500/20 px-2 py-1 rounded-full">-3.2%</span>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Active C2 Servers</p>
            <p className="text-2xl font-bold text-white">{stats.c2?.active || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Out of {stats.c2?.total || 0} total</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-orange-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-500/20 rounded-lg">
              <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <span className="text-xs font-medium text-orange-400 bg-orange-500/20 px-2 py-1 rounded-full">+8.1%</span>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Leaked Credentials</p>
            <p className="text-2xl font-bold text-white">{(stats.credentials?.total || 0).toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">{stats.credentials?.exposed || 0} exposed</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-green-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-xs font-medium text-green-400 bg-green-500/20 px-2 py-1 rounded-full">+24.3%</span>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Security Scans</p>
            <p className="text-2xl font-bold text-white">{stats.scans || 0}</p>
            <p className="text-xs text-gray-500 mt-1">This month</p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Timeline */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">Threat Activity</h3>
              <p className="text-sm text-gray-400">Last 7 days</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timelineData}>
              <defs>
                <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f3f4f6'
                }} 
              />
              <Area type="monotone" dataKey="threats" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorThreats)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Threats by Type */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white">Threats by Type</h3>
            <p className="text-sm text-gray-400">Distribution of threat categories</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={threatChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
              >
                {threatChartData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f3f4f6'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Second Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white">Threat Severity</h3>
            <p className="text-sm text-gray-400">Breakdown by severity level</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f3f4f6'
                }} 
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
            <p className="text-sm text-gray-400">Latest security events</p>
          </div>
          <div className="space-y-4">
            {[
              { type: 'Threat Detected', title: 'New ransomware campaign', time: '2 min ago', color: 'red' },
              { type: 'Scan Completed', title: 'Vulnerability scan finished', time: '15 min ago', color: 'green' },
              { type: 'Alert', title: 'C2 server detected', time: '1 hour ago', color: 'orange' },
              { type: 'Update', title: 'Threat intelligence updated', time: '2 hours ago', color: 'blue' },
            ].map((activity, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-700/50 transition">
                <div className={`w-2 h-2 rounded-full mt-2 bg-${activity.color}-500 flex-shrink-0`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{activity.title}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.type} • {activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Threats Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Recent Threats</h3>
              <p className="text-sm text-gray-400 mt-1">Latest threat intelligence updates</p>
            </div>
            <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">
              View All →
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
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {threats.length > 0 ? (
                threats.map((threat: any) => (
                  <tr key={threat.id} className="hover:bg-gray-700/50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(threat.first_seen || threat.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                        Active
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    No threats found
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
