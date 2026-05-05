import { useState, useEffect } from "react";
import { X, PlayCircle, HelpCircle } from "lucide-react";
import axios from "axios";

const NOTIFY_OPTIONS = ["BUY", "WATCH", "AVOID"];

export default function SettingsPanel({ stocks, onSave, onClose }) {
  const [form, setForm] = useState({
    telegram_group_chat_id: "",
    telegram_private_chat_id: "",
    run_time_utc: "10:17",
    notify_on: ["BUY", "WATCH"],
  });
  const [saved, setSaved] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    axios.get("/api/stocks").then((res) => {
      const s = res.data.settings || {};
      setForm((f) => ({ ...f, ...s }));
    });
  }, []);

  const toggle = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const toggleNotify = (opt) => {
    setForm((f) => ({
      ...f,
      notify_on: f.notify_on.includes(opt)
        ? f.notify_on.filter((n) => n !== opt)
        : [...f.notify_on, opt],
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    await onSave(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleRunNow = async () => {
    setRunning(true);
    try {
      await axios.post("/api/run");
      alert("Analysis started! Check Telegram in ~2 minutes.");
    } catch {
      alert("Failed to trigger run. Make sure the backend is running.");
    } finally {
      setRunning(false);
    }
  };

  const istTime = (() => {
    const [h, m] = form.run_time_utc.split(":").map(Number);
    const ist = (h * 60 + m + 330) % (24 * 60);
    const hh = String(Math.floor(ist / 60)).padStart(2, "0");
    const mm = String(ist % 60).padStart(2, "0");
    return `${hh}:${mm} IST`;
  })();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-lg mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-gray-900">Settings</h1>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={22} />
          </button>
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
                Negative number. Add bot to group → send a message → visit
                <code className="text-gray-500 ml-1">api.telegram.org/bot&#123;TOKEN&#125;/getUpdates</code>
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
              <p className="text-xs text-gray-400 mt-1">Positive number. DM the bot and use getUpdates.</p>
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
              <p className="text-xs text-gray-400 mt-1">= {istTime} (update GitHub Actions cron to match)</p>
            </div>

            <div>
              <label className="text-xs font-medium text-gray-600 block mb-2">Notify on</label>
              <div className="flex gap-3">
                {NOTIFY_OPTIONS.map((opt) => (
                  <label key={opt} className="flex items-center gap-1.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.notify_on.includes(opt)}
                      onChange={() => toggleNotify(opt)}
                      className="accent-blue-500"
                    />
                    <span className="text-sm text-gray-700">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleRunNow}
              disabled={running}
              className="flex items-center gap-2 border border-gray-200 rounded-xl px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <PlayCircle size={16} />
              {running ? "Starting…" : "Run Now"}
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white rounded-xl py-2 text-sm font-medium hover:bg-blue-700"
            >
              {saved ? "Saved ✓" : "Save Settings"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
