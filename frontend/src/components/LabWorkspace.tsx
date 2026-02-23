import type { ScenarioBlueprint } from '../api/client';

interface LabWorkspaceProps {
  blueprint: ScenarioBlueprint;
  labId: string;
  status: string;
  jupyterUrl: string | null;
  onValidate: () => void;
  onStop: () => void;
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

export function LabWorkspace({
  blueprint,
  labId,
  status,
  jupyterUrl,
  onValidate,
  onStop,
  loading,
}: LabWorkspaceProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Lab Controls — sticky */}
      <div className="sticky top-0 z-10 bg-gray-50 pt-2 pb-3">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold text-gray-900">
                Lab: <code className="text-sm bg-gray-100 px-2 py-0.5 rounded border border-gray-200">{labId}</code>
              </h2>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.color}`}>
                {config.animate && (
                  <span className="inline-block w-2 h-2 rounded-full bg-current mr-1.5 animate-pulse" />
                )}
                {config.label}
              </span>
            </div>
          </div>

          {status === 'running' && (
            <div className="flex items-center gap-3">
              {jupyterUrl && (
                <a
                  href={jupyterUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-1.5"
                >
                  Open JupyterLab
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              )}
              <button
                onClick={onValidate}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Checking...' : 'Check My Work'}
              </button>
              <button
                onClick={onStop}
                disabled={loading}
                className="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
              >
                Stop Lab
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Business Context */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Business Context</h3>
        <p className="text-sm text-gray-600 leading-relaxed">{blueprint.business_context}</p>
      </div>

      {/* Database Connections */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Database Connections</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Source</span>
            <p className="text-sm text-gray-700 font-mono mt-1">source-db:5432/source_db</p>
            <p className="text-xs text-gray-400 mt-0.5">labuser / labpass</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Target</span>
            <p className="text-sm text-gray-700 font-mono mt-1">target-db:5432/target_db</p>
            <p className="text-xs text-gray-400 mt-0.5">labuser / labpass</p>
          </div>
        </div>
      </div>

      {/* Source Tables */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Source Tables</h3>
        <div className="space-y-4">
          {blueprint.source_tables.map((table) => (
            <div key={table.table_name} className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <code className="text-sm font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                  {table.table_name}
                </code>
                <span className="text-xs text-gray-400">
                  {table.columns.length} columns, {table.sample_data.length} rows
                </span>
              </div>
              <p className="text-xs text-gray-500 mb-2">{table.description}</p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-100">
                      {table.columns.map((col) => (
                        <th key={col.name} className="text-left py-1.5 px-2 text-gray-500 font-medium">
                          {col.name}
                          <span className="text-gray-300 ml-1 font-normal">{col.data_type}</span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {table.sample_data.slice(0, 5).map((row, i) => (
                      <tr key={i} className="border-b border-gray-50">
                        {table.columns.map((col) => (
                          <td key={col.name} className="py-1 px-2 text-gray-600 font-mono">
                            {row[col.name] === null ? (
                              <span className="text-gray-300 italic">NULL</span>
                            ) : (
                              String(row[col.name])
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {table.sample_data.length > 5 && (
                  <p className="text-xs text-gray-400 mt-1 px-2">
                    ... and {table.sample_data.length - 5} more rows
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Target Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Target Table</h3>
        <div className="space-y-4">
          {blueprint.target_tables.map((table) => (
            <div key={table.table_name} className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <code className="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  {table.table_name}
                </code>
              </div>
              <p className="text-xs text-gray-500 mb-2">{table.description}</p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-1.5 px-2 text-gray-500 font-medium">Column</th>
                      <th className="text-left py-1.5 px-2 text-gray-500 font-medium">Type</th>
                      <th className="text-left py-1.5 px-2 text-gray-500 font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns.map((col) => (
                      <tr key={col.name} className="border-b border-gray-50">
                        <td className="py-1.5 px-2 text-gray-700 font-mono font-medium">{col.name}</td>
                        <td className="py-1.5 px-2 text-gray-500 font-mono">{col.data_type}</td>
                        <td className="py-1.5 px-2 text-gray-500">{col.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Transformation Steps */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Transformation Steps</h3>
        <ol className="space-y-3">
          {blueprint.transformation_steps.map((step) => (
            <li key={step.step_number} className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5">
                {step.step_number}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">{step.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>
                {step.hint && (
                  <p className="text-xs text-indigo-500 mt-1 font-mono bg-indigo-50 px-2 py-1 rounded">
                    Hint: {step.hint}
                  </p>
                )}
                {step.skill_tags.length > 0 && (
                  <div className="flex gap-1 mt-1.5">
                    {step.skill_tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-[10px] font-medium">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
