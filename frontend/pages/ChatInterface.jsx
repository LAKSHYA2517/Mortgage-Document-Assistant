import { useState } from 'react';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I have loaded the mortgage documents. What would you like to verify?' }
  ]);

  const handleAskQuestion = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setQuery('');
    
    // Fake loading state for visual testing
    setTimeout(() => {
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: "The Cash to Close is $45,000.",
        sources: [{ doc_type: "Closing Disclosure", score: 0.89 }]
      }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      
      {/* Header */}
      <div className="px-4 py-3 bg-white border-b border-slate-100">
        <h3 className="text-sm font-semibold text-slate-700">Underwriting Assistant</h3>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-sm' 
                : 'bg-white border border-slate-200 text-slate-700 rounded-tl-sm'
            }`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
              
              {/* Citations */}
              {msg.sources && (
                <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                  {msg.sources.map((source, sIdx) => (
                    <span key={sIdx} className="text-[11px] font-medium bg-slate-50 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-md">
                      Source: {source.doc_type}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form onSubmit={handleAskQuestion} className="relative flex items-center">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about loan amount, contingencies, or cash to close..." 
            className="w-full bg-slate-50 border border-slate-200 text-sm text-slate-800 rounded-full pl-5 pr-14 py-3.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
          />
          <button 
            type="submit" 
            className="absolute right-2 bg-indigo-600 text-white p-2 rounded-full hover:bg-indigo-700 transition-colors shadow-sm flex items-center justify-center h-9 w-9"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </form>
      </div>

    </div>
  );
}