import { useState } from 'react';

export default function PdfViewer() {
  // Set to null initially to prevent the "Inception" loop bug!
  const [pdfUrl, setPdfUrl] = useState(null); 

  return (
    <div className="flex flex-col h-full bg-slate-50">
      
      {/* Toolbar */}
      <div className="px-4 py-3 bg-white border-b border-slate-100 flex justify-between items-center">
        <h3 className="text-sm font-semibold text-slate-700">Source Document</h3>
        <button 
          className="text-xs font-medium bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 py-1.5 px-3 rounded-md transition-colors shadow-sm"
          onClick={() => alert("File upload will trigger the FastAPI /upload endpoint!")}
        >
          Upload PDF
        </button>
      </div>

      {/* Viewer Area */}
      <div className="flex-1 w-full h-full p-2">
        {pdfUrl ? (
          <iframe 
            src={pdfUrl} 
            className="w-full h-full rounded-lg border border-slate-200 bg-white"
            title="Mortgage Document"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 bg-white rounded-lg border border-dashed border-slate-300 mx-2 mb-2">
            <svg className="w-12 h-12 mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p className="text-sm font-medium">No document loaded</p>
            <p className="text-xs mt-1">Upload a Closing Disclosure to begin</p>
          </div>
        )}
      </div>

    </div>
  );
}