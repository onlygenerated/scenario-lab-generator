interface LabStatusProps {
  labId: string;
  status: string;
  jupyterUrl: string | null;
  onValidate: () => void;
  onStop: () => void;
  onViewInstructions: () => void;
  loading: boolean;
}

const STATUS_CONFIG: Record<string, { color: string; label: string; animate?: boolean }> = {
  pending: { color: 'bg-gray-100 text-gray-600', label: 'Pending' },
  starting: { color: 'bg-yellow-100 text-yellow-700', label: 'Starting...', animate: true },
  running: { color: 'bg-green-100 text-green-700', label: 'Running' },
  stopping: { color: 'bg-orange-100 text-orange-700', label: 'Stopping...', animate: true },
  stopped: { color: 'bg-gray-100 text-gray-500', label: 'Stopped' },
  error: { color: 'bg-red-100 text-red-700', label: 'Error' },
};

export function LabStatus({
  labId,
  status,
  jupyterUrl,
  onValidate,
  onStop,
  onViewInstructions,
  loading,
}: LabStatusProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Lab Environment</h2>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.color}`}>
            {config.animate && (
              <span className="inline-block w-2 h-2 rounded-full bg-current mr-1.5 animate-pulse" />
            )}
            {config.label}
          </span>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Lab ID</span>
            <code className="text-gray-700 bg-white px-2 py-0.5 rounded border border-gray-200 text-xs">
              {labId}
            </code>
          </div>

          {jupyterUrl && status === 'running' && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">JupyterLab</span>
              <a
                href={jupyterUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
              >
                Open in Browser
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>

        {status === 'running' && (
          <div className="mt-6 space-y-3">
            <p className="text-sm text-gray-500">
              Your lab is running. Open JupyterLab to complete the ETL task, then validate your work.
            </p>
            <div className="flex gap-3">
              <button
                onClick={onViewInstructions}
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                View Instructions
              </button>
              <button
                onClick={onValidate}
                disabled={loading}
                className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Checking...' : 'Check My Work'}
              </button>
            </div>
            <button
              onClick={onStop}
              disabled={loading}
              className="w-full px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
            >
              Stop Lab
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
