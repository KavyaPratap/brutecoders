import { useState } from 'react';

export default function InputSection({ onStart, status }) {
  const [inputs, setInputs] = useState({
    repoUrl: '',
    teamName: '',
    leaderName: ''
  });

  const handleChange = (e) => {
    setInputs({ ...inputs, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputs.repoUrl && inputs.teamName && inputs.leaderName) {
      onStart(inputs);
    }
  };

  const isRunning = status === 'RUNNING';

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-cyan-400">⚡</span> Agent Initialization
      </h2>
      
      <form onSubmit={handleSubmit} className="flex flex-col flex-grow gap-5">
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1 uppercase tracking-wider">GitHub Repository URL</label>
          <input 
            type="url" 
            name="repoUrl"
            required
            placeholder="https://github.com/user/repo"
            onChange={handleChange}
            disabled={isRunning}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1 uppercase tracking-wider">Team Name</label>
          <input 
            type="text" 
            name="teamName"
            required
            placeholder="e.g., RIFT ORGANISERS"
            onChange={handleChange}
            disabled={isRunning}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1 uppercase tracking-wider">Leader Name</label>
          <input 
            type="text" 
            name="leaderName"
            required
            placeholder="e.g., Saiyam Kumar"
            onChange={handleChange}
            disabled={isRunning}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all disabled:opacity-50"
          />
        </div>

        <div className="mt-auto pt-4">
          <button 
            type="submit" 
            disabled={isRunning}
            className={`w-full py-4 rounded-lg font-bold text-sm tracking-wide transition-all ${
              isRunning 
                ? 'bg-slate-800 text-cyan-500 border border-cyan-900 cursor-not-allowed flex justify-center items-center gap-2' 
                : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-[0_0_15px_rgba(8,145,178,0.4)] hover:shadow-[0_0_25px_rgba(8,145,178,0.6)]'
            }`}
          >
            {isRunning ? (
              <>
                <svg className="animate-spin h-5 w-5 text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                INITIALIZING AGENT...
              </>
            ) : 'RUN AGENT'}
          </button>
        </div>
      </form>
    </div>
  );
}