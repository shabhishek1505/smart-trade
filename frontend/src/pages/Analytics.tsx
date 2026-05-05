import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { PerformanceMetrics } from '../types/api';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function Analytics() {
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await apiClient.getPerformance();
        setPerformance(data);
      } catch (error) {
        console.error('Failed to load analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading analytics...</div>;
  }

  const equityData = [
    { month: 'Jan', value: 100000 },
    { month: 'Feb', value: 105000 },
    { month: 'Mar', value: 125000 },
    { month: 'Apr', value: 145230 },
  ];

  const monthlyReturnsData = [
    { month: 'Jan', return: 5 },
    { month: 'Feb', return: 4.8 },
    { month: 'Mar', return: 19 },
    { month: 'Apr', return: 16.2 },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Performance Analytics</h1>

      {/* Key Metrics */}
      {performance && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-gray-600 text-sm font-semibold">Win Rate</h4>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {(performance.win_rate * 100).toFixed(1)}%
            </p>
            <p className="text-gray-500 text-sm mt-1">
              {Math.round(performance.total_trades * (performance.win_rate || 0))} wins / {performance.total_trades} trades
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-gray-600 text-sm font-semibold">Sharpe Ratio</h4>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {((performance?.sharpe_ratio) ?? 0).toFixed(2)}
            </p>
            <p className="text-gray-500 text-sm mt-1">Risk-adjusted return</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-gray-600 text-sm font-semibold">Max Drawdown</h4>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {(((performance?.max_drawdown) ?? 0) * 100).toFixed(2)}%
            </p>
            <p className="text-gray-500 text-sm mt-1">Worst decline</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-gray-600 text-sm font-semibold">Total P&L</h4>
            <p className="text-3xl font-bold text-green-600 mt-2">
              ₹{performance.total_pnl?.toLocaleString() || '0'}
            </p>
            <p className="text-gray-500 text-sm mt-1">Cumulative profit</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-2 gap-8">
        {/* Equity Curve */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Equity Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={equityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Returns */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Monthly Returns</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyReturnsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
              <Bar dataKey="return" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-6">Detailed Metrics</h3>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <p className="text-gray-600 text-sm">Profit Factor</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">2.45</p>
            <p className="text-gray-500 text-sm mt-1">Gross profit / Gross loss</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Avg. Win</p>
            <p className="text-2xl font-bold text-green-600 mt-1">₹1,245</p>
            <p className="text-gray-500 text-sm mt-1">Average winning trade</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Avg. Loss</p>
            <p className="text-2xl font-bold text-red-600 mt-1">₹-650</p>
            <p className="text-gray-500 text-sm mt-1">Average losing trade</p>
          </div>

          <div>
            <p className="text-gray-600 text-sm">Win/Loss Ratio</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">1.92</p>
            <p className="text-gray-500 text-sm mt-1">Avg win / Avg loss</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Consecutive Wins</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">5</p>
            <p className="text-gray-500 text-sm mt-1">Best streak</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Consecutive Losses</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
            <p className="text-gray-500 text-sm mt-1">Worst streak</p>
          </div>
        </div>
      </div>
    </div>
  );
}
