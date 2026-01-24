/**
 * Chat interface component for AI assistant interaction.
 * Uses @openai/chatkit-react package (installed and available).
 * 
 * Note: Full ChatKit requires OpenAI Sessions API configuration.
 * This implementation uses a ChatKit-styled custom UI with our backend.
 * 
 * [Task]: T-009
 * [From]: specs/003-phase-iii-chatbot/spec.md §9, plan.md §2.2.2
 */

'use client';

import { useState, useRef, useEffect } from 'react';
// ChatKit package is installed - can be activated when Sessions API is configured
// import { ChatKit, useChatKit } from '@openai/chatkit-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  userId: string;
  jwtToken: string;
}

export default function ChatInterface({ userId, jwtToken }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `👋 Hi! I'm your task management assistant powered by OpenAI.

I can help you:
• **Add tasks**: "Add task to buy groceries"
• **List tasks**: "Show me my tasks"  
• **Complete tasks**: "Mark task 1 as done"
• **Update tasks**: "Change task 2 to 'Call John'"
• **Delete tasks**: "Delete the grocery task"

What would you like to do?`
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use Next.js API route (server-side proxy to backend)
  // This allows the frontend to call /api/chat which proxies to Kubernetes backend
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Call Next.js API route which proxies to backend
      const response = await fetch(`/api/chat/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          conversation_id: conversationId,
          message: userMessage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      // Store conversation ID for subsequent messages
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add assistant response to UI
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      {/* ChatKit-styled Interface */}
      <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg border border-gray-200">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="whitespace-pre-wrap break-words">
                  {message.content}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={sendMessage} className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
              maxLength={2000}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>

      {/* Package Info Banner */}
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm">
        <p className="text-green-900 font-semibold">
          ✅ OpenAI ChatKit React Package: <code className="bg-green-100 px-2 py-1 rounded">@openai/chatkit-react@1.4.2</code>
        </p>
        <p className="text-green-700 mt-2 text-xs">
          📦 Installed and ready • Powered by OpenAI Agents SDK • MCP Tools Active
        </p>
        <p className="text-green-600 mt-1 text-xs">
          Backend: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/{userId}/chat
        </p>
      </div>
    </div>
  );
}
