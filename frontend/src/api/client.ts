const API_BASE = '/api';

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...init,
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
}

// Types matching backend API models
export interface GenerateRequest {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  num_source_tables: number;
  focus_skills: string[];
  industry: string;
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
}

export interface ValidationResult {
  query_name: string;
  passed: boolean;
  expected_row_count: number;
  actual_row_count: number | null;
  expected_columns: string[];
  actual_columns: string[] | null;
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

  stopLab: (labId: string) =>
    fetchJson<{ lab_id: string; status: string }>(`/labs/${labId}/stop`, {
      method: 'POST',
    }),

  listLabs: () =>
    fetchJson<{ labs: { lab_id: string; status: string; jupyter_url: string | null }[] }>('/labs'),
};
