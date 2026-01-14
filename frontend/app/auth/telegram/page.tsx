'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

function TelegramAuthContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [linkingCode, setLinkingCode] = useState('');

  useEffect(() => {
    fetchLinkingCode();
  }, []);

  const fetchLinkingCode = async () => {
    try {
      const response = await api.get('/telegram/link-code/');
      setLinkingCode(response.data.code);
    } catch (error) {
      console.error('Failed to get linking code:', error);
    }
  };

  const handleTelegramLogin = () => {
    // Open Telegram bot
    const botUsername = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'cybershield_bot';
    window.open(`https://t.me/${botUsername}?start=${linkingCode}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#3390ec] via-[#2b7fd4] to-[#1e5a9e] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4 shadow-lg">
            <svg className="w-12 h-12 text-[#3390ec]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161l-1.87 8.8c-.134.604-.479.752-.97.467l-2.68-1.975-1.294 1.245c-.15.15-.276.276-.566.276l.201-2.853 4.96-4.48c.216-.192-.047-.298-.335-.106l-6.126 3.858-2.64-.825c-.574-.179-.59-.574.11-.87l10.35-3.99c.458-.17.858.107.708.68z"/>
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Telegram Authentication</h1>
          <p className="text-white/90">Link your Telegram account</p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Connect Telegram</h2>
            <p className="text-gray-600">Link your Telegram account to receive security alerts and notifications</p>
          </div>

          {linkingCode && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800 mb-2 font-medium">Your Linking Code:</p>
              <div className="flex items-center justify-between bg-white p-3 rounded border border-blue-300">
                <code className="text-lg font-mono text-blue-900">{linkingCode}</code>
                <button
                  onClick={() => navigator.clipboard.writeText(linkingCode)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <button
              onClick={handleTelegramLogin}
              className="w-full bg-[#3390ec] hover:bg-[#2b7fd4] text-white font-semibold py-3.5 rounded-lg transition flex items-center justify-center gap-3 shadow-lg"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161l-1.87 8.8c-.134.604-.479.752-.97.467l-2.68-1.975-1.294 1.245c-.15.15-.276.276-.566.276l.201-2.853 4.96-4.48c.216-.192-.047-.298-.335-.106l-6.126 3.858-2.64-.825c-.574-.179-.59-.574.11-.87l10.35-3.99c.458-.17.858.107.708.68z"/>
              </svg>
              <span>Open Telegram Bot</span>
            </button>

            <div className="text-center text-sm text-gray-600">
              <p className="mb-2">Steps to link your account:</p>
              <ol className="list-decimal list-inside space-y-1 text-left max-w-xs mx-auto">
                <li>Click the button above to open Telegram</li>
                <li>Start a chat with the bot</li>
                <li>Send your linking code: <code className="bg-gray-100 px-1 rounded">{linkingCode}</code></li>
                <li>Or use the /link command in the bot</li>
              </ol>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <Link
              href="/login"
              className="block text-center text-[#3390ec] hover:text-[#2b7fd4] font-medium"
            >
              ← Back to login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TelegramAuthPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-[#3390ec] via-[#2b7fd4] to-[#1e5a9e] flex items-center justify-center"><div className="text-white">Loading...</div></div>}>
      <TelegramAuthContent />
    </Suspense>
  );
}

