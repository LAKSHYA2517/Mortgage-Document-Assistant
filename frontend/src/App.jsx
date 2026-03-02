import PdfViewer from "../pages/pdfViewer.jsx";
import ChatInterface from '../pages/ChatInterface.jsx';

function App() {
  return (
    <div className="flex flex-col h-screen w-screen bg-slate-50 font-sans overflow-hidden">
      
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm z-10">
        <div>
          <h1 className="text-xl font-semibold text-slate-800 tracking-tight">Outamation Intelligence</h1>
          <p className="text-xs text-slate-500 mt-0.5">Mortgage Document Analysis System</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm font-medium text-slate-600">Engine Online</span>
        </div>
      </header>

      {/* Split Workspace */}
      <main className="flex flex-1 overflow-hidden p-4 gap-4">
        
        {/* Left Pane: Document */}
        <div className="w-1/2 flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <PdfViewer />
        </div>

        {/* Right Pane: Chat */}
        <div className="w-1/2 flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <ChatInterface />
        </div>

      </main>
    </div>
  );
}

export default App;
