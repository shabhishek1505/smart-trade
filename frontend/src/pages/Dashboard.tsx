import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { Strategy, Signal, Trade, PerformanceMetrics } from '../types/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [balance, setBalance] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [stratsData, signalsData, tradesData, perfData, balData] = await Promise.all([
          apiClient.getStrategies(),
          apiClient.getSignals(0, 5),
          apiClient.getTrades(0, 5),
          apiClient.getPerformance(),
          apiClient.getBalance(),
        ]);

        setStrategies(stratsData);
        setSignals(signalsData);
        setTrades(tradesData);
        setPerformance(perfData);
        setBalance(balData);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading dashboard...</div>;
  }

  const chartData = [
    { name: 'Jan', pnl: 5000 },
    { name: 'Feb', pnl: 12000 },
    { name: 'Mar', pnl: 25000 },
    { name: 'Apr', pnl: 45000 },
  ];

  return (
    <div className="space-y-8">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Total Balance</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            ${balance?.total_balance?.toLocaleString() || '0'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Available Capital</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">
            ${balance?.available_capital?.toLocaleString() || '0'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Total P&L</h3>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            ${performance?.total_pnl?.toLocaleString() || '0'}
          </p>
        </div>
      </div>

      {/* Performance Metrics */}
      {performance && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-gray-600 text-sm">Win Rate</h4>
            <p className="text-2xl font-bold text-green-600">{(performance.win_rate * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-gray-600 text-sm">Sharpe Ratio</h4>
            <p className="text-2xl font-bold text-blue-600">{((performance?.sharpe_ratio) ?? 0).toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-gray-600 text-sm">Max Drawdown</h4>
            <p className="text-2xl font-bold text-red-600">{(((performance?.max_drawdown) ?? 0) * 100).toFixed(2)}%</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-gray-600 text-sm">Total Trades</h4>
            <p className="text-2xl font-bold text-gray-900">{performance.total_trades}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-8">
        {/* Equity Curve */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="pnl" stroke="#3B82F6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Trades */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Trades</h3>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-left py-2">Symbol</th>
                  <th className="text-left py-2">Action</th>
                  <th className="text-right py-2">P&L</th>
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 5).map((trade) => (
                  <tr key={trade.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 font-semibold">{trade.symbol}</td>
                    <td className={`py-2 ${trade.action === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                      {trade.action}
                    </td>
                    <td className={`py-2 text-right ${trade.pnl! >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${trade.pnl?.toLocaleString() || '0'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Active Strategies */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Active Strategies</h3>
        <div className="grid grid-cols-3 gap-4">
          {strategies.map((strategy) => (
            <div key={strategy.name} className="border rounded p-4 hover:shadow-lg transition">
              <h4 className="font-semibold text-gray-900">{strategy.name}</h4>
              <div className="mt-2 space-y-1 text-sm text-gray-600">
                <div>Signals: {strategy.signals}</div>
                <div>Win Rate: {(strategy.win_rate * 100).toFixed(1)}%</div>
                <div className={`font-semibold ${strategy.enabled ? 'text-green-600' : 'text-red-600'}`}>
                  {strategy.enabled ? '✓ Enabled' : '✗ Disabled'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
