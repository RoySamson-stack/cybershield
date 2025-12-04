'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full bg-gray-900/95 backdrop-blur-md ${scrollY > 50 ? 'shadow-lg border-b border-gray-800' : ''} z-50 transition-all`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                CyberShield
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-400 hover:text-white font-medium transition">Features</a>
              <a href="#community" className="text-gray-400 hover:text-white font-medium transition">Community</a>
              <a href="#about" className="text-gray-400 hover:text-white font-medium transition">About</a>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-gray-400 hover:text-white px-4 py-2 rounded-lg text-sm font-medium transition"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-xl"
              >
                Join Community
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-400 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
              New: Enhanced Threat Sharing & Discussion Features
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              The Cybersecurity
              <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
                Community Platform
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-10 leading-relaxed max-w-2xl mx-auto">
              Share threat intelligence, track ransomware groups, discuss breaches, and collaborate with 
              cybersecurity professionals worldwide. The most sophisticated platform for threat intelligence sharing.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition shadow-xl hover:shadow-2xl hover:scale-105"
              >
                Join the Community
              </Link>
              <Link
                href="/login"
                className="bg-gray-800 hover:bg-gray-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition border-2 border-gray-700 shadow-lg hover:border-gray-600"
              >
                Browse Threats
              </Link>
            </div>
            
            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center items-center gap-8 text-sm">
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-8 h-8 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="font-medium">10K+ Members</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="font-medium">Real-time Updates</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="font-medium">Secure & Private</span>
              </div>
            </div>
          </div>

          {/* Platform Preview */}
          <div className="mt-16 rounded-2xl shadow-2xl border border-gray-800 overflow-hidden bg-gray-800 transform hover:scale-[1.01] transition-transform duration-300">
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-4 border-b border-gray-700 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <div className="ml-4 text-sm text-gray-400 font-medium">cybershield.io</div>
            </div>
            <div className="p-8 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500/50 transition">
                    <div className="h-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded w-3/4 mb-2"></div>
                    <div className="h-8 bg-gradient-to-r from-blue-500/50 to-purple-500/50 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 h-48 hover:border-blue-500/50 transition">
                  <div className="h-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded w-1/2 mb-4"></div>
                  <div className="space-y-2">
                    <div className="h-2 bg-gradient-to-r from-blue-500/50 to-blue-400/50 rounded w-full"></div>
                    <div className="h-2 bg-gradient-to-r from-purple-500/50 to-purple-400/50 rounded w-5/6"></div>
                    <div className="h-2 bg-gradient-to-r from-blue-500/50 to-blue-400/50 rounded w-4/6"></div>
                  </div>
                </div>
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 h-48 hover:border-purple-500/50 transition">
                  <div className="h-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded w-1/2 mb-4"></div>
                  <div className="space-y-2">
                    <div className="h-2 bg-gradient-to-r from-purple-500/50 to-purple-400/50 rounded w-full"></div>
                    <div className="h-2 bg-gradient-to-r from-blue-500/50 to-blue-400/50 rounded w-5/6"></div>
                    <div className="h-2 bg-gradient-to-r from-purple-500/50 to-purple-400/50 rounded w-4/6"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Share & Track Threat Intelligence</h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              A sophisticated platform for cybersecurity professionals to share, discuss, and track threats
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: 'Ransomware Groups',
                description: 'Track and share information about ransomware groups, their activities, leak sites, and victim data.',
                color: 'from-red-500 to-pink-500',
                icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
              },
              {
                title: 'Data Breaches',
                description: 'Share and discuss data breaches, exposed credentials, and compromised organizations.',
                color: 'from-orange-500 to-red-500',
                icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
              },
              {
                title: 'Onion Sites & Dark Web',
                description: 'Monitor and share findings from dark web sites, forums, and marketplaces.',
                color: 'from-purple-500 to-indigo-500',
                icon: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9',
              },
              {
                title: 'C2 Infrastructure',
                description: 'Share and track command and control servers, malware families, and infrastructure.',
                color: 'from-blue-500 to-cyan-500',
                icon: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01',
              },
              {
                title: 'Leaked Credentials',
                description: 'Search and share information about exposed credentials and data dumps.',
                color: 'from-green-500 to-emerald-500',
                icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
              },
              {
                title: 'Community Discussions',
                description: 'Engage in discussions, share insights, and collaborate with cybersecurity experts.',
                color: 'from-yellow-500 to-orange-500',
                icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-xl transition-all hover:-translate-y-1 group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={feature.icon} />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '10M+', label: 'Threats Shared', color: 'text-blue-400', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
              { value: '50K+', label: 'Community Members', color: 'text-purple-400', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
              { value: '24/7', label: 'Real-time Updates', color: 'text-green-400', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
              { value: '100+', label: 'Daily Posts', color: 'text-orange-400', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
            ].map((stat, idx) => (
              <div key={idx} className="text-center bg-gray-900 rounded-xl p-6 border border-gray-700 hover:border-blue-500/50 transition">
                <div className="flex justify-center mb-3">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color.replace('text-', 'from-').replace('-400', '-500/20')} border border-${stat.color.replace('text-', '')}/30 flex items-center justify-center`}>
                    <svg className={`w-6 h-6 ${stat.color}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={stat.icon} />
                    </svg>
                  </div>
                </div>
                <div className={`text-4xl font-bold ${stat.color} mb-2`}>
                  {stat.value}
                </div>
                <div className="text-gray-400 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Join the Cybersecurity Community</h2>
          <p className="text-xl text-blue-100 mb-8">
            Start sharing threat intelligence and collaborating with experts today.
          </p>
          <Link
            href="/register"
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition shadow-2xl hover:shadow-3xl hover:scale-105"
          >
            Join Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-950 text-gray-400 py-12 px-4 sm:px-6 lg:px-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-bold text-lg mb-4">CyberShield</h3>
              <p className="text-sm">The cybersecurity community platform for sharing threat intelligence and collaborating with experts.</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition">Features</a></li>
                <li><a href="#community" className="hover:text-white transition">Community</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Community</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#about" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Guidelines</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
            <p>&copy; 2024 CyberShield. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
