import { ChevronRight, Clock, TrendingDown, TrendingUp, Zap } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { Signal } from '../types';
import { popIn } from '../utils/animations';

interface SignalCardProps {
  signal: Signal;
  onClick: () => void;
}

export const SignalCard = ({ signal, onClick }: SignalCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      popIn(cardRef.current);
    }
  }, []);

  const getDecisionStyles = (decision: string) => {
    if (decision.includes('BUY')) return 'text-green-400 border-green-500/20 bg-green-500/5 shadow-[0_0_15px_rgba(34,197,94,0.1)]';
    if (decision.includes('SELL')) return 'text-red-400 border-red-500/20 bg-red-500/5 shadow-[0_0_15px_rgba(239,68,68,0.1)]';
    return 'text-yellow-400 border-yellow-500/20 bg-yellow-500/5';
  };

  return (
    <div 
      ref={cardRef}
      onClick={onClick}
      className="group relative bg-[#0a0e27]/40 backdrop-blur-xl border border-white/5 rounded-[32px] p-8 cursor-pointer transition-all duration-500 hover:border-gold/30 hover:bg-[#0a0e27]/60 hover:-translate-y-2 overflow-hidden"
    >
      {/* Dynamic Glow Line */}
      <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${
        signal.decision.includes('BUY') ? 'from-green-500/50 to-transparent' : 
        signal.decision.includes('SELL') ? 'from-red-500/50 to-transparent' : 
        'from-yellow-500/50 to-transparent'
      }`} />

      <div className="flex justify-between items-start mb-8">
        <div className="flex flex-col gap-1">
          <h2 className="text-3xl font-black tracking-tight group-hover:text-gold transition-colors">{signal.symbol}</h2>
          <div className="flex items-center gap-2 text-[10px] font-bold text-white/30 uppercase tracking-[0.2em]">
            <Clock size={12} />
            {new Date(signal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
        <div className={`px-4 py-2 rounded-2xl text-[10px] font-black tracking-widest border ${getDecisionStyles(signal.decision)}`}>
          {signal.decision}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
          <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest block mb-1">Duygu Skoru</span>
          <div className="flex items-center gap-2">
            <span className={`text-xl font-black ${signal.sentiment.score > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {(signal.sentiment.score * 100).toFixed(0)}%
            </span>
            {signal.sentiment.score > 0 ? <TrendingUp size={16} className="text-green-500" /> : <TrendingDown size={16} className="text-red-500" />}
          </div>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
          <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest block mb-1">Güven Skoru</span>
          <div className="flex items-center gap-2">
            <span className="text-xl font-black text-gold">
              {signal.confidence.toFixed(0)}%
            </span>
            <Zap size={16} className="text-gold fill-current" />
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 text-white/40 text-xs font-bold uppercase tracking-widest mt-auto group-hover:text-gold transition-all">
        Detaylı Analizi Gör
        <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
      </div>

      {/* Background Decorative Element */}
      <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-gold/5 blur-3xl rounded-full transition-all group-hover:bg-gold/10" />
    </div>
  );
};
