export default function Timeline({ currentStep, status }) {
  const steps = [
    { id: 1, label: 'Clone Repository' },
    { id: 2, label: 'Test Discovery Engine' },
    { id: 3, label: 'AI Minister Classification' },
    { id: 4, label: 'Sandbox Execution' },
    { id: 5, label: 'Git Operations' }
  ];

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-cyan-400">⏱️</span> Action Timeline
      </h2>

      <div className="relative border-l-2 border-slate-800 ml-3 space-y-8 my-4">
        {steps.map((step) => {
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id || status === 'PASSED';
          const isFailed = status === 'FAILED' && currentStep === step.id;

          let bulletColor = 'bg-slate-800 border-slate-600';
          let textColor = 'text-slate-500';

          if (isCompleted) {
            bulletColor = 'bg-green-500 border-green-400 shadow-[0_0_10px_rgba(34,197,94,0.5)]';
            textColor = 'text-slate-300';
          } else if (isFailed) {
            bulletColor = 'bg-red-500 border-red-400 shadow-[0_0_10px_rgba(239,68,68,0.5)]';
            textColor = 'text-red-400';
          } else if (isActive) {
            bulletColor = 'bg-cyan-500 border-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.5)] animate-pulse';
            textColor = 'text-cyan-400 font-bold';
          }

          return (
            <div key={step.id} className="relative pl-6">
              {/* Timeline Dot */}
              <div className={`absolute -left-[9px] top-1.5 h-4 w-4 rounded-full border-2 ${bulletColor}`}></div>
              {/* Step Text */}
              <div className={`font-mono text-sm tracking-wide transition-colors ${textColor}`}>
                {step.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}