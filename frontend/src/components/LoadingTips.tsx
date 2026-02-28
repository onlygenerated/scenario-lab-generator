import { useState, useEffect, useMemo } from 'react';
import ETL_TIPS from './etlTips';

interface LoadingTipsProps {
  skills: string[];
  intervalMs?: number;
}

export function LoadingTips({ skills, intervalMs = 15000 }: LoadingTipsProps) {
  // Build a shuffled list of relevant tips: skill-matched first, then general
  const tips = useMemo(() => {
    const tags = new Set(skills);
    const matched = ETL_TIPS.filter((t) => tags.has(t.tag));
    const general = ETL_TIPS.filter((t) => t.tag === 'GENERAL');
    const pool = [...matched, ...general];
    // Fisher-Yates shuffle
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    return pool;
  }, [skills]);

  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (tips.length === 0) return;
    const id = setInterval(() => {
      setIndex((prev) => (prev + 1) % tips.length);
    }, intervalMs);
    return () => clearInterval(id);
  }, [tips, intervalMs]);

  if (tips.length === 0) return null;

  return (
    <div className="mt-10 w-full max-w-lg bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 px-6 pt-4 pb-5 text-center">
      <p className="text-sm font-semibold text-stone-500 uppercase tracking-wide mb-3 font-mono">Tips</p>
      <p className="text-base text-stone-600">
        {tips[index].text}
      </p>
    </div>
  );
}
