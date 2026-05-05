import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { User } from '../types/api';

interface LayoutProps {
  children: React.ReactNode;
  user: User | null;
  onLogout: () => void;
}

export default function Layout({ children, user, onLogout }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    onLogout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/strategies', label: 'Strategies', icon: '🎯' },
    { path: '/trades', label: 'Trades', icon: '📈' },
    { path: '/positions', label: 'Positions', icon: '💼' },
    { path: '/analytics', label: 'Analytics', icon: '📉' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white transition-all`}>
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-xl font-bold">Smart-Trade</h1>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-800 rounded">
            {sidebarOpen ? '◄' : '►'}
          </button>
        </div>

        <nav className="mt-8">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 transition ${
                location.pathname === item.path
                  ? 'bg-blue-600 border-l-4 border-blue-400'
                  : 'hover:bg-gray-800'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              {sidebarOpen && <span className="ml-3">{item.label}</span>}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-8 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Smart-Trade Dashboard</h2>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{user?.username}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-8">{children}</div>
      </div>
    </div>
  );
}
