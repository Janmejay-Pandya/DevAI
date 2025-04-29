import React, { useEffect, useState } from 'react';
import axios from 'axios';

const PreviewPage = () => {
  const [htmlCode, setHtmlCode] = useState('');
  const [cssCode, setCssCode] = useState('');
  const [activeTab, setActiveTab] = useState('html');

  const colors = JSON.parse(localStorage.getItem('selected-colors')) || ['#aabbcc'];
  const title = localStorage.getItem('website-title') || 'My Website';

  useEffect(() => {
    const fetchGeneratedCode = async () => {
      try {
        const response = await axios.post('/api/generate_website_code/', {
          colors: colors,
          theme: title
        });

        const fullHtml = response.data.htmlCode;

        // Extract CSS part separately
        const cssMatch = fullHtml.match(/<style>([\s\S]*?)<\/style>/);
        const extractedCss = cssMatch ? cssMatch[1].trim() : '';

        // Remove style tag from HTML
        const cleanHtml = fullHtml.replace(/<style>[\s\S]*?<\/style>/, '');

        setHtmlCode(cleanHtml.trim());
        setCssCode(extractedCss);
      } catch (error) {
        console.error('Error generating website code:', error);
      }
    };

    fetchGeneratedCode();
  }, [colors, title]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-4 text-center">{title} - Preview</h1>

      <div className="flex flex-1 gap-4">
        {/* Left: Code Section */}
        <div className="w-1/2 bg-white shadow-md rounded-lg p-4 flex flex-col">
          {/* Tabs */}
          <div className="flex mb-4 border-b">
            <button
              className={`px-4 py-2 text-sm font-semibold ${activeTab === 'html' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('html')}
            >
              page.html
            </button>
            <button
              className={`px-4 py-2 text-sm font-semibold ${activeTab === 'css' ? 'border-b-2 border-green-500' : ''}`}
              onClick={() => setActiveTab('css')}
            >
              page.css
            </button>
          </div>

          {/* Code Area */}
          <div className="flex-1 overflow-auto">
            <pre className="bg-gray-900 text-white p-4 rounded-lg text-sm">
              {activeTab === 'html' ? htmlCode : cssCode}
            </pre>
          </div>
        </div>

        {/* Right: Live Preview */}
        <div className="w-1/2 bg-white shadow-md rounded-lg p-4">
          <iframe
            title="Website Preview"
            srcDoc={`<style>${cssCode}</style>${htmlCode}`}
            className="w-full h-full rounded-lg border"
          />
        </div>
      </div>
    </div>
  );
};

export default PreviewPage;
