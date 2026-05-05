import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { apiClient } from './services/api';
import { User } from './types/api';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Strategies from './pages/Strategies';
import Trades from './pages/Trades';
import Positions from './pages/Positions';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Layout from './components/Layout';

interface ProtectedRouteProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
}

function ProtectedRoute({ children, isAuthenticated }: ProtectedRouteProps) {
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      apiClient.setToken(token);
      apiClient
        .getCurrentUser()
        .then((user) => {
          setUser(user);
          setIsAuthenticated(true);
        })
        .catch(() => {
          localStorage.removeItem('access_token');
          setIsAuthenticated(false);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
        <Route path="/register" element={<Register onRegister={() => setIsAuthenticated(true)} />} />

        <Route
          path="/*"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <Layout user={user} onLogout={() => setIsAuthenticated(false)}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/strategies" element={<Strategies />} />
                  <Route path="/trades" element={<Trades />} />
                  <Route path="/positions" element={<Positions />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
