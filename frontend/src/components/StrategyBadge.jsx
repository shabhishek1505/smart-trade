const COLOR_MAP = {
  BUY: "bg-green-100 text-green-800",
  "STRONG BUY": "bg-green-200 text-green-900 font-bold",
  WATCH: "bg-yellow-100 text-yellow-800",
  AVOID: "bg-red-100 text-red-800",
  ALERT: "bg-orange-100 text-orange-800",
  NEUTRAL: "bg-gray-100 text-gray-600",
};

const LABEL_MAP = {
  rsi_ema: "RSI+EMA",
  macd: "MACD",
  breakout: "BREAKOUT",
  bollinger: "BB",
  volume_surge: "VOL",
};

function resolveColor(signal) {
  if (!signal) return COLOR_MAP.NEUTRAL;
  const upper = signal.toUpperCase();
  if (upper.includes("STRONG BUY")) return COLOR_MAP["STRONG BUY"];
  if (upper.includes("BUY")) return COLOR_MAP.BUY;
  if (upper.includes("WATCH")) return COLOR_MAP.WATCH;
  if (upper.includes("AVOID")) return COLOR_MAP.AVOID;
  if (upper.includes("ALERT")) return COLOR_MAP.ALERT;
  return COLOR_MAP.NEUTRAL;
}

export default function StrategyBadge({ strategy, signal, size = "sm" }) {
  const color = resolveColor(signal);
  const label = strategy ? LABEL_MAP[strategy] || strategy.toUpperCase() : signal;
  const sizeClass =
    size === "lg"
      ? "text-sm font-semibold px-3 py-1 rounded-full"
      : "text-xs px-2 py-0.5 rounded";

  return (
    <span className={`inline-block ${color} ${sizeClass}`}>
      {label}
      {signal && size === "sm" ? ` ${signal}` : ""}
    </span>
  );
}
