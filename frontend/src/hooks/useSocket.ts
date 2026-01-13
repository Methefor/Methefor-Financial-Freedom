import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { AppSettings, NewsItem, Portfolio, Signal } from '../types';

interface SocketData {
  signals: Signal[];
  news: NewsItem[];
  portfolio: Partial<Portfolio>;
  settings: Partial<AppSettings>;
  status: 'connecting' | 'connected' | 'disconnected';
}

export const useSocket = () => {
  const [data, setData] = useState<SocketData>({
    signals: [],
    news: [],
    portfolio: {},
    settings: {},
    status: 'connecting'
  });
  const socketRef = useRef<Socket | null>(null);

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

    socket.on('initial_data', (initialData: any) => {
      console.log('✓ Initial data received:', initialData);
      setData(prev => ({ 
        ...prev, 
        signals: initialData.signals || [],
        news: initialData.news || [],
        portfolio: initialData.portfolio || {},
        settings: initialData.settings || {}
      }));
    });

    socket.on('data_update', (update: any) => {
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
