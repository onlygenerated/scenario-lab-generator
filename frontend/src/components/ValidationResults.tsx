import type { ValidationResult } from '../api/client';

interface ValidationResultsProps {
  results: ValidationResult[];
  allPassed: boolean;
  onBack: () => void;
  onRetry: () => void;
}

export function ValidationResults({ results, allPassed, onBack, onRetry }: ValidationResultsProps) {
  const passCount = results.filter((r) => r.passed).length;

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      {/* Summary */}
      <div className={`
        rounded-xl shadow-sm border p-6 text-center
        ${allPassed
          ? 'bg-green-50 border-green-200'
          : 'bg-white border-gray-200'
        }
      `}>
        <div className={`
          w-16 h-16 rounded-full mx-auto flex items-center justify-center mb-3
          ${allPassed ? 'bg-green-100' : 'bg-gray-100'}
        `}>
          {allPassed ? (
            <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          )}
        </div>
        <h2 className="text-xl font-semibold text-gray-900">
          {allPassed ? 'All Checks Passed!' : `${passCount} of ${results.length} Checks Passed`}
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          {allPassed
            ? 'Congratulations! Your ETL pipeline is correct.'
            : 'Review the failed checks below and try again.'
          }
        </p>
      </div>

      {/* Individual Results */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Validation Details</h3>
        <div className="space-y-3">
          {results.map((result, i) => (
            <div
              key={i}
              className={`
                flex items-start gap-3 p-3 rounded-lg border
                ${result.passed
                  ? 'bg-green-50 border-green-100'
                  : 'bg-red-50 border-red-100'
                }
              `}
            >
              <div className="mt-0.5">
                {result.passed ? (
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">{result.query_name}</p>
                {!result.passed && result.error && (
                  <p className="text-xs text-red-600 mt-1">{result.error}</p>
                )}
                {result.actual_row_count !== null && (
                  <p className="text-xs text-gray-500 mt-0.5">
                    Expected {result.expected_row_count} rows, got {result.actual_row_count}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 justify-center">
        <button
          onClick={onBack}
          className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back to Lab
        </button>
        {!allPassed && (
          <button
            onClick={onRetry}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}
