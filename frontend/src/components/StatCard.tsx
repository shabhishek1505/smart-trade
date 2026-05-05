import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: number;
  trendLabel?: string;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info';
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendLabel,
  variant = 'default',
  className = '',
}) => {
  const bgColors = {
    default: 'bg-blue-50 border-blue-200',
    success: 'bg-green-50 border-green-200',
    danger: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-purple-50 border-purple-200',
  };

  const iconColors = {
    default: 'text-blue-600',
    success: 'text-green-600',
    danger: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-purple-600',
  };

  const trendColors = {
    positive: 'text-green-600 bg-green-50',
    negative: 'text-red-600 bg-red-50',
  };

  return (
    <div
      className={`${bgColors[variant]} border rounded-lg p-6 flex items-start justify-between ${className}`}
    >
      <div className="flex-1">
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
        {trend !== undefined && trendLabel && (
          <div
            className={`${
              trend >= 0 ? trendColors.positive : trendColors.negative
            } inline-block px-3 py-1 rounded text-sm font-semibold mt-2`}
          >
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% {trendLabel}
          </div>
        )}
      </div>
      {icon && <div className={`${iconColors[variant]} text-3xl ml-4`}>{icon}</div>}
    </div>
  );
};
