import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import './styles/App.scss';
import WebSocketService from './services/websocket';

// Components
import ArcReactor from './components/ArcReactor';
import SystemMetrics from './components/SystemMetrics';
import WeatherPanel from './components/WeatherPanel';
import StatusRings from './components/StatusRings';

const App: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    WebSocketService.onMessage((message) => {
      setMessages((prev) => [...prev, JSON.stringify(message)]);
    });

    const socket = WebSocketService.getSocket();
    if (socket) {
      socket.on('connect', () => setConnected(true));
      socket.on('disconnect', () => setConnected(false));
    }

    return () => {
      WebSocketService.disconnect();
    };
  }, []);

  return (
    <div className="jarvis-interface">
      <div className="header">
        <h1>JARVIS OS</h1>
        <div className="version">v1.2.5</div>
      </div>
      
      <div className="main-display">
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <ArcReactor />
          <StatusRings />
          <OrbitControls enableZoom={false} />
        </Canvas>
      </div>

      <div className="metrics-container">
        <SystemMetrics />
        <WeatherPanel />
      </div>

      <div className="footer">
        <div className="status">STARK INDUSTRIES</div>
        <div className="time">System Time: {new Date().toLocaleTimeString()}</div>
      </div>
    </div>
  );
};

export default App;