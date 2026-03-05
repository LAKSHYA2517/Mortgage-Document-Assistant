import PdfViewer from "../pages/pdfViewer.jsx";
import ChatInterface from '../pages/ChatInterface.jsx';

function App() {
  return (
    <div className="flex flex-col h-screen w-screen bg-white font-sans overflow-hidden">
      
      {/* Top Header */}
      <header className="bg-white border-b border-slate-100 px-8 py-5 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-slate-900 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <div>
            <h1 className="text-lg font-medium text-slate-900">Mortgage Assistance</h1>
            
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5">
          <span className="flex h-2 w-2 relative">
            <span className="animate-pulse absolute inline-flex h-full w-full rounded-full bg-emerald-400"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-medium text-slate-500">Active</span>
        </div>
      </header>

      {/* Split Workspace */}
      <main className="flex flex-1 overflow-hidden p-5 gap-5">
        
        {/* Left Pane: Document */}
        <div className="w-1/2 flex flex-col bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
          <PdfViewer />
        </div>

        {/* Right Pane: Chat */}
        <div className="w-1/2 flex flex-col bg-white rounded-lg border border-slate-200 overflow-hidden">
          <ChatInterface />
        </div>

      </main>
    </div>
  );
}

export default App;
