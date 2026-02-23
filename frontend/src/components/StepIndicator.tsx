export type WorkflowStep =
  | 'CONFIGURE'
  | 'GENERATING'
  | 'REVIEW'
  | 'LAUNCHING'
  | 'RUNNING'
  | 'VALIDATING'
  | 'RESULTS';

const STEPS: { key: WorkflowStep; label: string }[] = [
  { key: 'CONFIGURE', label: 'Configure' },
  { key: 'GENERATING', label: 'Generate' },
  { key: 'REVIEW', label: 'Review' },
  { key: 'LAUNCHING', label: 'Launch' },
  { key: 'RUNNING', label: 'Lab' },
  { key: 'VALIDATING', label: 'Validate' },
  { key: 'RESULTS', label: 'Results' },
];

interface StepIndicatorProps {
  currentStep: WorkflowStep;
}

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  const currentIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <nav className="flex items-center justify-center gap-1 mb-8">
      {STEPS.map((step, i) => {
        const isActive = i === currentIndex;
        const isCompleted = i < currentIndex;

        return (
          <div key={step.key} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold
                  transition-colors duration-200
                  ${isActive
                    ? 'bg-indigo-600 text-white'
                    : isCompleted
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'bg-gray-100 text-gray-400'
                  }
                `}
              >
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  i + 1
                )}
              </div>
              <span
                className={`
                  text-[10px] mt-1 font-medium
                  ${isActive ? 'text-indigo-600' : isCompleted ? 'text-indigo-500' : 'text-gray-400'}
                `}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={`
                  w-8 h-0.5 mx-1 mt-[-12px]
                  ${i < currentIndex ? 'bg-indigo-300' : 'bg-gray-200'}
                `}
              />
            )}
          </div>
        );
      })}
    </nav>
  );
}
