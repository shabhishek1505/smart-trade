import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Dashboard from "./components/Dashboard";
import SettingsPanel from "./components/SettingsPanel";
import AddStockModal from "./components/AddStockModal";

axios.defaults.baseURL = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [stocks, setStocks] = useState([]);
  const [results, setResults] = useState({ last_run: null, stocks: [] });
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("dashboard");
  const [modalState, setModalState] = useState({ open: false, editStock: null });

  const fetchData = useCallback(async () => {
    try {
      const [stocksRes, resultsRes] = await Promise.all([
        axios.get("/api/stocks"),
        axios.get("/api/results"),
      ]);
      setStocks(stocksRes.data.stocks || []);
      setResults(resultsRes.data);
    } catch (e) {
      console.error("Failed to fetch data:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSaveStock = async (formData) => {
    if (formData._isEdit) {
      const { _isEdit, ...body } = formData;
      await axios.put(`/api/stocks/${body.ticker}`, body);
    } else {
      await axios.post("/api/stocks", formData);
    }
    setModalState({ open: false, editStock: null });
    await fetchData();
  };

  const handleDeleteStock = async (ticker) => {
    if (!window.confirm(`Remove ${ticker}?`)) return;
    await axios.delete(`/api/stocks/${ticker}`);
    fetchData();
  };

  const handleSaveSettings = async (settings) => {
    await axios.put("/api/settings", settings);
    fetchData();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {activeView === "dashboard" ? (
        <Dashboard
          stocks={stocks}
          results={results}
          loading={loading}
          onAddStock={() => setModalState({ open: true, editStock: null })}
          onEditStock={(stock) => setModalState({ open: true, editStock: stock })}
          onDeleteStock={handleDeleteStock}
          onOpenSettings={() => setActiveView("settings")}
        />
      ) : (
        <SettingsPanel
          stocks={stocks}
          onSave={handleSaveSettings}
          onClose={() => setActiveView("dashboard")}
          onResultsRefresh={fetchData}
        />
      )}

      {modalState.open && (
        <AddStockModal
          editStock={modalState.editStock}
          existingTickers={stocks.map((s) => s.ticker)}
          onSave={handleSaveStock}
          onClose={() => setModalState({ open: false, editStock: null })}
        />
      )}
    </div>
  );
}
