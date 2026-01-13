import axios from 'axios';
import { Bitcoin, Briefcase, Globe, Plus, Search, Trash2, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { WatchlistEntry } from '../types';
import { popIn } from '../utils/animations';

export const WatchlistSection = () => {
  const [watchlist, setWatchlist] = useState<WatchlistEntry[]>([]);
  const [newSymbol, setNewSymbol] = useState('');
  const [category, setCategory] = useState('custom');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    fetchWatchlist();
    popIn('.watchlist-card');
  }, []);

  const fetchWatchlist = async () => {
    try {
      const res = await axios.get('/api/watchlist');
      if (res.data.success) {
        setWatchlist(res.data.watchlist);
      }
    } catch (err) {
      console.error('Watchlist fetch error:', err);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;
    setLoading(true);
    try {
      const res = await axios.post('/api/watchlist/add', {
        symbol: newSymbol.toUpperCase().trim(),
        category
      });
      if (res.data.success) {
        setMessage({ type: 'success', text: `${newSymbol.toUpperCase()} eklendi.` });
        setNewSymbol('');
        fetchWatchlist();
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Eklenemedi.' });
    }
    setLoading(false);
    setTimeout(() => setMessage(null), 3000);
  };

  const handleRemove = async (symbol: string) => {
    try {
      const res = await axios.post('/api/watchlist/remove', { symbol });
      if (res.data.success) {
        fetchWatchlist();
      }
    } catch (err) {
       console.error('Remove error:', err);
    }
  };

  const getIcon = (type: string) => {
    switch(type) {
      case 'crypto': return <Bitcoin className="text-orange-400" size={18} />;
      case 'stock': return <Briefcase className="text-blue-400" size={18} />;
      default: return <TrendingUp className="text-gold" size={18} />;
    }
  };

  return (
    <div className="max-w-6xl space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-4">
        <div>
          <h2 className="text-3xl font-black tracking-tight flex items-center gap-4">
            <Globe className="text-gold" size={32} /> Radar & Takip Listesi
          </h2>
          <p className="text-white/40 font-medium mt-1">Algoritmanın analiz etmesini istediğin tüm sembolleri buradan yönet.</p>
        </div>
      </div>

      {/* Add New Symbol Form */}
      <form onSubmit={handleAdd} className="bg-white/5 border border-white/10 rounded-[32px] p-8 flex flex-col md:flex-row gap-6 items-end">
        <div className="flex-1 space-y-3">
          <label className="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">Yeni Sembol (Örn: AAPL, BTC-USD, THYAO.IS)</label>
          <div className="relative">
             <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-white/20" size={18} />
             <input 
              type="text" 
              placeholder="Sembol girin..." 
              value={newSymbol}
              onChange={e => setNewSymbol(e.target.value)}
              className="w-full bg-[#0a0e27] border border-white/10 rounded-2xl py-4 pl-14 pr-6 focus:border-gold/50 focus:outline-none font-bold text-lg"
             />
          </div>
        </div>
        <div className="w-full md:w-64 space-y-3">
          <label className="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">Kategori</label>
          <select 
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="w-full bg-[#0a0e27] border border-white/10 rounded-2xl py-4 px-5 focus:border-gold/50 focus:outline-none font-bold appearance-none cursor-pointer"
          >
            <option value="custom">Özel Liste</option>
            <option value="stocks">ABD Borsası</option>
            <option value="turkish">Borsa İstanbul</option>
            <option value="crypto">Kripto Para</option>
          </select>
        </div>
        <button 
          disabled={loading}
          type="submit"
          className="h-[60px] px-10 bg-gold text-dark-bg font-black rounded-2xl shadow-xl hover:scale-105 active:scale-95 transition-all flex items-center gap-3 disabled:opacity-50"
        >
          <Plus size={20} />
          EKLE
        </button>
      </form>

      {message && (
        <div className={`p-4 rounded-2xl text-sm font-bold flex items-center gap-3 animate-in slide-in-from-top-4 duration-300 ${message.type === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
          <Zap size={18} /> {message.text}
        </div>
      )}

      {/* Watchlist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {watchlist.map((entry, idx) => (
          <div 
            key={idx} 
            className="watchlist-card group p-6 bg-[#0a0e27]/40 backdrop-blur-xl border border-white/10 rounded-[28px] flex items-center justify-between hover:bg-[#0a0e27]/60 hover:border-gold/30 transition-all hover:-translate-y-1"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/5">
                {getIcon(entry.type)}
              </div>
              <div>
                <h4 className="font-black text-xl tracking-tight leading-none group-hover:text-white transition-colors uppercase">{entry.symbol}</h4>
                <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest mt-1 block">{entry.category}</span>
              </div>
            </div>
            <button 
              onClick={() => handleRemove(entry.symbol)}
              className="p-3 text-white/20 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all opacity-0 group-hover:opacity-100"
            >
              <Trash2 size={18} />
            </button>
          </div>
        ))}
        {watchlist.length === 0 && (
           <div className="col-span-full py-20 text-center opacity-20 flex flex-col items-center gap-4">
              <Globe size={64} />
              <span className="font-black uppercase tracking-[0.4em]">Radar Boş</span>
           </div>
        )}
      </div>
    </div>
  );
};
