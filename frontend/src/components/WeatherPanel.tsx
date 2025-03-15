import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  description: string;
  sunrise: string;
  sunset: string;
  moonPhase: string;
}

const WeatherPanel: React.FC = () => {
  const [weather, setWeather] = useState<WeatherData>({
    temperature: 0,
    humidity: 0,
    windSpeed: 0,
    description: 'Loading...',
    sunrise: '--:--',
    sunset: '--:--',
    moonPhase: 'Unknown'
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.get<WeatherData>('http://localhost:8000/api/weather');
        setWeather(response.data);
      } catch (error) {
        setError('Failed to fetch weather data');
        console.error('Failed to fetch weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
    const interval = setInterval(fetchWeather, 300000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="data-panel weather-panel error">
        <h2>Weather Conditions</h2>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="data-panel weather-panel">
      <h2>Weather Conditions</h2>
      
      <div className="weather-grid">
        <div className="weather-item">
          <div className="weather-label">Temperature</div>
          <div className="weather-value">{loading ? '--' : `${weather.temperature}°C`}</div>
        </div>

        <div className="weather-item">
          <div className="weather-label">Humidity</div>
          <div className="weather-value">{loading ? '--' : `${weather.humidity}%`}</div>
        </div>

        <div className="weather-item">
          <div className="weather-label">Wind Speed</div>
          <div className="weather-value">{loading ? '--' : `${weather.windSpeed} km/h`}</div>
        </div>

        <div className="weather-item">
          <div className="weather-label">Conditions</div>
          <div className="weather-value">{weather.description}</div>
        </div>

        <div className="weather-item sun-times">
          <div className="weather-label">Sun Times</div>
          <div className="weather-value">
            ↑ {weather.sunrise}
            <br />
            ↓ {weather.sunset}
          </div>
        </div>

        <div className="weather-item">
          <div className="weather-label">Moon Phase</div>
          <div className="weather-value">{weather.moonPhase}</div>
        </div>
      </div>

      <style>
        {`
          .weather-panel {
            padding: 20px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(0, 162, 255, 0.3);
            border-radius: 8px;
          }

          .error-message {
            color: #ff4444;
            text-align: center;
            padding: 20px;
            background: rgba(255, 68, 68, 0.1);
            border-radius: 5px;
          }

          h2 {
            margin: 0 0 20px;
            font-size: 1.5rem;
            color: #00a2ff;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .weather-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
          }

          .weather-item {
            background: rgba(0, 162, 255, 0.1);
            border: 1px solid rgba(0, 162, 255, 0.2);
            border-radius: 5px;
            padding: 15px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
          }

          .weather-item:hover {
            background: rgba(0, 162, 255, 0.15);
            border-color: rgba(0, 162, 255, 0.3);
          }

          .weather-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 5px;
            color: #00a2ff;
          }

          .weather-value {
            font-size: 1.2rem;
            font-weight: 500;
            color: #fff;
          }
        `}
      </style>
    </div>
  );
};

export default WeatherPanel;