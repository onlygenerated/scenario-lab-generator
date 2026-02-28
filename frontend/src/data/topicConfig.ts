export interface TopicConfig {
  skills: { id: string; label: string }[];
  defaultSkills: string[];
  formSubtitle: string;
}

export const TOPIC_CONFIG: Record<string, TopicConfig> = {
  'etl-pipelines': {
    skills: [
      { id: 'JOIN', label: 'JOIN' },
      { id: 'AGGREGATION', label: 'AGGREGATION' },
      { id: 'WINDOW_FUNCTION', label: 'WINDOW FUNCTION' },
      { id: 'PIVOT', label: 'PIVOT' },
      { id: 'CLEANING', label: 'CLEANING' },
      { id: 'DATE_HANDLING', label: 'DATE HANDLING' },
      { id: 'DEDUPLICATION', label: 'DEDUPLICATION' },
      { id: 'TYPE_CASTING', label: 'TYPE CASTING' },
    ],
    defaultSkills: ['JOIN', 'AGGREGATION'],
    formSubtitle: 'Choose parameters for your data pipeline lab',
  },
  'data-modeling': {
    skills: [
      { id: 'NORMALIZATION', label: 'NORMALIZATION' },
      { id: 'PRIMARY_KEY', label: 'PRIMARY KEY' },
      { id: 'FOREIGN_KEY', label: 'FOREIGN KEY' },
      { id: 'STAR_SCHEMA', label: 'STAR SCHEMA' },
      { id: 'SURROGATE_KEY', label: 'SURROGATE KEY' },
      { id: 'CONSTRAINT_DESIGN', label: 'CONSTRAINTS' },
      { id: 'INDEXING', label: 'INDEXING' },
      { id: 'SCD', label: 'SLOWLY CHANGING DIM' },
    ],
    defaultSkills: ['NORMALIZATION', 'PRIMARY_KEY'],
    formSubtitle: 'Choose parameters for your data modeling lab',
  },
};
