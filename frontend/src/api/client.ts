const API_BASE = '/api';

// Self-test and generation can take 2-5 minutes; browser default (~60-90s) is too short.
const FETCH_TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `HTTP ${response.status}`);
    }
    return response.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('Request timed out — the server may still be working. Check the labs list.');
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Types matching backend API models
export interface GenerateRequest {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  num_source_tables: number;
  focus_skills: string[];
  industry: string;
  include_solutions?: boolean;
}

export interface ColumnDefinition {
  name: string;
  data_type: string;
  nullable: boolean;
  is_primary_key: boolean;
  description: string;
}

export interface SourceTable {
  table_name: string;
  description: string;
  columns: ColumnDefinition[];
  sample_data: Record<string, unknown>[];
}

export interface TargetTable {
  table_name: string;
  description: string;
  columns: ColumnDefinition[];
}

export interface TransformationStep {
  step_number: number;
  title: string;
  description: string;
  hint: string;
  solution_code: string;
  skill_tags: string[];
}

export interface ValidationQuery {
  query_name: string;
  sql: string;
  expected_row_count: number;
  expected_columns: string[];
  description: string;
}

export interface ScenarioBlueprint {
  title: string;
  description: string;
  difficulty: string;
  estimated_minutes: number;
  learning_objectives: string[];
  business_context: string;
  source_tables: SourceTable[];
  target_tables: TargetTable[];
  transformation_steps: TransformationStep[];
  validation_queries: ValidationQuery[];
  lab_instructions: string;
  success_epilogue?: string;
  failure_epilogue?: string;
}

export interface FeedbackItem {
  query_name: string;
  diagnosis: string;
  suggestion: string;
}

export interface ValidationResult {
  query_name: string;
  passed: boolean;
  expected_row_count: number;
  actual_row_count: number | null;
  expected_columns: string[];
  actual_columns: string[] | null;
  error: string | null;
  feedback: FeedbackItem | null;
}

export interface SelfTestResponse {
  passed: boolean;
  lab_id: string | null;
  jupyter_url: string | null;
  validation_results: ValidationResult[];
  error: string | null;
}

export const api = {
  getDemoBlueprint: () =>
    fetchJson<{ blueprint: ScenarioBlueprint }>('/demos/blueprint'),

  generateScenario: (request: GenerateRequest) =>
    fetchJson<{ blueprint: ScenarioBlueprint }>('/scenarios/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  selfTest: (blueprint: ScenarioBlueprint, include_solutions = true) =>
    fetchJson<SelfTestResponse>('/scenarios/self-test', {
      method: 'POST',
      body: JSON.stringify({ blueprint, include_solutions }),
    }),

  launchLab: (blueprint: ScenarioBlueprint) =>
    fetchJson<{ lab_id: string; status: string; jupyter_url: string | null }>('/labs/launch', {
      method: 'POST',
      body: JSON.stringify({ blueprint }),
    }),

  getLabStatus: (labId: string) =>
    fetchJson<{ lab_id: string; status: string; jupyter_url: string | null; error_message: string | null }>(`/labs/${labId}`),

  validateLab: (labId: string) =>
    fetchJson<{ lab_id: string; all_passed: boolean; results: ValidationResult[] }>(`/labs/${labId}/validate`, {
      method: 'POST',
    }),

  getFeedback: (labId: string) =>
    fetchJson<{ lab_id: string; feedback: FeedbackItem[] }>(`/labs/${labId}/feedback`, {
      method: 'POST',
    }),

  stopLab: (labId: string) =>
    fetchJson<{ lab_id: string; status: string }>(`/labs/${labId}/stop`, {
      method: 'POST',
    }),

  listLabs: () =>
    fetchJson<{ labs: { lab_id: string; status: string; jupyter_url: string | null }[] }>('/labs'),
};
