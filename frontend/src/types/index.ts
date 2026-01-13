export interface Signal {
  symbol: string;
  decision: 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
  combined_score: number;
  confidence: number;
  sentiment: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
    news_count: number;
  };
  technical: {
    rsi?: number;
    trend?: string;
    decision?: string;
    score?: number;
  };
  price: {
    current: number;
    change_1d?: number;
    change_5d?: number;
  };
  reasons: string[];
  ai_explanation?: string;
  timestamp: string;
}

export interface NewsItem {
  id: number;
  source: string;
  title: string;
  summary: string;
  link: string;
  published: string;
  category: string;
  sentiment: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
  };
  matched_symbol?: string;
}

export interface Portfolio {
  total_equity: number;
  cash: number;
  holdings: {
    symbol: string;
    quantity: number;
    price: number;
    value: number;
    avg_price: number;
    pnl: number;
  }[];
}

export interface AppSettings {
  ui: {
    theme: 'dark' | 'light' | 'cyber';
    compact_mode: boolean;
  };
  analysis: {
    rsi_overbought: number;
    rsi_oversold: number;
    min_confidence: number;
  };
  notifications: {
    telegram_enabled: boolean;
    browser_push_enabled: boolean;
  };
}

export interface WatchlistEntry {
  symbol: string;
  category: string;
  type: 'stock' | 'crypto' | 'commodity';
  market: 'US' | 'TR' | 'GLOBAL' | 'CRYPTO';
}
