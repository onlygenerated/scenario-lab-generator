import type { ScenarioBlueprint } from '../api/client';

interface LabWorkspaceProps {
  blueprint: ScenarioBlueprint;
  labId: string | null;
  status: string;
  jupyterUrl: string | null;
  onValidate: () => void;
  onStop: () => void;
  launching: boolean;
  onAutoLaunch: () => void;
  loading: boolean;
}

const STATUS_CONFIG: Record<string, { color: string; label: string; animate?: boolean }> = {
  pending: { color: 'bg-stone-100 text-stone-600', label: 'Pending' },
  starting: { color: 'bg-yellow-100 text-yellow-700', label: 'Starting...', animate: true },
  running: { color: 'bg-green-100 text-green-700', label: 'Running' },
  stopping: { color: 'bg-orange-100 text-orange-700', label: 'Stopping...', animate: true },
  stopped: { color: 'bg-stone-100 text-stone-500', label: 'Stopped' },
  error: { color: 'bg-red-100 text-red-700', label: 'Error' },
};

export function LabWorkspace({
  blueprint,
  labId,
  status,
  jupyterUrl,
  onValidate,
  onStop,
  launching,
  onAutoLaunch,
  loading,
}: LabWorkspaceProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Blueprint Header */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-stone-900">{blueprint.title}</h2>
            <p className="text-sm text-stone-500 mt-1">{blueprint.description}</p>
          </div>
          <span className={`
            px-3 py-1 rounded-full text-xs font-semibold capitalize
            ${blueprint.difficulty === 'beginner' ? 'bg-green-100 text-green-700' :
              blueprint.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'}
          `}>
            {blueprint.difficulty}
          </span>
        </div>

        <div className="flex gap-6 mt-4 text-sm text-stone-600">
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {blueprint.estimated_minutes} min
          </div>
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z" />
            </svg>
            {blueprint.source_tables.length} source → {blueprint.target_tables.length} target
          </div>
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {blueprint.transformation_steps.length} steps
          </div>
        </div>
      </div>

      {/* Lab Controls — sticky */}
      <div className="sticky top-0 z-10 pt-2 pb-3">
        <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-4">
          {labId ? (
            <>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-semibold text-stone-900">
                    Lab: <code className="text-sm bg-stone-100 px-2 py-0.5 rounded border border-stone-200">{labId}</code>
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
                      className="px-4 py-2 bg-teal-600 text-white rounded-md text-sm font-semibold hover:bg-teal-500 active:bg-teal-700 transition-colors flex items-center gap-1.5 shadow-[0_2px_0_0_rgba(0,0,0,0.2)] active:shadow-none active:translate-y-[1px]"
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
                    className="px-4 py-2 bg-green-600 text-white rounded-md text-sm font-semibold hover:bg-green-700 disabled:opacity-50 transition-colors shadow-[0_2px_0_0_rgba(0,0,0,0.2)] active:shadow-none active:translate-y-[1px]"
                  >
                    {loading ? 'Checking...' : 'Check My Work'}
                  </button>
                  <button
                    onClick={onStop}
                    disabled={loading}
                    className="px-4 py-2 border border-red-200 text-red-600 rounded-md text-sm font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
                  >
                    Stop Lab
                  </button>
                </div>
              )}
            </>
          ) : launching ? (
            <div className="flex items-center gap-3 py-1">
              <p className="text-sm text-stone-500 font-mono">
                starting lab environment<span className="animate-pulse">_</span>
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <p className="text-sm text-stone-500">Lab environment is not running.</p>
              <button
                onClick={onAutoLaunch}
                className="px-4 py-2 bg-teal-600 text-white rounded-md text-sm font-semibold hover:bg-teal-500 active:bg-teal-700 transition-colors shadow-[0_2px_0_0_rgba(0,0,0,0.2)] active:shadow-none active:translate-y-[1px]"
              >
                Launch Lab
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Learning Objectives */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Learning Objectives</h3>
        <ul className="space-y-1.5">
          {blueprint.learning_objectives.map((obj, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-stone-600">
              <svg className="w-4 h-4 text-teal-500 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              {obj}
            </li>
          ))}
        </ul>
      </div>

      {/* Business Context */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Business Context</h3>
        <p className="text-sm text-stone-600 leading-relaxed">{blueprint.business_context}</p>
      </div>

      {/* Database Connections */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Database Connections</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-stone-50 rounded-lg p-3 border border-stone-100">
            <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">Source</span>
            <p className="text-sm text-stone-700 font-mono mt-1">source-db:5432/source_db</p>
            <p className="text-xs text-stone-500 mt-0.5">labuser / labpass</p>
          </div>
          <div className="bg-stone-50 rounded-lg p-3 border border-stone-100">
            <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">Target</span>
            <p className="text-sm text-stone-700 font-mono mt-1">target-db:5432/target_db</p>
            <p className="text-xs text-stone-500 mt-0.5">labuser / labpass</p>
          </div>
        </div>
      </div>

      {/* Source Tables */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Source Tables</h3>
        <div className="space-y-4">
          {blueprint.source_tables.map((table) => (
            <div key={table.table_name} className="border border-stone-100 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <code className="text-sm font-semibold text-teal-600 bg-teal-50 px-2 py-0.5 rounded">
                  {table.table_name}
                </code>
                <span className="text-xs text-stone-500">
                  {table.columns.length} columns, {table.sample_data.length} rows
                </span>
              </div>
              <p className="text-xs text-stone-500 mb-2">{table.description}</p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="border-b border-stone-100">
                      {table.columns.map((col) => (
                        <th key={col.name} className="text-left py-1.5 px-2 text-stone-500 font-medium">
                          {col.name}
                          <span className="text-stone-400 ml-1 font-normal">{col.data_type}</span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {table.sample_data.slice(0, 5).map((row, i) => (
                      <tr key={i} className="border-b border-stone-50">
                        {table.columns.map((col) => (
                          <td key={col.name} className="py-1 px-2 text-stone-600 font-mono">
                            {row[col.name] === null ? (
                              <span className="text-stone-300 italic">NULL</span>
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
                  <p className="text-xs text-stone-500 mt-1 px-2">
                    ... and {table.sample_data.length - 5} more rows
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Target Table */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Target Table</h3>
        <div className="space-y-4">
          {blueprint.target_tables.map((table) => (
            <div key={table.table_name} className="border border-stone-100 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <code className="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  {table.table_name}
                </code>
              </div>
              <p className="text-xs text-stone-500 mb-2">{table.description}</p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="border-b border-stone-100">
                      <th className="text-left py-1.5 px-2 text-stone-500 font-medium">Column</th>
                      <th className="text-left py-1.5 px-2 text-stone-500 font-medium">Type</th>
                      <th className="text-left py-1.5 px-2 text-stone-500 font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns.map((col) => (
                      <tr key={col.name} className="border-b border-stone-50">
                        <td className="py-1.5 px-2 text-stone-700 font-mono font-medium">{col.name}</td>
                        <td className="py-1.5 px-2 text-stone-500 font-mono">{col.data_type}</td>
                        <td className="py-1.5 px-2 text-stone-500">{col.description}</td>
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
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3">Transformation Steps</h3>
        <ol className="space-y-3">
          {blueprint.transformation_steps.map((step) => (
            <li key={step.step_number} className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5">
                {step.step_number}
              </div>
              <div>
                <p className="text-sm font-medium text-stone-800">{step.title}</p>
                <p className="text-xs text-stone-500 mt-0.5">{step.description}</p>
                {step.hint && (
                  <p className="text-xs text-teal-600 mt-1 font-mono bg-teal-50 px-2 py-1 rounded">
                    Hint: {step.hint}
                  </p>
                )}
                {step.skill_tags.length > 0 && (
                  <div className="flex gap-1 mt-1.5">
                    {step.skill_tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-stone-100 text-stone-500 rounded text-[10px] font-medium font-mono">
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
