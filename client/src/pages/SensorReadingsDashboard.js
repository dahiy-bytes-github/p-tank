import { useState, useEffect } from 'react';
import '../styles/SensorReadingDashboard.css';

const SensorReadingsDashboard = () => {
  const [readings, setReadings] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    totalPages: 1,
    totalItems: 0
  });
  const [filters, setFilters] = useState({
    temp: '',
    ph: '',
    tank_level_min: '',
    tank_level_max: '',
    start_date: '',
    end_date: ''
  });
  const [loading, setLoading] = useState(false);
  const [filtersApplied, setFiltersApplied] = useState(false);

  const fetchReadings = async () => {
    setLoading(true);
    try {
      // Create base params object
      const paramsObj = {
        page: pagination.page,
        limit: pagination.limit
      };

      // Add filters only when applied
      if (filtersApplied) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== '') {
            paramsObj[key] = value;
          }
        });
      }

      const params = new URLSearchParams(paramsObj);
      const response = await fetch(`http://localhost:5555/sensorreadings?${params.toString()}`);

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      setReadings(data.readings);
      setPagination(prev => ({
        ...prev,
        totalPages: data.pagination.total_pages,
        totalItems: data.pagination.total_items
      }));
    } catch (error) {
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReadings();
  }, [pagination.page, pagination.limit, filtersApplied]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const applyFilters = () => {
    setPagination(prev => ({ ...prev, page: 1 }));
    setFiltersApplied(true);
  };

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= pagination.totalPages) {
      setPagination(prev => ({ ...prev, page: newPage }));
    }
  };

  const resetFilters = () => {
    setFilters({
      temp: '',
      ph: '',
      tank_level_min: '',
      tank_level_max: '',
      start_date: '',
      end_date: ''
    });
    setFiltersApplied(false);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const exportToCSV = () => {
    const headers = ['Timestamp', 'Temperature (°C)', 'pH Level', 'Tank Level (%)'];
    const csvContent = [
      headers.join(','),
      ...readings.map(r => [
        `"${new Date(r.timestamp).toLocaleString()}"`,
        r.temp,
        r.ph,
        r.tank_level_per
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sensor_readings_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="sensor-readings">
      <h1 className="sr-title">Sensor Readings Dashboard</h1>

      {/* Filters Section */}
      <div className="sr-filters">
        <h2 className="sr-subtitle">Filters</h2>
        <div className="sr-filter-grid">
          <div className="sr-filter-group">
            <label className="sr-label">Temperature (°C)</label>
            <input
              type="number"
              name="temp"
              value={filters.temp}
              onChange={handleFilterChange}
              className="sr-input"
              step="0.1"
            />
          </div>

          <div className="sr-filter-group">
            <label className="sr-label">pH Level</label>
            <input
              type="number"
              name="ph"
              value={filters.ph}
              onChange={handleFilterChange}
              className="sr-input"
              step="0.1"
            />
          </div>

          <div className="sr-filter-group">
            <label className="sr-label">Tank Level Min (%)</label>
            <input
              type="number"
              name="tank_level_min"
              value={filters.tank_level_min}
              onChange={handleFilterChange}
              className="sr-input"
              min="0"
              max="100"
            />
          </div>

          <div className="sr-filter-group">
            <label className="sr-label">Tank Level Max (%)</label>
            <input
              type="number"
              name="tank_level_max"
              value={filters.tank_level_max}
              onChange={handleFilterChange}
              className="sr-input"
              min="0"
              max="100"
            />
          </div>

          <div className="sr-filter-group">
            <label className="sr-label">Start Date</label>
            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
              className="sr-input"
            />
          </div>

          <div className="sr-filter-group">
            <label className="sr-label">End Date</label>
            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
              className="sr-input"
            />
          </div>

          <div className="sr-filter-actions">
            <button onClick={applyFilters} className="sr-apply-btn">
              Apply Filters
            </button>
            <button onClick={resetFilters} className="sr-reset-btn">
              Reset Filters
            </button>
            <button onClick={exportToCSV} className="sr-export-btn">
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {loading && (
        <div className="sr-loading">
          <div className="sr-spinner"></div>
        </div>
      )}

      {!loading && (
        <div className="sr-table-container">
          <table className="sr-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Temperature (°C)</th>
                <th>pH Level</th>
                <th>Tank Level (%)</th>
              </tr>
            </thead>
            <tbody>
              {readings.length > 0 ? (
                readings.map((reading) => (
                  <tr key={reading.id} className="sr-table-row">
                    <td className="sr-table-cell">{new Date(reading.timestamp).toLocaleString()}</td>
                    <td className="sr-table-cell">{reading.temp}</td>
                    <td className="sr-table-cell">{reading.ph}</td>
                    <td className="sr-table-cell">{reading.tank_level_per}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="sr-no-data">
                    No readings found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {!loading && pagination.totalPages > 1 && (
        <div className="sr-pagination">
          <button
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
            className="sr-pagination-btn"
          >
            Previous
          </button>

          <span className="sr-page-info">
            Page {pagination.page} of {pagination.totalPages}
          </span>

          <button
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.totalPages}
            className="sr-pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default SensorReadingsDashboard;
