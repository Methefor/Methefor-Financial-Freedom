import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

export const useSocket = () => {
  const [data, setData] = useState({
    signals: [],
    news: [],
    portfolio: {},
    settings: {},
    status: 'connecting'
  });
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = io('/', {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      withCredentials: true
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Socket connected');
      setData(prev => ({ ...prev, status: 'connected' }));
    });

    socket.on('initial_data', (initialData) => {
      console.log('✓ Initial data received:', initialData);
      setData(prev => ({ 
        ...prev, 
        signals: initialData.signals || [],
        news: initialData.news || [],
        portfolio: initialData.portfolio || {},
        settings: initialData.settings || {}
      }));
    });

    socket.on('data_update', (update) => {
      console.log('⟳ Data update received:', update);
      setData(prev => ({ 
        ...prev, 
        signals: update.signals || prev.signals,
        news: update.news || prev.news,
        portfolio: update.portfolio || prev.portfolio
      }));
    });

    socket.on('disconnect', () => {
      setData(prev => ({ ...prev, status: 'disconnected' }));
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const requestUpdate = () => {
    if (socketRef.current) {
      socketRef.current.emit('request_update');
    }
  };

  return { ...data, requestUpdate };
};
