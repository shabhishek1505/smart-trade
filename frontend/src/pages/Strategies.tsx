import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { Strategy } from '../types/api';

export default function Strategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        const data = await apiClient.getStrategies();
        setStrategies(data);
      } catch (error) {
        console.error('Failed to load strategies:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStrategies();
  }, []);

  const handleToggleStrategy = async (strategyName: string, enabled: boolean) => {
    try {
      if (enabled) {
        await apiClient.stopStrategy(strategyName);
      } else {
        await apiClient.startStrategy(strategyName);
      }
      setStrategies(strategies.map(s =>
        s.name === strategyName ? { ...s, enabled: !enabled } : s
      ));
    } catch (error) {
      console.error('Failed to toggle strategy:', error);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading strategies...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Strategies</h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Add Strategy
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {strategies.map((strategy) => (
          <div key={strategy.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900">{strategy.name}</h3>
                <div className="mt-4 grid grid-cols-4 gap-4">
                  <div>
                    <p className="text-gray-600 text-sm">Signals</p>
                    <p className="text-2xl font-bold">{strategy.signals}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Win Rate</p>
                    <p className="text-2xl font-bold text-green-600">
                      {(strategy.win_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Total Trades</p>
                    <p className="text-2xl font-bold">24</p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">P&L</p>
                    <p className="text-2xl font-bold text-green-600">+₹12,500</p>
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleToggleStrategy(strategy.name, strategy.enabled)}
                className={`px-6 py-3 rounded font-semibold transition ${
                  strategy.enabled
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
              >
                {strategy.enabled ? '✓ Enabled' : '✗ Disabled'}
              </button>
            </div>

            <div className="mt-6 pt-6 border-t">
              <button className="text-blue-600 hover:underline font-semibold">
                View Details & Performance →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
