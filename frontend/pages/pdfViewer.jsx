import { useState, useRef } from 'react';
import axios from 'axios';

export default function PdfViewer() {
  const [pdfUrl, setPdfUrl] = useState(null); 
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 1. Instantly show the PDF in the UI using a local browser blob URL
    const localUrl = URL.createObjectURL(file);
    setPdfUrl(localUrl);
    setIsUploading(true);

    // 2. Send the file to your FastAPI backend to be parsed and vectorized
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert(`Success: ${response.data.message}`);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Error uploading document to the AI engine.");
      setPdfUrl(null); // Reset if upload fails
    } finally {
      setIsUploading(false);
      // Reset the input so you can upload the same file again if needed
      if (fileInputRef.current) fileInputRef.current.value = ''; 
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50">
      
      {/* Hidden File Input */}
      <input 
        type="file" 
        accept="application/pdf" 
        ref={fileInputRef} 
        onChange={handleFileUpload} 
        className="hidden" 
      />

      <div className="px-5 py-3.5 bg-white border-b border-slate-100 flex justify-between items-center">
        <h3 className="text-sm font-medium text-slate-700">Document</h3>
        <button 
          className="text-xs font-medium bg-slate-900 text-white hover:bg-slate-800 py-2 px-3 rounded-lg transition-colors disabled:opacity-60"
          onClick={() => fileInputRef.current.click()}
          disabled={isUploading}
        >
          {isUploading ? 'Ingesting...' : 'Upload PDF'}
        </button>
      </div>

      <div className="flex-1 w-full h-full p-3">
        {pdfUrl ? (
          <iframe 
            src={pdfUrl} 
            className="w-full h-full rounded-lg border border-slate-200 bg-white"
            title="Mortgage Document"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 bg-white rounded-lg border border-slate-200">
            <svg className="w-10 h-10 mb-2.5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p className="text-sm font-medium text-slate-700">No document loaded</p>
            <p className="text-xs text-slate-500 mt-1">Upload a PDF to begin analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}