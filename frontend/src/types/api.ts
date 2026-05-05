/**API Types */

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Strategy {
  id?: number;
  name: string;
  enabled: boolean;
  signals?: number;
  win_rate: number;
  total_pnl?: number;
  profit_factor?: number;
}

export interface Signal {
  id: number;
  strategy: string;
  symbol: string;
  signal: "BUY" | "SELL" | "HOLD";
  price: number;
  confidence: number;
  status: "PENDING" | "EXECUTED" | "REJECTED";
  timestamp: string;
}

export interface Trade {
  id: number;
  symbol: string;
  action: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  pnl_pct?: number;
  entry_time: string;
  exit_time?: string;
  status: "OPEN" | "CLOSED" | "CANCELLED";
  strategy?: string;
}

export interface Position {
  id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  invested_value: number;
  current_value: number;
  unrealized_pnl?: number;
  unrealized_pnl_pct?: number;
  strategy?: string;
}

export interface PerformanceMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  average_win: number;
  average_loss: number;
  max_drawdown?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  total_pnl: number;
  current_balance?: number;
  starting_balance?: number;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  message?: string;
  timestamp: string;
}
