export default function FixesTable({ fixes }) {
  const getBugColor = (type) => {
    const colors = {
      LINTING: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10',
      SYNTAX: 'text-red-400 border-red-400/30 bg-red-400/10',
      LOGIC: 'text-purple-400 border-purple-400/30 bg-purple-400/10',
      TYPE_ERROR: 'text-orange-400 border-orange-400/30 bg-orange-400/10',
      IMPORT: 'text-blue-400 border-blue-400/30 bg-blue-400/10',
      INDENTATION: 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10',
    };
    return colors[type] || 'text-slate-400 border-slate-400/30 bg-slate-400/10';
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-cyan-400">📋</span> Applied Fixes Ledger
      </h2>

      <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/50 flex-grow">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 text-xs font-mono text-slate-400 uppercase tracking-wider">
              <th className="p-4 font-medium">File Context</th>
              <th className="p-4 font-medium">Bug Classification</th>
              <th className="p-4 font-medium">Commit Message</th>
              <th className="p-4 font-medium text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 font-mono text-sm">
            {fixes.length === 0 ? (
              <tr>
                <td colSpan="4" className="p-8 text-center text-slate-500 italic">
                  Awaiting agent telemetry...
                </td>
              </tr>
            ) : (
              fixes.map((fix, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors group">
                  <td className="p-4">
                    <span className="text-slate-300 block">{fix.file}</span>
                    <span className="text-slate-500 text-xs">Line {fix.line}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-[10px] uppercase border ${getBugColor(fix.type)}`}>
                      {fix.type}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400 group-hover:text-slate-200 transition-colors">
                    {fix.commitMsg}
                  </td>
                  <td className="p-4 text-right">
                    <span className={`flex items-center justify-end gap-1 ${fix.status === 'FIXED' ? 'text-green-400' : 'text-red-400'}`}>
                      {fix.status === 'FIXED' ? '✓' : '✗'} {fix.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}