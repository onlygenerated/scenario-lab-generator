import { Link } from 'react-router-dom';
import { CATEGORIES } from '../data/categories';

export function Landing() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="bg-stone-900 border-b border-stone-800">
        <div className="max-w-5xl mx-auto px-6 py-12 text-center">
          <h1 className="text-3xl font-bold text-stone-50 font-mono tracking-tight">
            <span className="text-teal-400">&#9656;</span> labwright
          </h1>
          <p className="mt-2 text-stone-400 font-mono text-sm">
            ai-generated hands-on labs — pick a topic, get a live environment
          </p>
        </div>
      </header>

      {/* Category Grid */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {CATEGORIES.map((category) => {
            const hasAvailable = category.topics.some((t) => t.available);
            return (
              <div
                key={category.id}
                className={`
                  bg-white/80 backdrop-blur-sm rounded-lg border border-stone-200/60 p-6 flex flex-col
                  ${hasAvailable ? 'border-l-2 border-l-teal-500' : 'opacity-75'}
                `}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{category.icon}</span>
                  <h2 className="text-lg font-semibold text-stone-900">{category.name}</h2>
                </div>
                <p className="text-sm text-stone-500 mb-4">{category.description}</p>

                <ul className="space-y-2 mt-auto">
                  {category.topics.map((topic) => (
                    <li key={topic.id}>
                      {topic.available ? (
                        <Link
                          to={`/lab/${category.id}/${topic.id}`}
                          className="flex items-center gap-2 text-sm font-medium text-teal-600 hover:text-teal-800 transition-colors"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-teal-500 shrink-0" />
                          {topic.name}
                        </Link>
                      ) : (
                        <div className="flex items-center gap-2 text-sm text-stone-500">
                          <span className="w-1.5 h-1.5 rounded-full bg-stone-300 shrink-0" />
                          <span>{topic.name}</span>
                          <span className="ml-auto text-xs bg-stone-100 text-stone-500 px-2 py-0.5 rounded font-mono">
                            Coming Soon
                          </span>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
