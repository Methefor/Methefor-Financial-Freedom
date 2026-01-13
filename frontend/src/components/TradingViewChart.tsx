import { useEffect, useRef } from 'react';

interface TradingViewChartProps {
  symbol: string;
}

export const TradingViewChart = ({ symbol }: TradingViewChartProps) => {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Clear previous widget
    if (container.current) {
      container.current.innerHTML = '';
    }

    // Akıllı Sembol Eşleşmesi
    let tradingViewSymbol = symbol;
    if (symbol.includes('USD')) {
      tradingViewSymbol = `BINANCE:${symbol.replace('-', '')}T`;
    } else if (['MSTR', 'AAPL', 'AMD', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN', 'MSFT'].includes(symbol)) {
      tradingViewSymbol = `NASDAQ:${symbol}`;
    } else if (['F', 'HWM', 'OSCR', 'OPEN', 'WMT'].includes(symbol)) {
      tradingViewSymbol = `NYSE:${symbol}`;
    } else if (symbol.includes('.IS')) {
      tradingViewSymbol = `BIST:${symbol.replace('.IS', '')}`;
    }

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      "autosize": true,
      "symbol": tradingViewSymbol,
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "tr",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "calendar": false,
      "support_host": "https://www.tradingview.com"
    });
    
    if (container.current) {
      container.current.appendChild(script);
    }
  }, [symbol]);

  return (
    <div className="tradingview-widget-container h-[500px] w-full bg-black/20" ref={container}>
      <div className="tradingview-widget-container__widget h-full w-full"></div>
    </div>
  );
};
