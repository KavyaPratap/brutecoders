import { useState } from 'react';
import InputSection from './components/InputSection';
import RunSummary from './components/RunSummary';
import ScoreBoard from './components/ScoreBoard';
import FixesTable from './components/FixesTable';
import Timeline from './components/Timeline';

function App() {
  // --- STATE MANAGEMENT ---
  const [status, setStatus] = useState('IDLE'); 
  const [runData, setRunData] = useState({
    repoUrl: '',
    teamName: '',
    leaderName: '',
    timeTaken: '00:00'
  });
  const [score, setScore] = useState({ base: 100, speedBonus: 0, efficiencyPenalty: 0, total: 100 });
  const [fixes, setFixes] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);

  // --- THE INTEGRATION: API CALL & SSE STREAM ---
  const handleStartRun = async (inputs) => {
    // 1. Reset the dashboard for a new run
    setStatus('RUNNING');
    setRunData(prev => ({ ...prev, ...inputs, timeTaken: '00:00' }));
    setFixes([]); 
    setScore({ base: 100, speedBonus: 0, efficiencyPenalty: 0, total: 100 });
    setCurrentStep(1); 

    try {
      // 2. Trigger the FastAPI Backend
      const response = await fetch('http://127.0.0.1:8000/api/run-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs)
      });

      if (!response.ok) throw new Error("Backend failed to start");
      
      const data = await response.json();
      console.log("Agent initialized. Run ID:", data.run_id);

      // 3. Connect to the Real-Time SSE Stream
      const eventSource = new EventSource(`http://127.0.0.1:8000/api/stream/${data.run_id}`);

      // Listen for Status changes (RUNNING, PASSED, FAILED)
      eventSource.addEventListener('status', (e) => {
        setStatus(e.data);
        if (e.data === 'PASSED' || e.data === 'FAILED') {
          eventSource.close(); // Close connection when done
        }
      });

      // Listen for Timeline Step changes
      eventSource.addEventListener('step', (e) => {
        setCurrentStep(parseInt(e.data));
      });

      // Listen for text logs (we will just print these to the browser console for now)
      eventSource.addEventListener('log', (e) => {
        console.log("🤖 AGENT LOG:", e.data);
      });

      // Listen for applied fixes to populate the table
      eventSource.addEventListener('fix', (e) => {
        const newFix = JSON.parse(e.data);
        setFixes(prev => [...prev, newFix]);
      });

      // Listen for the final Score calculation
      eventSource.addEventListener('score', (e) => {
        const newScore = JSON.parse(e.data);
        setScore(newScore);
      });

      // Handle connection errors
      eventSource.onerror = (err) => {
        console.error("SSE Stream Error:", err);
        setStatus('FAILED');
        eventSource.close();
      };

    } catch (error) {
      console.error("Failed to communicate with backend:", error);
      setStatus('FAILED');
    }
  };

  return (
    <div className="min-h-screen p-6 md:p-12">
      <header className="mb-10 border-b border-cyan-900/50 pb-6">
        <h1 className="text-4xl font-black tracking-tight text-white drop-shadow-md">
          <span className="text-cyan-400">THE HEALING</span> AGENT
        </h1>
        <p className="mt-2 text-slate-400 font-mono text-sm">Autonomous Code Repair & Scoring Dashboard</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-2xl backdrop-blur-sm">
             <InputSection onStart={handleStartRun} status={status} />
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-2xl backdrop-blur-sm">
             <Timeline currentStep={currentStep} status={status} />
          </div>
        </div>

        <div className="lg:col-span-8 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-2xl backdrop-blur-sm">
               <RunSummary data={runData} status={status} />
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-2xl backdrop-blur-sm relative overflow-hidden">
               <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-cyan-500/10 blur-3xl"></div>
               <ScoreBoard score={score} />
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-2xl backdrop-blur-sm min-h-[400px]">
             <FixesTable fixes={fixes} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;