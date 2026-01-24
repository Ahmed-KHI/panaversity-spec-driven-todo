/**
 * Chat page for AI assistant interaction - Phase III
 * [Task]: T-010
 * [From]: specs/003-phase-iii-chatbot/spec.md §9, plan.md §2.2.1
 */

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import ChatInterface from '@/components/ChatInterface';
import Link from 'next/link';

export default async function ChatPage() {
  // Check authentication via backend cookies
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;
  const backendUserCookie = cookieStore.get('user')?.value;

  if (!token || !backendUserCookie) {
    redirect('/login');
  }

  // Parse backend user
  let user: any;
  try {
    user = JSON.parse(backendUserCookie);
  } catch (e) {
    console.error('Failed to parse user cookie:', e);
    redirect('/login');
  }

  const backendUserId = user.id;
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              AI Task Assistant
            </h1>
            <p className="text-gray-600 mt-2">
              Manage your tasks through natural conversation
            </p>
          </div>
          
          <Link
            href="/dashboard"
            className="px-4 py-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            ← Back to Dashboard
          </Link>
        </div>
        
        <ChatInterface
          userId={backendUserId}
          jwtToken={token}
        />
        
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">💡 Tips:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Use natural language: "Add a task to call mom tomorrow"</li>
            <li>• Reference tasks by number: "Complete task 1"</li>
            <li>• Ask for your tasks anytime: "What tasks do I have?"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
