import axios from 'axios';
import { Activity, AlertCircle, Bot, Info, ShoppingCart, TrendingDown, TrendingUp, X, Zap } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Signal } from '../types';
import { fadeIn, popIn } from '../utils/animations';
import { TradingViewChart } from './TradingViewChart';

interface SignalModalProps {
  signal: Signal;
  onClose: () => void;
}

export const SignalModal = ({ signal, onClose }: SignalModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  useEffect(() => {
    if (modalRef.current) popIn(modalRef.current);
    if (backdropRef.current) fadeIn(backdropRef.current);
  }, []);

  const handleTrade = async (side: 'BUY' | 'SELL') => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await axios.post('/api/trade', {
        symbol: signal.symbol,
        side,
        quantity,
        price: signal.price.current
      });
      setStatus({ type: 'success', msg: res.data.message });
      setTimeout(() => setStatus(null), 5000);
    } catch (error: any) {
      setStatus({ type: 'error', msg: error.response?.data?.error || 'İşlem başarısız.' });
    }
    setLoading(false);
  };

  return (
    <div 
      ref={backdropRef}
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-black/90 backdrop-blur-2xl"
    >
      <div 
        ref={modalRef}
        className="bg-[#0a0e27] border border-white/10 w-full max-w-6xl h-full max-h-[90vh] rounded-[48px] overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.8)] flex flex-col relative"
      >
        {/* Header */}
        <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
          <div className="flex items-center gap-6">
            <div className={`w-16 h-16 rounded-3xl flex items-center justify-center text-2xl font-black border ${
              signal.decision.includes('BUY') ? 'bg-green-500/10 text-green-400 border-green-500/20' : 
              signal.decision.includes('SELL') ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
              'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
            }`}>
              {signal.symbol[0]}
            </div>
            <div>
              <h2 className="text-3xl font-black tracking-tighter">{signal.symbol} Analizi</h2>
              <div className="flex items-center gap-2 text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">
                <Activity size={12} />
                Gerçek Zamanlı Piyasa Verisi & AI Sentezi
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-white/40 hover:bg-red-500/20 hover:text-red-400 transition-all"
          >
            <X size={24} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-10 space-y-12">
          {/* TradingView Chart Section */}
          <div className="rounded-[32px] overflow-hidden border border-white/10 shadow-2xl">
            <TradingViewChart symbol={signal.symbol} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            {/* Left Column: Analysis */}
            <div className="lg:col-span-7 space-y-10">
              {/* Decision Card */}
              <div className={`p-8 rounded-[32px] border relative overflow-hidden group ${
                signal.decision.includes('BUY') ? 'bg-green-500/5 border-green-500/20' : 
                signal.decision.includes('SELL') ? 'bg-red-500/5 border-red-500/20' : 
                'bg-yellow-500/5 border-yellow-500/20'
              }`}>
                <div className="relative z-10 flex justify-between items-center">
                  <div>
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-40 mb-2 block">Sistem Kararı</span>
                    <h3 className={`text-5xl font-black italic tracking-tighter ${
                      signal.decision.includes('BUY') ? 'text-green-400' : 
                      signal.decision.includes('SELL') ? 'text-red-400' : 
                      'text-yellow-400'
                    }`}>
                      {signal.decision}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-40 mb-2 block">Güven Endeksi</span>
                    <div className="text-4xl font-black text-gold flex items-center gap-2 justify-end">
                      {signal.confidence.toFixed(1)}%
                      <Zap size={28} className="fill-current" />
                    </div>
                  </div>
                </div>
                {/* Background Glow */}
                <div className={`absolute -right-20 -bottom-20 w-64 h-64 blur-[100px] opacity-20 ${
                  signal.decision.includes('BUY') ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>

               {/* Trade Control Panel (NEW) */}
               <div className="p-8 bg-white/5 border border-white/10 rounded-[32px] space-y-8">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-black text-gold tracking-[0.3em] uppercase flex items-center gap-3">
                    <ShoppingCart size={20} /> KAĞIT ÜZERİNDE İŞLEM
                  </h3>
                  <div className="text-right">
                    <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] block">Anlık Fiyat</span>
                    <span className="text-2xl font-black text-white">${signal.price?.current?.toLocaleString()}</span>
                  </div>
                </div>

                <div className="flex flex-col md:flex-row gap-6 items-end">
                  <div className="flex-1 space-y-4">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">İşlem Miktarı (Adet)</label>
                    <input 
                      type="number"
                      value={quantity}
                      onChange={(e) => setQuantity(Math.max(0.0001, parseFloat(e.target.value) || 0))}
                      className="w-full bg-[#0a0e27] border border-white/10 rounded-2xl py-5 px-6 focus:outline-none focus:border-gold/50 text-xl font-bold"
                    />
                  </div>
                  <div className="flex gap-4 w-full md:w-auto">
                    <button 
                      onClick={() => handleTrade('BUY')}
                      disabled={loading}
                      className="flex-1 md:w-40 h-20 bg-green-500 text-dark-bg font-black rounded-2xl shadow-[0_10px_30px_rgba(34,197,94,0.3)] hover:scale-105 active:scale-95 transition-all flex flex-col items-center justify-center disabled:opacity-50"
                    >
                      <TrendingUp size={24} />
                      <span className="text-xs mt-1">SATIN AL</span>
                    </button>
                    <button 
                      onClick={() => handleTrade('SELL')}
                      disabled={loading}
                      className="flex-1 md:w-40 h-20 bg-red-500 text-dark-bg font-black rounded-2xl shadow-[0_10px_30px_rgba(239,68,68,0.3)] hover:scale-105 active:scale-95 transition-all flex flex-col items-center justify-center disabled:opacity-50"
                    >
                      <TrendingDown size={24} />
                      <span className="text-xs mt-1">AÇIĞA SAT</span>
                    </button>
                  </div>
                </div>

                {status && (
                  <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2 ${
                    status.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {status.type === 'success' ? <Zap size={20} /> : <AlertCircle size={20} />}
                    <span className="text-sm font-bold">{status.msg}</span>
                  </div>
                )}
              </div>
              
              {/* AI Explanation */}
              <div className="space-y-4">
                <h3 className="text-sm font-black flex items-center gap-3 text-gold tracking-[0.3em] uppercase">
                  <Bot size={20} className="text-gold" /> ASİSTAN ANALİZİ
                </h3>
                <div className="p-8 bg-gold/5 border border-gold/10 rounded-[32px] text-lg text-white/80 leading-relaxed font-medium shadow-[inset_0_0_40px_rgba(255,215,0,0.03)]">
                   {signal.ai_explanation || 'Bu sembol için kapsamlı AI raporu oluşturuluyor...'}
                </div>
              </div>
            </div>

            {/* Right Column: Evidence & Metrics */}
            <div className="lg:col-span-5 space-y-10">
               <div className="p-8 bg-white/5 rounded-[32px] border border-white/5">
                <h3 className="text-sm font-black mb-6 tracking-[0.3em] uppercase flex items-center gap-3 opacity-60">
                   <Info size={18} /> Teknik Kanıtlar
                </h3>
                <ul className="space-y-4">
                  {signal.reasons?.map((reason, i) => (
                    <li key={i} className="text-sm text-white/70 bg-white/[0.03] p-5 rounded-[20px] border border-white/5 flex gap-5 items-center group hover:bg-white/[0.07] transition-all">
                      <div className="w-2 h-2 bg-gold rounded-full shadow-[0_0_10px_#ffd700]" />
                      <span className="font-semibold">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-6">
                 <div className="p-6 bg-white/5 rounded-[28px] border border-white/5">
                    <span className="text-[10px] font-black text-white/30 uppercase tracking-widest block mb-2">Duygu</span>
                    <div className={`text-2xl font-black ${signal.sentiment.score > 0 ? 'text-green-400' : 'text-red-400'}`}>
                       {(signal.sentiment.score * 100).toFixed(0)}%
                    </div>
                 </div>
                 <div className="p-6 bg-white/5 rounded-[28px] border border-white/5">
                    <span className="text-[10px] font-black text-white/30 uppercase tracking-widest block mb-2">Teknik Skor</span>
                    <div className="text-2xl font-black text-blue-400">
                       {signal.technical.score || 0}
                    </div>
                 </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-white/[0.01] border-t border-white/5 text-center text-white/20 text-[10px] font-bold uppercase tracking-[0.4em]">
           Methefor Intelligence Framework v6.0 © 2026
        </div>
      </div>
    </div>
  );
};
