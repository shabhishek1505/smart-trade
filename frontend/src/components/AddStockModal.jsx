import { useState, useEffect } from "react";
import { X } from "lucide-react";

const ALL_STRATEGIES = [
  { id: "rsi_ema", label: "RSI + EMA" },
  { id: "macd", label: "MACD Crossover" },
  { id: "breakout", label: "52-Week Breakout" },
  { id: "bollinger", label: "Bollinger Band Squeeze" },
  { id: "volume_surge", label: "Volume Surge" },
];

const DEFAULT_FORM = {
  ticker: "",
  display_name: "",
  active: true,
  strategies: ["rsi_ema"],
  custom_stop_loss_pct: 5,
  notes: "",
};

export default function AddStockModal({ editStock, existingTickers, onSave, onClose }) {
  const isEdit = Boolean(editStock);
  const [form, setForm] = useState(DEFAULT_FORM);
  const [error, setError] = useState("");

  useEffect(() => {
    if (editStock) {
      setForm({ ...DEFAULT_FORM, ...editStock });
    }
  }, [editStock]);

  const toggle = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const toggleStrategy = (id) => {
    setForm((f) => ({
      ...f,
      strategies: f.strategies.includes(id)
        ? f.strategies.filter((s) => s !== id)
        : [...f.strategies, id],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!form.ticker.trim()) return setError("Ticker is required");
    if (!form.display_name.trim()) return setError("Display name is required");
    if (form.strategies.length === 0) return setError("Select at least one strategy");

    const ticker = form.ticker.trim().toUpperCase();
    if (!isEdit && existingTickers.map((t) => t.toUpperCase()).includes(ticker)) {
      return setError("This ticker is already in your watchlist");
    }

    onSave({ ...form, ticker, _isEdit: isEdit });
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="font-bold text-gray-900 text-lg">{isEdit ? "Edit Stock" : "Add Stock"}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">NSE Ticker *</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 uppercase"
                placeholder="e.g. BEL.NS"
                value={form.ticker}
                onChange={(e) => toggle("ticker", e.target.value.toUpperCase())}
                disabled={isEdit}
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Display Name *</label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                placeholder="e.g. BEL"
                value={form.display_name}
                onChange={(e) => toggle("display_name", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-600 block mb-2">Strategies *</label>
            <div className="space-y-2">
              {ALL_STRATEGIES.map(({ id, label }) => (
                <label key={id} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.strategies.includes(id)}
                    onChange={() => toggleStrategy(id)}
                    className="accent-blue-500"
                  />
                  <span className="text-sm text-gray-700">{label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">
              Stop-Loss % <span className="text-gray-400">(default 5)</span>
            </label>
            <input
              type="number"
              min="1"
              max="20"
              step="0.5"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              value={form.custom_stop_loss_pct}
              onChange={(e) => toggle("custom_stop_loss_pct", parseFloat(e.target.value))}
            />
          </div>

          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">Notes</label>
            <textarea
              rows={2}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none"
              placeholder="Your personal notes..."
              value={form.notes}
              onChange={(e) => toggle("notes", e.target.value)}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="active"
              checked={form.active}
              onChange={(e) => toggle("active", e.target.checked)}
              className="accent-blue-500"
            />
            <label htmlFor="active" className="text-sm text-gray-700 cursor-pointer">Active (include in daily analysis)</label>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 border border-gray-200 rounded-xl py-2 text-sm text-gray-600 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" className="flex-1 bg-blue-600 text-white rounded-xl py-2 text-sm font-medium hover:bg-blue-700">
              {isEdit ? "Save Changes" : "Add Stock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
