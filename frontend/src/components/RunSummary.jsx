export default function RunSummary({ data, status }) {
  // Determine color based on status
  const statusColors = {
    IDLE: 'text-slate-500',
    RUNNING: 'text-cyan-400 animate-pulse',
    PASSED: 'text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]',
    FAILED: 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]'
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-cyan-400">📊</span> Run Telemetry
      </h2>

      <div className="space-y-4 flex-grow">
        {/* Status Display */}
        <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800/50 flex justify-between items-center">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">System Status</span>
          <span className={`font-black tracking-widest ${statusColors[status]}`}>
            {status}
          </span>
        </div>

        {/* Dynamic Details Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800/50">
             <span className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-1">Time Elapsed</span>
             <span className="text-2xl font-mono text-white">{data.timeTaken || '00:00'}</span>
          </div>
          <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800/50">
             <span className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-1">Target Repo</span>
             <span className="text-sm font-mono text-slate-300 truncate block w-full">
               {data.repoUrl ? new URL(data.repoUrl).pathname.slice(1) : 'Awaiting input...'}
             </span>
          </div>
        </div>

        {/* Target Branch */}
        <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800/50">
          <span className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-1">Target Output Branch</span>
          <span className="text-sm font-mono text-cyan-300 break-all">
            {data.teamName && data.leaderName 
              ? `${data.teamName.replace(/\s+/g, '_')}_${data.leaderName.replace(/\s+/g, '_')}_AI_Fix`.toUpperCase() 
              : 'AWAITING_INPUT'}
          </span>
        </div>
      </div>
    </div>
  );
}