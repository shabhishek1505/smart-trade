import React, { useState } from 'react';
import { apiClient } from '../services/api';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('credentials');
  const [formData, setFormData] = useState({
    apiKey: '',
    apiSecret: '',
    password: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleAddCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await apiClient.addCredentials({
        broker: 'angel_one',
        api_key: formData.apiKey,
        api_secret: formData.apiSecret,
      });
      setMessage('Credentials added successfully');
      setFormData({ ...formData, apiKey: '', apiSecret: '' });
    } catch (error) {
      setMessage('Failed to add credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.newPassword !== formData.confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      await apiClient.changePassword({
        old_password: formData.password,
        new_password: formData.newPassword,
      });
      setMessage('Password changed successfully');
      setFormData({
        ...formData,
        password: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (error) {
      setMessage('Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Settings</h1>

      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveTab('credentials')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'credentials'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Broker Credentials
        </button>
        <button
          onClick={() => setActiveTab('preferences')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'preferences'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Preferences
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'security'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Security
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-4 rounded ${
          message.includes('success') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {message}
        </div>
      )}

      {/* Broker Credentials */}
      {activeTab === 'credentials' && (
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-2xl font-bold mb-6">Connect Broker</h2>
          <form onSubmit={handleAddCredentials} className="space-y-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Broker</label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded">
                <option>Angel One</option>
                <option>Zerodha</option>
                <option>ICICI Direct</option>
                <option>5paisa</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">API Key</label>
              <input
                type="password"
                name="apiKey"
                value={formData.apiKey}
                onChange={handleInputChange}
                placeholder="Your broker API key"
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">API Secret</label>
              <input
                type="password"
                name="apiSecret"
                value={formData.apiSecret}
                onChange={handleInputChange}
                placeholder="Your broker API secret"
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-semibold"
              >
                {loading ? 'Adding...' : 'Add Credentials'}
              </button>
              <button
                type="button"
                className="px-6 py-2 border border-gray-300 rounded hover:bg-gray-50 font-semibold"
              >
                Test Connection
              </button>
            </div>
          </form>

          <div className="mt-8 pt-8 border-t">
            <h3 className="text-xl font-bold mb-4">Connected Accounts</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-4 border rounded">
                <div>
                  <p className="font-semibold">Angel One</p>
                  <p className="text-gray-600 text-sm">Connected on Apr 10, 2026</p>
                </div>
                <button className="text-red-600 hover:text-red-700 font-semibold">
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preferences */}
      {activeTab === 'preferences' && (
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-2xl font-bold mb-6">Preferences</h2>
          <form className="space-y-6">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Theme</label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded">
                <option>Light</option>
                <option>Dark</option>
                <option>Auto</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Language</label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded">
                <option>English</option>
                <option>Hindi</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Timezone</label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded">
                <option>Asia/Kolkata (IST)</option>
                <option>UTC</option>
              </select>
            </div>

            <div>
              <label className="flex items-center">
                <input type="checkbox" className="rounded mr-2" defaultChecked />
                <span className="text-gray-700 font-semibold">Email notifications for trades</span>
              </label>
            </div>

            <div>
              <label className="flex items-center">
                <input type="checkbox" className="rounded mr-2" defaultChecked />
                <span className="text-gray-700 font-semibold">Browser notifications</span>
              </label>
            </div>

            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-semibold"
            >
              Save Preferences
            </button>
          </form>
        </div>
      )}

      {/* Security */}
      {activeTab === 'security' && (
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-2xl font-bold mb-6">Change Password</h2>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">Current Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your current password"
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">New Password</label>
              <input
                type="password"
                name="newPassword"
                value={formData.newPassword}
                onChange={handleInputChange}
                placeholder="Enter new password (min 8 chars)"
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm your new password"
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-semibold"
            >
              {loading ? 'Updating...' : 'Change Password'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
