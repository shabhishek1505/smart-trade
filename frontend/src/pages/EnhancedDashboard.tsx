import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
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
import { Card, StatCard, Table, Badge, Button } from '../components';
import { apiClient } from '../services/api';
import { Trade, Position, PerformanceMetrics } from '../types/api';

export default function EnhancedDashboard() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [tradesData, positionsData, perfData] = await Promise.all([
          apiClient.getTrades(0, 5),
          apiClient.getPositions(),
          apiClient.getPerformance(),
        ]);
        setTrades(tradesData || []);
        setPositions(positionsData || []);
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
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Sample equity curve data
  const equityData = [
    { date: 'Apr 1', value: 100000 },
    { date: 'Apr 3', value: 105000 },
    { date: 'Apr 5', value: 110000 },
    { date: 'Apr 7', value: 108000 },
    { date: 'Apr 9', value: 115000 },
    { date: 'Apr 10', value: 145230 },
  ];

  // Strategy distribution
  const strategyData = [
    { name: 'SMA RSI MACD', value: 45, color: '#3B82F6' },
    { name: 'Moving Avg', value: 35, color: '#10B981' },
    { name: 'RSI MACD', value: 20, color: '#F59E0B' },
  ];

  // Win/Loss distribution
  const winLossData = [
    { name: 'Wins', value: performance?.winning_trades || 0 },
    { name: 'Losses', value: performance?.losing_trades || 0 },
  ];

  const tradeColumns = [
    { key: 'symbol', title: 'Symbol' },
    { key: 'action', title: 'Action', render: (val: string) => <Badge label={val} variant={val === 'BUY' ? 'success' : 'danger'} /> },
    { key: 'entry_price', title: 'Entry', render: (val: number) => `₹${val.toFixed(2)}` },
    { key: 'exit_price', title: 'Exit', render: (val: number) => `₹${val?.toFixed(2) || '-'}` },
    {
      key: 'pnl',
      title: 'P&L',
      render: (val: number) => (
        <span className={val >= 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
          ₹{val.toFixed(2)}
        </span>
      ),
    },
    {
      key: 'status',
      title: 'Status',
      render: (val: string) => (
        <Badge
          label={val}
          variant={val === 'CLOSED' ? 'success' : val === 'OPEN' ? 'info' : 'warning'}
        />
      ),
    },
  ];

  const positionColumns = [
    { key: 'symbol', title: 'Symbol' },
    { key: 'quantity', title: 'Quantity' },
    { key: 'average_price', title: 'Avg Price', render: (val: number) => `₹${val.toFixed(2)}` },
    { key: 'current_price', title: 'Current', render: (val: number) => `₹${val.toFixed(2)}` },
    {
      key: 'current_value',
      title: 'Value',
      render: (val: number, record: Position) => {
        const pnl = record.current_value - record.invested_value;
        return (
          <div>
            <div className="font-semibold">₹{val.toFixed(0)}</div>
            <div className={pnl >= 0 ? 'text-green-600 text-sm' : 'text-red-600 text-sm'}>
              {pnl >= 0 ? '+' : ''}₹{pnl.toFixed(0)}
            </div>
          </div>
        );
      },
    },
  ];

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card title="Error">
          <p className="text-red-600">{error}</p>
        </Card>
      </div>
    );
  }

  const totalInvested = positions.reduce((sum, p) => sum + (p.invested_value || 0), 0);
  const totalCurrentValue = positions.reduce((sum, p) => sum + (p.current_value || 0), 0);
  const unrealizedPnL = totalCurrentValue - totalInvested;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trading Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your trading overview.</p>
        </div>
        <Button variant="primary" onClick={() => window.location.href = '/strategies'}>
          📊 View Strategies
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Balance"
          value={`₹${(totalCurrentValue + (performance?.total_pnl || 0)).toLocaleString()}`}
          variant="info"
          trend={((performance?.total_pnl || 0) / 100000) * 100}
          trendLabel="vs initial"
        />
        <StatCard
          title="Portfolio Value"
          value={`₹${totalCurrentValue.toLocaleString()}`}
          subtitle={`+₹${unrealizedPnL.toLocaleString()}`}
          variant="success"
        />
        <StatCard
          title="Total P&L"
          value={`₹${(performance?.total_pnl || 0).toLocaleString()}`}
          variant={performance && performance.total_pnl >= 0 ? 'success' : 'danger'}
        />
        <StatCard
          title="Win Rate"
          value={`${((performance?.win_rate || 0) * 100).toFixed(1)}%`}
          subtitle={`${performance?.winning_trades || 0}W / ${performance?.losing_trades || 0}L`}
          variant="warning"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Equity Curve */}
        <Card title="Equity Growth" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={equityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Strategy Distribution */}
        <Card title="Strategy Mix">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={strategyData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {strategyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Risk Metrics">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Sharpe Ratio</span>
              <span className="text-xl font-bold text-gray-900">{((performance?.sharpe_ratio ?? 0) as number).toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Profit Factor</span>
              <span className="text-xl font-bold text-gray-900">{((performance?.profit_factor ?? 0) as number).toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Win/Loss</span>
              <span className="text-xl font-bold text-gray-900">
                {performance ? (performance.average_win / Math.abs(performance.average_loss)).toFixed(2) : '-'}
              </span>
            </div>
          </div>
        </Card>

        <Card title="Trade Summary">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Trades</span>
              <span className="text-xl font-bold text-gray-900">{performance?.total_trades || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Win</span>
              <span className="text-xl font-bold text-green-600">₹{(performance?.average_win || 0).toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Loss</span>
              <span className="text-xl font-bold text-red-600">₹{(performance?.average_loss || 0).toFixed(0)}</span>
            </div>
          </div>
        </Card>

        <Card title="Win/Loss Distribution">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={winLossData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Trades */}
      <Card title="Recent Trades" subtitle="Last 5 trades" headerAction={<Button variant="ghost" size="sm">View All</Button>}>
        <Table columns={tradeColumns} data={trades} rowKey="id" loading={loading} />
      </Card>

      {/* Open Positions */}
      <Card title="Open Positions" subtitle={`${positions.length} position(s) open`}>
        <Table columns={positionColumns} data={positions} rowKey="id" loading={loading} />
      </Card>
    </div>
  );
}
