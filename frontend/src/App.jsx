import { useEffect, useState } from 'react';
import { Activity, Users } from 'lucide-react';

function App() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/teams')
      .then((res) => res.json())
      .then((data) => {
        setTeams(data);
        setLoading(false);
      })
      .catch((err) => console.error("Error fetching teams:", err));
  }, []);

  return (
    <div className="min-h-screen p-8">
      <header className="mb-10 flex items-center gap-3 border-b border-slate-700 pb-6">
        <Activity className="h-8 w-8 text-emerald-400" />
        <h1 className="text-3xl font-bold tracking-tight text-white">PitchVision</h1>
      </header>

      <main>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-200">2022 World Cup Teams</h2>
          <span className="flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-400">
            <Users className="h-4 w-4" />
            {teams.length} Teams Loaded
          </span>
        </div>

        {loading ? (
          <div className="flex h-40 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/50">
            <p className="text-slate-400 animate-pulse">Loading database...</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {teams.map((team) => (
              <div 
                key={team.team_id} 
                className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-700 bg-slate-800 p-4 transition-colors hover:border-emerald-500 hover:bg-slate-700"
              >
                <span className="font-medium text-slate-200">{team.name}</span>
                <span className="text-xs text-slate-500">ID: {team.team_id}</span>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;