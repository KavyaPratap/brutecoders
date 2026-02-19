export default function ScoreBoard({ score }) {
  // Calculate percentage for the progress bar
  const percentage = Math.max(0, Math.min(100, (score.total / 100) * 100));

  return (
    <div className="flex flex-col h-full relative z-10">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-yellow-400">🏆</span> Live Score
      </h2>

      <div className="flex-grow flex flex-col justify-center">
        {/* The Big Number */}
        <div className="flex items-end gap-2 mb-6">
          <span className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-sm">
            {score.total}
          </span>
          <span className="text-slate-400 font-mono mb-2">/ 100</span>
        </div>

        {/* Score Breakdown */}
        <div className="space-y-3 font-mono text-sm mb-8">
          <div className="flex justify-between text-slate-300">
            <span>Base Score</span>
            <span>{score.base}</span>
          </div>
          <div className="flex justify-between text-green-400">
            <span>Speed Bonus (&lt;5m)</span>
            <span>+{score.speedBonus}</span>
          </div>
          <div className="flex justify-between text-red-400">
            <span>Efficiency Penalty</span>
            <span>{score.efficiencyPenalty}</span>
          </div>
        </div>

        {/* Visual Progress Bar */}
        <div className="w-full bg-slate-900 rounded-full h-3 border border-slate-700 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-cyan-500 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out relative"
            style={{ width: `${percentage}%` }}
          >
            <div className="absolute top-0 right-0 bottom-0 left-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.15)_50%,rgba(255,255,255,0.15)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem] animate-[progress_1s_linear_infinite]"></div>
          </div>
        </div>
      </div>
    </div>
  );
}