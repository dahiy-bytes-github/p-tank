import React, { useState } from 'react';
import '../styles/PredictionCard.css';

const PredictionCard = () => {
  const [reading, setReading] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch("http://localhost:5555/predict", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sensor_cm: parseFloat(reading) })
      });
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
      
      const data = await response.json();
      setPrediction(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-card">
      <h2>Septic Tank Level Prediction</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="reading">Current Sensor Reading (cm):</label>
          <input
            id="reading"
            type="number"
            step="0.1"
            min="22"
            max="27"
            value={reading}
            onChange={(e) => setReading(e.target.value)}
            required
          />
          <small>Must be between 22.0 and 27.0 cm</small>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Predicting...' : 'Predict'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {prediction && (
        <div className="prediction-results">
          <div className={`current-level ${prediction.current_level > 80 ? 'critical' : ''}`}>
            Current Level: {prediction.current_level}%
          </div>
          
          <div className="forecast">
            <h3>6-Hour Forecast:</h3>
            <div className="forecast-bars">
              {prediction.prediction.forecast.map((level, i) => (
                <div key={i} className="forecast-bar-container">
                  <div 
                    className={`forecast-bar ${level > 80 ? 'critical' : ''}`}
                    style={{ height: `${level}%` }}
                  ></div>
                  <div className="forecast-hour">+{i+1}h</div>
                  <div className="forecast-value">{level}%</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="summary">
            <p>Next 3h Average: {prediction.prediction.next_3h}%</p>
            <p>Peak Level: {prediction.prediction.max_level}%</p>
            {prediction.prediction.critical && (
              <p className="critical-warning">⚠️ Critical level predicted!</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionCard;