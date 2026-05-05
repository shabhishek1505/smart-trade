import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, StatCard, Badge } from '../components';
import { apiClient } from '../services/api';
import { PerformanceMetrics, Strategy } from '../types/api';

type StrategyPerf = Strategy;

export default function EnhancedAnalytics() {
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [strategies, setStrategies] = useState<StrategyPerf[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [perfData, stratData] = await Promise.all([
          apiClient.getPerformance(),
          apiClient.getStrategiesPerformance(),
        ]);
        setPerformance(perfData || {
          total_trades: 0,
          winning_trades: 0,
          losing_trades: 0,
          win_rate: 0,
          profit_factor: 0,
          average_win: 0,
          average_loss: 0,
          total_pnl: 0,
        });
        setStrategies(stratData || []);
      } catch (err) {
        console.error('Failed to load analytics data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Sample monthly data
  const monthlyData = [
    { month: 'January', pnl: 5200, trades: 4, wins: 3 },
    { month: 'February', pnl: 4800, trades: 5, wins: 3 },
    { month: 'March', pnl: 22500, trades: 8, wins: 6 },
    { month: 'April', pnl: 12530, trades: 7, wins: 5 },
  ];

  // Sample daily equity curve
  const equityCurve = [
    { date: 'Apr 1', balance: 100000, highWater: 100000 },
    { date: 'Apr 2', balance: 102000, highWater: 102000 },
    { date: 'Apr 3', balance: 105000, highWater: 105000 },
    { date: 'Apr 4', balance: 103000, highWater: 105000 },
    { date: 'Apr 5', balance: 108000, highWater: 108000 },
    { date: 'Apr 6', balance: 112000, highWater: 112000 },
    { date: 'Apr 7', balance: 115000, highWater: 115000 },
    { date: 'Apr 8', balance: 118000, highWater: 118000 },
    { date: 'Apr 9', balance: 130000, highWater: 130000 },
    { date: 'Apr 10', balance: 145230, highWater: 145230 },
  ];

  // Win/Loss ratio data
  const winLossRatio = [
    { category: 'Wins', value: performance?.winning_trades || 0, fill: '#10B981' },
    { category: 'Losses', value: performance?.losing_trades || 0, fill: '#EF4444' },
  ];

  // Returns distribution
  const returnsDistribution = [
    { range: '-50% to 0%', count: 2 },
    { range: '0% to 5%', count: 5 },
    { range: '5% to 10%', count: 8 },
    { range: '10%+', count: 9 },
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Performance Analytics</h1>
        <p className="text-gray-600 mt-1">Detailed analysis of your trading performance</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total P&L"
          value={`₹${(performance?.total_pnl || 0).toLocaleString()}`}
          variant={performance && performance.total_pnl >= 0 ? 'success' : 'danger'}
          icon="📈"
        />
        <StatCard
          title="Win Rate"
          value={`${((performance?.win_rate || 0) * 100).toFixed(1)}%`}
          subtitle={`${performance?.winning_trades || 0} wins`}
          variant="info"
          icon="🎯"
        />
        <StatCard
          title="Sharpe Ratio"
          value={`${(performance?.sharpe_ratio || 0).toFixed(2)}`}
          subtitle="Risk-adjusted return"
          variant="warning"
          icon="📊"
        />
        <StatCard
          title="Max Drawdown"
          value={`${((performance?.max_drawdown || 0) * 100).toFixed(2)}%`}
          subtitle="Worst decline"
          variant="danger"
          icon="📉"
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve with High Water Mark */}
        <Card title="Equity Curve" subtitle="Daily balance with high water mark">
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={equityCurve}>
              <defs>
                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Legend />
              <Area
                type="monotone"
                dataKey="balance"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#colorBalance)"
                name="Balance"
              />
              <Line
                type="monotone"
                dataKey="highWater"
                stroke="#10B981"
                strokeDasharray="5 5"
                name="High Water Mark"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Monthly Returns */}
        <Card title="Monthly P&L" subtitle="Performance by month">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Legend />
              <Bar dataKey="pnl" fill="#3B82F6" name="P&L" />
              <Bar dataKey="wins" fill="#10B981" name="Wins" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Statistics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Win/Loss Distribution */}
        <Card title="Win/Loss Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={winLossRatio}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category, value }) => `${category}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {winLossRatio.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Returns Distribution */}
        <Card title="Returns Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={returnsDistribution}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="range" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Key Metrics */}
        <Card title="Key Metrics">
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b">
              <span className="text-gray-600">Total Trades</span>
              <span className="text-2xl font-bold text-gray-900">{performance?.total_trades || 0}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b">
              <span className="text-gray-600">Profit Factor</span>
              <span className="text-2xl font-bold text-blue-600">{(performance?.profit_factor || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b">
              <span className="text-gray-600">Avg Win</span>
              <span className="text-2xl font-bold text-green-600">₹{(performance?.average_win || 0).toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Loss</span>
              <span className="text-2xl font-bold text-red-600">₹{(performance?.average_loss || 0).toFixed(0)}</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Strategy Performance */}
      <Card title="Strategy Performance" subtitle="Breakdown by trading strategy">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Strategy</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total P&L</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Trades</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Win Rate</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Profit Factor</th>
              </tr>
            </thead>
            <tbody>
              {strategies.map((strategy, index) => {
                const pnl = strategy.total_pnl ?? 0;
                const trades = strategy.signals ?? 0;
                const profit = strategy.profit_factor ?? 0;
                return (
                <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-6 py-4 font-semibold text-gray-900">{strategy.name}</td>
                  <td className={`px-6 py-4 font-semibold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ₹{pnl.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-gray-600">{trades}</td>
                  <td className="px-6 py-4">
                    <Badge
                      label={`${((strategy.win_rate ?? 0) * 100).toFixed(1)}%`}
                      variant={(strategy.win_rate ?? 0) > 0.5 ? 'success' : 'warning'}
                    />
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-900">{profit.toFixed(2)}</td>
                </tr>
              );
              })}

            </tbody>
          </table>
        </div>
      </Card>

      {/* Risk Metrics */}
      <Card title="Risk Metrics" subtitle="Detailed risk analysis">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Sortino Ratio</p>
            <p className="text-3xl font-bold text-purple-600">{(performance?.sortino_ratio || 0).toFixed(2)}</p>
            <p className="text-xs text-gray-500 mt-1">Downside risk adjusted</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Recovery Factor</p>
            <p className="text-3xl font-bold text-blue-600">
              {performance && (performance.max_drawdown ?? 0) !== 0 ? (performance.total_pnl / Math.abs(((performance.max_drawdown ?? 0) * 100000))).toFixed(2) : '-'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Profit per unit drawdown</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Expectancy</p>
            <p className="text-3xl font-bold text-green-600">
              ₹{performance ? ((performance.total_pnl / performance.total_trades) || 0).toFixed(0) : '0'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Avg profit per trade</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Profit/Loss Ratio</p>
            <p className="text-3xl font-bold text-orange-600">
              {performance ? (performance.average_win / Math.abs(performance.average_loss)).toFixed(2) : '-'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Average win vs loss</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
