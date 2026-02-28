export type WorkflowStep =
  | 'CONFIGURE'
  | 'GENERATE'
  | 'LAB'
  | 'RESULTS';

const STEPS: { key: WorkflowStep; number: string; label: string }[] = [
  { key: 'CONFIGURE', number: '01', label: 'configure' },
  { key: 'GENERATE', number: '02', label: 'generate' },
  { key: 'LAB', number: '03', label: 'lab' },
  { key: 'RESULTS', number: '04', label: 'results' },
];

interface StepIndicatorProps {
  currentStep: WorkflowStep;
}

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  const currentIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <nav className="flex items-center justify-center gap-0 mb-8 font-mono text-xs tracking-wide">
      {STEPS.map((step, i) => {
        const isActive = i === currentIndex;
        const isCompleted = i < currentIndex;

        return (
          <div key={step.key} className="flex items-center">
            <span
              className={`
                px-1
                ${isActive
                  ? 'text-teal-600 border-b border-teal-500'
                  : isCompleted
                    ? 'text-stone-500'
                    : 'text-stone-400'
                }
              `}
            >
              {isCompleted && (
                <svg className="w-3 h-3 inline-block mr-0.5 -mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {step.number} {step.label}
            </span>
            {i < STEPS.length - 1 && (
              <span className={`mx-2 ${i < currentIndex ? 'text-stone-500' : 'text-stone-400'}`}>
                ———
              </span>
            )}
          </div>
        );
      })}
    </nav>
  );
}
