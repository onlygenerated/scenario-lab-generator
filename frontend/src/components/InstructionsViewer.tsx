import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';

interface InstructionsViewerProps {
  markdown: string;
  onClose: () => void;
}

export function InstructionsViewer({ markdown, onClose }: InstructionsViewerProps) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Lab Instructions</h2>
          <button
            onClick={onClose}
            className="px-4 py-1.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Back to Lab
          </button>
        </div>
        <div className="p-6 prose prose-sm prose-gray max-w-none
          prose-headings:text-gray-900
          prose-h1:text-2xl prose-h1:font-bold prose-h1:mb-4
          prose-h2:text-lg prose-h2:font-semibold prose-h2:mt-8 prose-h2:mb-3
          prose-h3:text-base prose-h3:font-semibold prose-h3:mt-6 prose-h3:mb-2
          prose-p:text-gray-600 prose-p:leading-relaxed
          prose-li:text-gray-600
          prose-code:text-indigo-600 prose-code:bg-indigo-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:before:content-none prose-code:after:content-none
          prose-pre:bg-gray-900 prose-pre:text-gray-100
          prose-table:text-sm
          prose-th:text-left prose-th:px-3 prose-th:py-2 prose-th:bg-gray-50
          prose-td:px-3 prose-td:py-2
          prose-strong:text-gray-800
        ">
          <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
            {markdown}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
