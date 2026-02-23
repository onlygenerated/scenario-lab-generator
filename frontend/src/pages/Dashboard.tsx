import { useState } from 'react';
import { api } from '../api/client';
import type { GenerateRequest, ScenarioBlueprint, ValidationResult } from '../api/client';
import { StepIndicator } from '../components/StepIndicator';
import type { WorkflowStep } from '../components/StepIndicator';
import { ScenarioForm } from '../components/ScenarioForm';
import { BlueprintViewer } from '../components/BlueprintViewer';
import { LabWorkspace } from '../components/LabWorkspace';
import { ValidationResults } from '../components/ValidationResults';

export function Dashboard() {
  const [step, setStep] = useState<WorkflowStep>('CONFIGURE');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [blueprint, setBlueprint] = useState<ScenarioBlueprint | null>(null);
  const [labId, setLabId] = useState<string | null>(null);
  const [labStatus, setLabStatus] = useState<string>('pending');
  const [jupyterUrl, setJupyterUrl] = useState<string | null>(null);
  const [validationResults, setValidationResults] = useState<ValidationResult[] | null>(null);
  const [allPassed, setAllPassed] = useState(false);

  // Pre-launched lab from self-test (reused on "Launch Lab")
  const [prelaunchedLabId, setPrelaunchedLabId] = useState<string | null>(null);
  const [prelaunchedJupyterUrl, setPrelaunchedJupyterUrl] = useState<string | null>(null);

  const runSelfTest = async (bp: ScenarioBlueprint) => {
    setStep('SELF_TESTING');
    try {
      const result = await api.selfTest(bp);
      if (result.passed && result.lab_id) {
        setPrelaunchedLabId(result.lab_id);
        setPrelaunchedJupyterUrl(result.jupyter_url);
        setStep('REVIEW');
      } else {
        setError(result.error || 'Self-test failed — scenario may have bugs');
        setStep('CONFIGURE');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Self-test failed');
      setStep('CONFIGURE');
    }
  };

  const handleGenerate = async (request: GenerateRequest) => {
    setLoading(true);
    setError(null);
    setStep('GENERATING');
    try {
      const response = await api.generateScenario(request);
      setBlueprint(response.blueprint);
      await runSelfTest(response.blueprint);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed');
      setStep('CONFIGURE');
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setLoading(true);
    setError(null);
    setStep('GENERATING');
    try {
      const response = await api.getDemoBlueprint();
      setBlueprint(response.blueprint);
      await runSelfTest(response.blueprint);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load demo');
      setStep('CONFIGURE');
    } finally {
      setLoading(false);
    }
  };

  const handleLaunch = async () => {
    if (!blueprint) return;

    // If we have a pre-launched lab from self-test, reuse it (instant)
    if (prelaunchedLabId) {
      setLabId(prelaunchedLabId);
      setLabStatus('running');
      setJupyterUrl(prelaunchedJupyterUrl);
      setPrelaunchedLabId(null);
      setPrelaunchedJupyterUrl(null);
      setStep('RUNNING');
      return;
    }

    // Fallback: normal launch (no self-test ran, or self-test lab was cleaned up)
    setLoading(true);
    setError(null);
    setStep('LAUNCHING');
    try {
      const response = await api.launchLab(blueprint);
      setLabId(response.lab_id);
      setLabStatus(response.status);
      setJupyterUrl(response.jupyter_url);
      setStep('RUNNING');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Launch failed');
      setStep('REVIEW');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!labId) return;
    setLoading(true);
    setError(null);
    setStep('VALIDATING');
    try {
      const response = await api.validateLab(labId);
      setValidationResults(response.results);
      setAllPassed(response.all_passed);
      setStep('RESULTS');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Validation failed');
      setStep('RUNNING');
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    if (!labId) return;
    setLoading(true);
    try {
      await api.stopLab(labId);
      setLabStatus('stopped');
      setLabId(null);
      setJupyterUrl(null);
      setStep('CONFIGURE');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Stop failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    // Clean up pre-launched lab if it exists
    if (prelaunchedLabId) {
      try {
        await api.stopLab(prelaunchedLabId);
      } catch {
        // Best effort cleanup
      }
    }

    setStep('CONFIGURE');
    setBlueprint(null);
    setLabId(null);
    setLabStatus('pending');
    setJupyterUrl(null);
    setValidationResults(null);
    setAllPassed(false);
    setError(null);
    setPrelaunchedLabId(null);
    setPrelaunchedJupyterUrl(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">ScenarioLab</h1>
            <p className="text-xs text-gray-400">AI-Powered Data Pipeline Training</p>
          </div>
          {step !== 'CONFIGURE' && (
            <button
              onClick={handleReset}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Start Over
            </button>
          )}
        </div>
      </header>

      {/* Step Indicator */}
      <div className="max-w-5xl mx-auto px-6 pt-6">
        <StepIndicator currentStep={step} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="max-w-5xl mx-auto px-6 mb-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <svg className="w-5 h-5 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-red-700 flex-1">{error}</p>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 pb-12">
        {/* Loading overlay for generating/self-testing/launching/validating */}
        {(step === 'GENERATING' || step === 'SELF_TESTING' || step === 'LAUNCHING' || step === 'VALIDATING') && loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-10 h-10 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
            <p className="text-sm text-gray-500">
              {step === 'GENERATING' && 'Generating your scenario...'}
              {step === 'SELF_TESTING' && 'Testing scenario...'}
              {step === 'LAUNCHING' && 'Starting lab environment...'}
              {step === 'VALIDATING' && 'Checking your work...'}
            </p>
          </div>
        )}

        {/* Configure */}
        {step === 'CONFIGURE' && (
          <ScenarioForm
            onGenerate={handleGenerate}
            onDemo={handleDemo}
            loading={loading}
            demoMode={true}
          />
        )}

        {/* Review */}
        {step === 'REVIEW' && blueprint && (
          <BlueprintViewer
            blueprint={blueprint}
            onLaunch={handleLaunch}
            onBack={handleReset}
            loading={loading}
          />
        )}

        {/* Running */}
        {step === 'RUNNING' && labId && blueprint && (
          <LabWorkspace
            blueprint={blueprint}
            labId={labId}
            status={labStatus}
            jupyterUrl={jupyterUrl}
            onValidate={handleValidate}
            onStop={handleStop}
            loading={loading}
          />
        )}

        {/* Results */}
        {step === 'RESULTS' && validationResults && (
          <ValidationResults
            results={validationResults}
            allPassed={allPassed}
            onBack={() => setStep('RUNNING')}
            onRetry={() => setStep('RUNNING')}
          />
        )}
      </main>
    </div>
  );
}
