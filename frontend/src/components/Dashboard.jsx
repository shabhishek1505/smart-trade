import { Settings, Plus, Sun, Moon } from "lucide-react";
import StockCard from "./StockCard";

function formatIST(isoStr) {
  if (!isoStr) return "Never";
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(isoStr));
}

function SummaryPill({ label, count, color }) {
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${color}`}>
      <span>{label}</span>
      <span className="font-bold">{count}</span>
    </div>
  );
}

export default function Dashboard({ stocks, results, loading, darkMode, onToggleDark, onAddStock, onEditStock, onDeleteStock, onOpenSettings }) {
  const resultMap = Object.fromEntries((results.stocks || []).map((r) => [r.ticker, r]));

  const counts = { BUY: 0, WATCH: 0, AVOID: 0, NEUTRAL: 0 };
  (results.stocks || []).forEach((r) => {
    const sig = r.overall_signal || "";
    if (sig.includes("BUY")) counts.BUY++;
    else if (sig.includes("WATCH")) counts.WATCH++;
    else if (sig.includes("AVOID")) counts.AVOID++;
    else counts.NEUTRAL++;
  });

  const displayStocks = stocks.length > 0
    ? stocks
    : (results.stocks || []).map((r) => ({ ticker: r.ticker, display_name: r.display_name }));

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Stock Monitor</h1>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Last run: {formatIST(results.last_run)}</p>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onToggleDark}
            className="p-2 text-gray-400 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <button onClick={onOpenSettings} className="p-2 text-gray-400 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors">
            <Settings size={22} />
          </button>
        </div>
      </div>

      {/* Summary bar */}
      <div className="flex flex-wrap gap-2 mb-6">
        <SummaryPill label="🟢 BUY"     count={counts.BUY}     color="bg-green-50  dark:bg-green-900/30  text-green-700  dark:text-green-400" />
        <SummaryPill label="🟡 WATCH"   count={counts.WATCH}   color="bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400" />
        <SummaryPill label="🔴 AVOID"   count={counts.AVOID}   color="bg-red-50    dark:bg-red-900/30    text-red-700    dark:text-red-400" />
        <SummaryPill label="⚪ NEUTRAL" count={counts.NEUTRAL} color="bg-gray-100  dark:bg-gray-700      text-gray-600   dark:text-gray-300" />
      </div>

      {/* Grid */}
      {loading ? (
        <div className="text-center text-gray-400 dark:text-gray-500 py-20">Loading…</div>
      ) : displayStocks.length === 0 ? (
        <div className="text-center text-gray-400 dark:text-gray-500 py-20">
          <p className="text-lg mb-2">No stocks yet</p>
          <p className="text-sm">Click + to add your first stock</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayStocks.map((stock) => (
            <StockCard
              key={stock.ticker}
              stockConfig={stock}
              result={resultMap[stock.ticker] || null}
              onEdit={onEditStock}
              onDelete={onDeleteStock}
            />
          ))}
        </div>
      )}

      {/* FAB */}
      <button
        onClick={onAddStock}
        className="fixed bottom-6 right-6 bg-blue-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-blue-700 transition-colors"
        aria-label="Add stock"
      >
        <Plus size={26} />
      </button>
    </div>
  );
}
