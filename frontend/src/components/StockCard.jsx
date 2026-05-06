import { useState } from "react";
import { Pencil, Trash2, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import StrategyBadge from "./StrategyBadge";

const STRAT_LABELS = {
  rsi_ema:      "RSI + EMA",
  macd:         "MACD",
  bollinger:    "Bollinger Bands",
  breakout:     "52W Breakout",
  volume_surge: "Volume Surge",
};

function OverallBadge({ signal }) {
  if (!signal) return <span className="text-gray-400 dark:text-gray-500 text-sm">Pending analysis</span>;
  const color = signal.includes("BUY")
    ? "bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300"
    : signal.includes("WATCH")
    ? "bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300"
    : signal.includes("AVOID")
    ? "bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300"
    : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300";
  return <span className={`text-sm font-semibold px-3 py-1 rounded-full ${color}`}>{signal}</span>;
}

function LLMVerdictBadge({ verdict }) {
  const styles = {
    BULLISH: "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-700",
    BEARISH: "bg-rose-100 dark:bg-rose-900/40 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-700",
    NEUTRAL: "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-600",
  };
  const icons = { BULLISH: "▲", BEARISH: "▼", NEUTRAL: "◆" };
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${styles[verdict] || styles.NEUTRAL}`}>
      {icons[verdict] || "◆"} {verdict}
    </span>
  );
}

function ConfidenceDots({ confidence }) {
  const levels = { HIGH: 3, MEDIUM: 2, LOW: 1 };
  const filled = levels[confidence] || 1;
  return (
    <span className="flex gap-0.5 items-center">
      {[1, 2, 3].map((i) => (
        <span key={i} className={`w-1.5 h-1.5 rounded-full ${i <= filled ? "bg-violet-500" : "bg-gray-200 dark:bg-gray-600"}`} />
      ))}
      <span className="text-xs text-gray-400 dark:text-gray-500 ml-0.5">{confidence}</span>
    </span>
  );
}

export default function StockCard({ result, stockConfig, onEdit, onDelete }) {
  const [expanded, setExpanded] = useState(false);

  const name         = result?.display_name || stockConfig?.display_name || stockConfig?.ticker;
  const ticker       = result?.ticker || stockConfig?.ticker;
  const price        = result?.last_price;
  const chg          = result?.day_change_pct;
  const overall      = result?.overall_signal;
  const stratResults = result?.strategy_results || {};
  const notes        = stockConfig?.notes || result?.notes;
  const llm          = result?.llm_verdict;
  const runAt        = result?.run_at
    ? new Date(result.run_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: true })
    : null;

  const entryZone = result?.best_entry_zone;
  const sl  = result?.best_stop_loss;
  const t1  = result?.best_target_1;
  const t2  = result?.best_target_2;

  const hasDetail = Object.keys(stratResults).length > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col transition-colors">

      {/* Clickable main body */}
      <div
        className={`p-4 flex flex-col gap-3 ${hasDetail ? "cursor-pointer" : ""}`}
        onClick={hasDetail ? () => setExpanded((e) => !e) : undefined}
      >
        {/* Header row */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-gray-900 dark:text-gray-100 text-lg">{name}</span>
              <span className="text-xs text-gray-400 dark:text-gray-500">{ticker}</span>
            </div>
            {price != null && (
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-gray-700 dark:text-gray-300 font-medium">₹{price.toLocaleString("en-IN")}</span>
                {chg != null && (
                  <span className={`text-sm font-medium ${chg >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                    {chg >= 0 ? "+" : ""}{chg.toFixed(2)}%
                  </span>
                )}
              </div>
            )}
          </div>
          {/* Action buttons — stop propagation so they don't toggle expand */}
          <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
            {onEdit && (
              <button onClick={() => onEdit(stockConfig)} className="p-1 text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 transition-colors">
                <Pencil size={15} />
              </button>
            )}
            {onDelete && (
              <button onClick={() => onDelete(ticker)} className="p-1 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors">
                <Trash2 size={15} />
              </button>
            )}
          </div>
        </div>

        <OverallBadge signal={overall} />

        {/* Strategy badges */}
        {Object.keys(stratResults).length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(stratResults).map(([strat, res]) => (
              <StrategyBadge key={strat} strategy={strat} signal={res.signal} size="sm" />
            ))}
          </div>
        )}

        {/* Levels */}
        {entryZone && (
          <div className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-2 space-y-0.5">
            <div>Entry: ₹{entryZone[0].toLocaleString("en-IN")} – ₹{entryZone[1].toLocaleString("en-IN")}</div>
            {sl && <div>SL: ₹{sl.toLocaleString("en-IN")}</div>}
            {t1 && <div>T1: ₹{t1.toLocaleString("en-IN")}{t2 ? ` | T2: ₹${t2.toLocaleString("en-IN")}` : ""}</div>}
          </div>
        )}

        {/* AI Verdict */}
        {llm && (
          <div className="border border-violet-100 dark:border-violet-800/50 bg-violet-50/60 dark:bg-violet-900/20 rounded-lg p-3 flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-violet-700 dark:text-violet-400">
                <Sparkles size={13} />
                <span className="text-xs font-semibold tracking-wide uppercase">AI Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <ConfidenceDots confidence={llm.confidence} />
                <LLMVerdictBadge verdict={llm.verdict} />
              </div>
            </div>
            <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{llm.reasoning}</p>
            {llm.market_context && (
              <p className="text-xs text-violet-600 dark:text-violet-400 italic">{llm.market_context}</p>
            )}
          </div>
        )}

        {/* Notes */}
        {notes && (
          <p className="text-xs text-gray-500 dark:text-gray-400 italic border-t border-gray-50 dark:border-gray-700 pt-2">{notes}</p>
        )}

        {/* Footer */}
        {hasDetail && (
          <div className="flex items-center justify-between pt-0.5">
            {runAt ? <p className="text-xs text-gray-400 dark:text-gray-500">↻ {runAt}</p> : <span />}
            <span className="flex items-center gap-1 text-xs text-blue-500 dark:text-blue-400 font-medium">
              {expanded ? "Hide details" : "Indicator details"}
              {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </span>
          </div>
        )}
      </div>

      {/* Expanded detail drawer */}
      {expanded && hasDetail && (
        <div className="border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40 rounded-b-xl px-4 py-4 space-y-4">
          {Object.entries(stratResults).map(([strat, res]) => (
            <div key={strat}>
              {/* Strategy heading */}
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wide">
                  {STRAT_LABELS[strat] || strat}
                </span>
                <StrategyBadge strategy={strat} signal={res.signal} size="xs" />
              </div>

              {/* Reason */}
              {res.reason && (
                <p className="text-xs text-gray-500 dark:text-gray-400 italic mb-2">{res.reason}</p>
              )}

              {/* Indicator values grid */}
              {res.indicators && Object.keys(res.indicators).length > 0 && (
                <div className="grid grid-cols-2 gap-x-6 gap-y-1">
                  {Object.entries(res.indicators).map(([key, val]) => (
                    <div key={key} className="flex justify-between items-center py-0.5 border-b border-gray-100 dark:border-gray-700/60">
                      <span className="text-xs text-gray-400 dark:text-gray-500">{key}</span>
                      <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 tabular-nums">{val}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
