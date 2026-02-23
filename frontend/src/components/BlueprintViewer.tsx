import type { ScenarioBlueprint } from '../api/client';

interface BlueprintViewerProps {
  blueprint: ScenarioBlueprint;
  onLaunch: () => void;
  onBack: () => void;
  loading: boolean;
}

export function BlueprintViewer({ blueprint, onLaunch, onBack, loading }: BlueprintViewerProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{blueprint.title}</h2>
            <p className="text-sm text-gray-500 mt-1">{blueprint.description}</p>
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

        <div className="flex gap-6 mt-4 text-sm text-gray-600">
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

      {/* Learning Objectives */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Learning Objectives</h3>
        <ul className="space-y-1.5">
          {blueprint.learning_objectives.map((obj, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
              <svg className="w-4 h-4 text-indigo-500 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              {obj}
            </li>
          ))}
        </ul>
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

      {/* Actions */}
      <div className="flex gap-3 justify-center">
        <button
          onClick={onBack}
          className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={onLaunch}
          disabled={loading}
          className="px-8 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Launching...' : 'Launch Lab'}
        </button>
      </div>
    </div>
  );
}
