import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

interface SystemData {
  cpu: number;
  memory: number;
  temperature: number;
  network: {
    up: number;
    down: number;
  };
}

const SystemMetrics: React.FC = () => {
  const [systemData, setSystemData] = useState<SystemData>({
    cpu: 0,
    memory: 0,
    temperature: 0,
    network: { up: 0, down: 0 }
  });

  useEffect(() => {
    const socket = io('http://localhost:8000');

    socket.on('system_metrics', (data: SystemData) => {
      setSystemData(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="data-panel system-metrics">
      <h2>System Metrics</h2>
      
      <div className="metric-grid">
        <div className="metric-item">
          <div className="metric-label">CPU Usage</div>
          <div className="metric-value">
            <div className="progress-bar" style={{ width: `${systemData.cpu}%` }} />
            {systemData.cpu.toFixed(1)}%
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-label">Memory</div>
          <div className="metric-value">
            <div className="progress-bar" style={{ width: `${systemData.memory}%` }} />
            {systemData.memory.toFixed(1)}%
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-label">Temperature</div>
          <div className="metric-value">{systemData.temperature}°C</div>
        </div>

        <div className="metric-item">
          <div className="metric-label">Network</div>
          <div className="metric-value">
            ↑ {(systemData.network.up / 1024 / 1024).toFixed(2)} MB/s
            <br />
            ↓ {(systemData.network.down / 1024 / 1024).toFixed(2)} MB/s
          </div>
        </div>
      </div>

      <style>
        {`
          .system-metrics {
            padding: 20px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(0, 162, 255, 0.3);
            border-radius: 8px;
          }

          .system-metrics h2 {
            margin: 0 0 20px;
            font-size: 1.5rem;
            color: #00a2ff;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          .system-metrics .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
          }

          .system-metrics .metric-item {
            background: rgba(0, 162, 255, 0.1);
            border: 1px solid rgba(0, 162, 255, 0.2);
            border-radius: 5px;
            padding: 15px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
          }

          .system-metrics .metric-item:hover {
            background: rgba(0, 162, 255, 0.15);
            border-color: rgba(0, 162, 255, 0.3);
          }

          .system-metrics .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 5px;
            color: #00a2ff;
          }

          .system-metrics .metric-value {
            font-size: 1.2rem;
            font-weight: 500;
            color: #fff;
          }

          .system-metrics .progress-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: #00a2ff;
            transition: width 0.3s ease;
          }
        `}
      </style>
    </div>
  );
};

export default SystemMetrics;