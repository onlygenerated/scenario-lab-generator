import { useState } from 'react';
import type { GenerateRequest } from '../api/client';

interface ScenarioFormProps {
  onGenerate: (request: GenerateRequest) => void;
  onDemo: () => void;
  loading: boolean;
  demoMode: boolean;
}

const SKILL_OPTIONS = [
  'JOIN',
  'AGGREGATION',
  'WINDOW_FUNCTION',
  'PIVOT',
  'CLEANING',
  'DATE_HANDLING',
  'DEDUPLICATION',
  'TYPE_CASTING',
];

const INDUSTRIES = [
  'retail',
  'healthcare',
  'finance',
  'logistics',
  'education',
  'marketing',
  'manufacturing',
  'real_estate',
];

export function ScenarioForm({ onGenerate, onDemo, loading, demoMode }: ScenarioFormProps) {
  const [difficulty, setDifficulty] = useState<GenerateRequest['difficulty']>('intermediate');
  const [numTables, setNumTables] = useState(2);
  const [skills, setSkills] = useState<string[]>(['JOIN', 'AGGREGATION']);
  const [industry, setIndustry] = useState('retail');

  const toggleSkill = (skill: string) => {
    setSkills((prev) =>
      prev.includes(skill)
        ? prev.filter((s) => s !== skill)
        : prev.length < 5
          ? [...prev, skill]
          : prev
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      difficulty,
      num_source_tables: numTables,
      focus_skills: skills,
      industry,
    });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-1">Configure Scenario</h2>
        <p className="text-sm text-gray-500 mb-6">
          Choose parameters for your data pipeline lab
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <div className="flex gap-3">
              {(['beginner', 'intermediate', 'advanced'] as const).map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty(d)}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors
                    ${difficulty === d
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }
                  `}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Source Tables */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Tables: {numTables}
            </label>
            <input
              type="range"
              min={1}
              max={5}
              value={numTables}
              onChange={(e) => setNumTables(Number(e.target.value))}
              className="w-full accent-indigo-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>1</span>
              <span>5</span>
            </div>
          </div>

          {/* Focus Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Focus Skills <span className="text-gray-400 font-normal">(select up to 5)</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {SKILL_OPTIONS.map((skill) => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => toggleSkill(skill)}
                  className={`
                    px-3 py-1.5 rounded-full text-xs font-medium transition-colors
                    ${skills.includes(skill)
                      ? 'bg-indigo-100 text-indigo-700 ring-1 ring-indigo-300'
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                    }
                  `}
                >
                  {skill.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {INDUSTRIES.map((ind) => (
                <option key={ind} value={ind}>
                  {ind.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading || skills.length === 0}
              className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Generating...' : 'Generate Scenario'}
            </button>
            {demoMode && (
              <button
                type="button"
                onClick={onDemo}
                disabled={loading}
                className="px-5 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                Use Demo
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
