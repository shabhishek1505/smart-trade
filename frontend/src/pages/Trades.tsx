import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { Trade } from '../types/api';

export default function Trades() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    const loadTrades = async () => {
      try {
        const data = await apiClient.getTrades(currentPage, pageSize);
        setTrades(data);
      } catch (error) {
        console.error('Failed to load trades:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTrades();
  }, [currentPage, pageSize]);

  if (loading) {
    return <div className="text-center py-8">Loading trades...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Trade History</h1>
        <div className="flex gap-4">
          <select className="px-4 py-2 border border-gray-300 rounded">
            <option>All Strategies</option>
            <option>SMA RSI MACD</option>
            <option>Moving Average Crossover</option>
          </select>
          <input
            type="date"
            className="px-4 py-2 border border-gray-300 rounded"
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Symbol</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Entry</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Exit</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Qty</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">P&L</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Return %</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 font-semibold text-gray-900">{trade.symbol}</td>
                <td className={`px-6 py-4 font-semibold ${trade.action === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                  {trade.action}
                </td>
                <td className="px-6 py-4 text-gray-600">₹{trade.entry_price?.toFixed(2) || '-'}</td>
                <td className="px-6 py-4 text-gray-600">₹{trade.exit_price?.toFixed(2) || '-'}</td>
                <td className="px-6 py-4 text-gray-600">{trade.quantity || '-'}</td>
                <td className={`px-6 py-4 font-semibold ${(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ₹{trade.pnl?.toFixed(2) || '-'}
                </td>
                <td className={`px-6 py-4 ${(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {trade.pnl ? ((trade.pnl / (trade.entry_price || 1)) * 100).toFixed(2) : '-'}%
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    trade.status === 'CLOSED' ? 'bg-green-100 text-green-800' :
                    trade.status === 'OPEN' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {trade.status || 'CLOSED'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center">
        <select value={pageSize} onChange={(e) => setPageSize(parseInt(e.target.value))}>
          <option value={10}>10 per page</option>
          <option value={25}>25 per page</option>
          <option value={50}>50 per page</option>
        </select>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-4 py-2">Page {currentPage + 1}</span>
          <button
            onClick={() => setCurrentPage(currentPage + 1)}
            className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
