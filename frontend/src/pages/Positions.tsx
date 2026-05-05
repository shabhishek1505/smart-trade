import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { Position } from '../types/api';

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPositions = async () => {
      try {
        const data = await apiClient.getPositions();
        setPositions(data || []);
      } catch (error) {
        console.error('Failed to load positions:', error);
        setPositions([]);
      } finally {
        setLoading(false);
      }
    };

    loadPositions();
  }, []);

  const totalValue = positions.reduce((sum, p) => sum + (p.current_value || 0), 0);
  const totalInvested = positions.reduce((sum, p) => sum + (p.invested_value || 0), 0);
  const totalPnL = totalValue - totalInvested;

  if (loading) {
    return <div className="text-center py-8">Loading positions...</div>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Current Positions</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Total Position Value</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            ₹{totalValue.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Total Invested</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            ₹{totalInvested.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-semibold">Total P&L</h3>
          <p className={`text-3xl font-bold mt-2 ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ₹{totalPnL.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-white rounded-lg shadow overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Symbol</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Quantity</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Avg. Cost</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Current Price</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Position Value</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">P&L</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Return %</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => {
              const pnl = (position.current_value || 0) - (position.invested_value || 0);
              const returnPct = position.invested_value ? (pnl / position.invested_value) * 100 : 0;
              return (
                <tr key={position.symbol} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 font-semibold text-gray-900">{position.symbol}</td>
                  <td className="px-6 py-4 text-gray-600">{position.quantity}</td>
                  <td className="px-6 py-4 text-gray-600">₹{position.average_price?.toFixed(2) || '-'}</td>
                  <td className="px-6 py-4 text-gray-600">₹{position.current_price?.toFixed(2) || '-'}</td>
                  <td className="px-6 py-4 font-semibold text-gray-900">₹{position.current_value?.toLocaleString() || '-'}</td>
                  <td className={`px-6 py-4 font-semibold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ₹{pnl.toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 ${returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {returnPct.toFixed(2)}%
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-red-600 hover:text-red-700 font-semibold">
                      Close
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {positions.length === 0 && (
        <div className="text-center py-8 text-gray-600">
          No open positions. Start a strategy to open positions.
        </div>
      )}
    </div>
  );
}
