import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

export const useWebSocket = (onMessage) => {
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const connect = useCallback(() => {
    try {
      const websocket = api.connectWebSocket((message) => {
        if (onMessage) {
          onMessage(message);
        }
      });

      websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        setReconnectAttempts(0);
      };

      websocket.onclose = () => {
        console.log('❌ WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt reconnect
        if (reconnectAttempts < 5) {
          setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, 3000);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setWs(websocket);

      return websocket;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [onMessage, reconnectAttempts]);

  useEffect(() => {
    const websocket = connect();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  return { isConnected, ws };
};
