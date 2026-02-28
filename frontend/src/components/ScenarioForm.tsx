import { useState, useMemo } from 'react';
import type { GenerateRequest } from '../api/client';
import { TOPIC_CONFIG } from '../data/topicConfig';
import WILD_CARDS from './wildCards';

interface ScenarioFormProps {
  onGenerate: (request: GenerateRequest) => void;
  onDemo: () => void;
  loading: boolean;
  demoMode: boolean;
  topicId?: string;
}

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


const CUSTOM_SENTINEL = '__custom__';

const WILD_CARD_SENTINEL = '__wildcard__';

export function ScenarioForm({ onGenerate, onDemo, loading, demoMode, topicId }: ScenarioFormProps) {
  const config = TOPIC_CONFIG[topicId || 'etl-pipelines'] || TOPIC_CONFIG['etl-pipelines'];
  const [difficulty, setDifficulty] = useState<GenerateRequest['difficulty']>('intermediate');
  const [numTables, setNumTables] = useState(2);
  const [skills, setSkills] = useState<string[]>(config.defaultSkills);
  const [industry, setIndustry] = useState('retail');
  const [customIndustry, setCustomIndustry] = useState('');
  const [includeSolutions, setIncludeSolutions] = useState(true);
  const wildCard = useMemo(() => WILD_CARDS[Math.floor(Math.random() * WILD_CARDS.length)], []);
  const effectiveIndustry =
    industry === CUSTOM_SENTINEL ? customIndustry.trim() :
    industry === WILD_CARD_SENTINEL ? wildCard :
    industry;

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
    if (industry === CUSTOM_SENTINEL && effectiveIndustry.length === 0) return;
    onGenerate({
      difficulty,
      num_source_tables: numTables,
      focus_skills: skills,
      industry: effectiveIndustry,
      include_solutions: includeSolutions,
      topic: topicId || 'etl-pipelines',
    });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6">
        <h2 className="text-xl font-semibold text-stone-900 mb-1">Configure Scenario</h2>
        <p className="text-sm text-stone-500 mb-6">
          {config.formSubtitle}
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">Difficulty</label>
            <div className="flex gap-3">
              {(['beginner', 'intermediate', 'advanced'] as const).map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty(d)}
                  className={`
                    px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors font-mono
                    ${difficulty === d
                      ? 'bg-teal-600 text-white shadow-[0_2px_0_0_rgba(0,0,0,0.2)] active:shadow-none active:translate-y-[1px]'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
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
            <label className="block text-sm font-medium text-stone-700 mb-2">
              Source Tables: {numTables}
            </label>
            <input
              type="range"
              min={1}
              max={5}
              value={numTables}
              onChange={(e) => setNumTables(Number(e.target.value))}
              className="w-full accent-teal-600"
            />
            <div className="flex justify-between text-xs text-stone-500 mt-1">
              <span>1</span>
              <span>5</span>
            </div>
          </div>

          {/* Focus Skills */}
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">
              Focus Skills <span className="text-stone-500 font-normal">(select up to 5)</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {config.skills.map((skill) => (
                <button
                  key={skill.id}
                  type="button"
                  onClick={() => toggleSkill(skill.id)}
                  className={`
                    px-3 py-1.5 rounded text-xs font-medium transition-colors font-mono
                    ${skills.includes(skill.id)
                      ? 'border border-teal-400 text-teal-700 bg-teal-50/50'
                      : 'border border-stone-300 text-stone-500 bg-transparent hover:border-stone-400'
                    }
                  `}
                >
                  {skill.label}
                </button>
              ))}
            </div>
          </div>

          {/* Industry / Theme */}
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">Industry / Theme</label>
            <div className="flex flex-wrap gap-2">
              {INDUSTRIES.map((ind) => (
                <button
                  key={ind}
                  type="button"
                  onClick={() => setIndustry(ind)}
                  className={`
                    px-3 py-1.5 rounded text-xs font-medium transition-colors font-mono
                    ${industry === ind
                      ? 'border border-teal-400 text-teal-700 bg-teal-50/50'
                      : 'border border-stone-300 text-stone-500 bg-transparent hover:border-stone-400'
                    }
                  `}
                >
                  {ind.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </button>
              ))}
              <button
                type="button"
                onClick={() => setIndustry(WILD_CARD_SENTINEL)}
                className={`
                  px-3 py-1.5 rounded text-xs font-medium transition-colors font-mono
                  ${industry === WILD_CARD_SENTINEL
                    ? 'border border-purple-400 text-purple-700 bg-purple-50/50'
                    : 'border border-stone-300 text-purple-500 bg-transparent hover:border-stone-400'
                  }
                `}
              >
                {wildCard}
              </button>
              <button
                type="button"
                onClick={() => setIndustry(CUSTOM_SENTINEL)}
                className={`
                  px-3 py-1.5 rounded text-xs font-medium transition-colors font-mono
                  ${industry === CUSTOM_SENTINEL
                    ? 'border border-teal-400 text-teal-700 bg-teal-50/50'
                    : 'border border-stone-300 text-stone-500 bg-transparent hover:border-stone-400'
                  }
                `}
              >
                Custom…
              </button>
            </div>
            {industry === CUSTOM_SENTINEL && (
              <input
                type="text"
                value={customIndustry}
                onChange={(e) => setCustomIndustry(e.target.value)}
                maxLength={100}
                autoFocus
                placeholder="Your industry, a movie, a celebrity, or whatever you want!"
                className="mt-2 w-full px-3 py-2 border border-stone-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            )}
          </div>

          {/* Options */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="include-solutions"
              checked={includeSolutions}
              onChange={(e) => setIncludeSolutions(e.target.checked)}
              className="h-4 w-4 rounded border-stone-300 text-teal-600 focus:ring-teal-500"
            />
            <label htmlFor="include-solutions" className="text-sm text-stone-600">
              Include solution & incorrect solution notebooks in lab
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading || skills.length === 0 || (industry === CUSTOM_SENTINEL && customIndustry.trim().length === 0)}
              className="flex-1 bg-teal-600 text-white py-2.5 rounded-md text-sm font-semibold hover:bg-teal-500 active:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-[0_2px_0_0_rgba(0,0,0,0.2)] active:shadow-none active:translate-y-[1px]"
            >
              {loading ? 'Generating...' : 'Generate Scenario'}
            </button>
            {demoMode && (
              <button
                type="button"
                onClick={onDemo}
                disabled={loading}
                className="px-5 py-2.5 border border-stone-300 rounded-md text-sm font-medium text-stone-600 hover:bg-stone-50 disabled:opacity-50 transition-colors"
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
