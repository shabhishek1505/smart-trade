import { useState, useEffect, useRef } from "react";
import { X, PlayCircle, HelpCircle, Loader } from "lucide-react";
import axios from "axios";

const NOTIFY_OPTIONS = ["BUY", "WATCH", "AVOID"];
const POLL_INTERVAL = 12000;   // check status every 12s
const MAX_WAIT_MS   = 5 * 60 * 1000; // give up after 5 min

export default function SettingsPanel({ stocks, onSave, onClose, onResultsRefresh }) {
  const [form, setForm] = useState({
    telegram_group_chat_id: "",
    telegram_private_chat_id: "",
    run_time_utc: "10:17",
    notify_on: ["BUY", "WATCH"],
  });
  const [saved, setSaved] = useState(false);
  const [runState, setRunState] = useState("idle"); // idle | triggered | running | done | error
  const [runMsg, setRunMsg]     = useState("");
  const pollRef  = useRef(null);
  const startRef = useRef(null);

  useEffect(() => {
    axios.get("/api/stocks").then((res) => {
      const s = res.data.settings || {};
      setForm((f) => ({ ...f, ...s }));
    });
    return () => clearPoll();
  }, []);

  const clearPoll = () => {
    if (pollRef.current) clearInterval(pollRef.current);
  };

  const toggle = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const toggleNotify = (opt) =>
    setForm((f) => ({
      ...f,
      notify_on: f.notify_on.includes(opt)
        ? f.notify_on.filter((n) => n !== opt)
        : [...f.notify_on, opt],
    }));

  const handleSave = async (e) => {
    e.preventDefault();
    await onSave(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const startPolling = (lastRunBefore) => {
    startRef.current = Date.now();
    pollRef.current = setInterval(async () => {
      // timeout guard
      if (Date.now() - startRef.current > MAX_WAIT_MS) {
        clearPoll();
        setRunState("error");
        setRunMsg("Timed out waiting for results. Check GitHub Actions.");
        return;
      }

      try {
        // check workflow status
        const { data: wf } = await axios.get("/api/run/status");
        if (wf.status === "in_progress" || wf.status === "queued") {
          setRunState("running");
          setRunMsg("Analysis running… checking every 12s");
          return;
        }
        if (wf.status === "completed") {
          if (wf.conclusion === "failure") {
            clearPoll();
            setRunState("error");
            setRunMsg("Workflow failed. Check GitHub Actions for details.");
            return;
          }
          // workflow done — wait briefly for GitHub raw CDN to update
          setTimeout(async () => {
            await onResultsRefresh();
            clearPoll();
            setRunState("done");
            setRunMsg("Done! Dashboard updated with latest results.");
          }, 3000);
        }
      } catch {
        // silently continue polling
      }
    }, POLL_INTERVAL);
  };

  const handleRunNow = async () => {
    setRunState("triggered");
    setRunMsg("Triggering analysis…");
    clearPoll();
    try {
      const { data } = await axios.post("/api/run");
      if (data.error) {
        setRunState("error");
        setRunMsg(data.error);
        return;
      }
      setRunMsg("Triggered! Analysis running — results in ~3 min");
      setRunState("running");
      // capture current last_run to detect change
      const resultsNow = await axios.get("/api/results").then(r => r.data.last_run).catch(() => null);
      startPolling(resultsNow);
    } catch (e) {
      setRunState("error");
      setRunMsg(e.response?.data?.error || "Failed to trigger. Check GITHUB_PAT on Render.");
    }
  };

  const istTime = (() => {
    const [h, m] = form.run_time_utc.split(":").map(Number);
    const ist = (h * 60 + m + 330) % (24 * 60);
    return `${String(Math.floor(ist / 60)).padStart(2, "0")}:${String(ist % 60).padStart(2, "0")} IST`;
  })();

  const runBtnLabel = {
    idle:      "Run Now",
    triggered: "Triggering…",
    running:   "Running…",
    done:      "Done ✓",
    error:     "Retry",
  }[runState];

  const runMsgColor = runState === "error" ? "text-red-600" : runState === "done" ? "text-green-600" : "text-blue-600";

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-lg mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-gray-900">Settings</h1>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={22} /></button>
        </div>

        {/* Run Now card */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 mb-5">
          <h2 className="font-semibold text-gray-800 mb-3">Manual Analysis</h2>
          <button
            onClick={handleRunNow}
            disabled={runState === "triggered" || runState === "running"}
            className="flex items-center gap-2 bg-blue-600 text-white rounded-xl px-5 py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-60 transition-colors"
          >
            {(runState === "triggered" || runState === "running")
              ? <Loader size={16} className="animate-spin" />
              : <PlayCircle size={16} />}
            {runBtnLabel}
          </button>
          {runMsg && <p className={`text-xs mt-2 ${runMsgColor}`}>{runMsg}</p>}
          <p className="text-xs text-gray-400 mt-2">
            Triggers GitHub Actions — takes ~3 min. Results auto-update here when done.
          </p>
        </div>

        <form onSubmit={handleSave} className="space-y-5">
          {/* Telegram */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 space-y-4">
            <h2 className="font-semibold text-gray-800">Telegram</h2>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Group Chat ID</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                placeholder="-1001234567890"
                value={form.telegram_group_chat_id}
                onChange={(e) => toggle("telegram_group_chat_id", e.target.value)}
              />
              <p className="text-xs text-gray-400 mt-1 flex items-start gap-1">
                <HelpCircle size={12} className="mt-0.5 shrink-0" />
                Negative number. Add bot to group → send a message → visit getUpdates URL
              </p>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Private Chat ID</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                placeholder="123456789"
                value={form.telegram_private_chat_id}
                onChange={(e) => toggle("telegram_private_chat_id", e.target.value)}
              />
            </div>
          </div>

          {/* Schedule */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 space-y-4">
            <h2 className="font-semibold text-gray-800">Schedule</h2>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Run Time (UTC)</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                placeholder="10:17"
                value={form.run_time_utc}
                onChange={(e) => toggle("run_time_utc", e.target.value)}
              />
              <p className="text-xs text-gray-400 mt-1">= {istTime}</p>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-2">Notify on</label>
              <div className="flex gap-3">
                {NOTIFY_OPTIONS.map((opt) => (
                  <label key={opt} className="flex items-center gap-1.5 cursor-pointer">
                    <input type="checkbox" checked={form.notify_on.includes(opt)} onChange={() => toggleNotify(opt)} className="accent-blue-500" />
                    <span className="text-sm text-gray-700">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <button type="submit" className="w-full bg-blue-600 text-white rounded-xl py-2.5 text-sm font-medium hover:bg-blue-700">
            {saved ? "Saved ✓" : "Save Settings"}
          </button>
        </form>
      </div>
    </div>
  );
}
