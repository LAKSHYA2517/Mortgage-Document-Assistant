import { useState } from 'react';
import axios from 'axios';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I have loaded the mortgage documents. What would you like to verify?' }
  ]);

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // 1. Instantly display the user's message
    const currentQuery = query;
    setMessages((prev) => [...prev, { role: 'user', content: currentQuery }]);
    setQuery('');
    setIsLoading(true);

    try {
      // 2. Call your actual FastAPI backend
      const response = await axios.post('http://localhost:8000/query', {
        question: currentQuery
      });

      // 3. Display the real AI response and its sources
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources
      }]);

    } catch (error) {
      console.error("Error querying the RAG engine:", error);
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: "Error: Could not connect to the AI engine. Please ensure the backend and Ollama are running." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      
      {/* Header */}
      <div className="px-5 py-3.5 bg-white border-b border-slate-100 flex justify-between items-center">
        <h3 className="text-sm font-medium text-slate-700">Assistant</h3>
        {isLoading && (
          <span className="text-xs text-slate-500 animate-pulse">
            Processing...
          </span>
        )}
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-3.5 ${
              msg.role === 'user' 
                ? 'bg-slate-900 text-white' 
                : 'bg-slate-50 text-slate-700 border border-slate-200'
            }`}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              
              {/* Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5 border-t border-slate-200 pt-2.5">
                  {msg.sources.map((source, sIdx) => (
                    <span key={sIdx} className="text-[10px] font-medium bg-white text-slate-600 border border-slate-200 px-2 py-0.5 rounded">
                      {source.doc_type} (${((source.score * 100).toFixed(1))}%)
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-100">
        <form onSubmit={handleAskQuestion} className="relative flex items-center gap-2">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            placeholder={isLoading ? "Please wait..." : "Ask about the document..."} 
            className="flex-1 bg-slate-50 border border-slate-200 text-sm text-slate-800 rounded-lg pl-4 pr-12 py-2.5 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:border-slate-400 transition-all disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={isLoading || !query.trim()}
            className="bg-slate-900 text-white p-2 rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center h-9 w-9 disabled:bg-slate-300 disabled:cursor-not-allowed flex-shrink-0"
          >
            {isLoading ? (
              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            )}
          </button>
        </form>
      </div>

    </div>
  );
}