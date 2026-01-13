import axios from 'axios';
import { Activity, LineChart as ChartIcon, DollarSign, TrendingDown, TrendingUp, Wallet, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Portfolio } from '../types';
import { fadeIn } from '../utils/animations';

export const PortfolioSection = ({ portfolio }: { portfolio: Portfolio }) => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    fadeIn('.portfolio-stat');
    fetchHistory();
  }, [portfolio]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('/api/portfolio/history');
      if (res.data.success) {
        setHistory(res.data.history);
      }
    } catch (err) {
      console.error('History fetch error:', err);
    }
  };

  if (!portfolio) return null;

  return (
    <div className="space-y-10">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard 
          label="Toplam Bakiye" 
          value={`$${portfolio.total_equity?.toLocaleString()}`} 
          icon={<Wallet className="text-gold" size={24} />} 
          className="portfolio-stat"
        />
        <StatCard 
          label="Nakit (USD)" 
          value={`$${portfolio.cash?.toLocaleString()}`} 
          icon={<DollarSign className="text-blue-400" size={24} />} 
          className="portfolio-stat"
        />
        <StatCard 
          label="Varlık Değeri" 
          value={`$${((portfolio.total_equity || 0) - (portfolio.cash || 0))?.toLocaleString()}`} 
          icon={<TrendingUp className="text-green-400" size={24} />} 
          className="portfolio-stat"
        />
      </div>

      {/* Performance Chart */}
      <div className="bg-[#0a0e27]/40 backdrop-blur-xl border border-white/5 rounded-[40px] p-10">
        <div className="flex justify-between items-center mb-10">
           <div>
             <h2 className="text-xl font-black tracking-tight uppercase italic flex items-center gap-3">
               <ChartIcon size={20} className="text-gold" /> Performans Analizi
             </h2>
             <span className="text-[10px] font-black tracking-widest text-white/20 uppercase mt-1 block">Özsermaye Gelişim Grafiği (Son 100 Kayıt)</span>
           </div>
           <div className="flex gap-2">
              <span className="px-3 py-1 bg-white/5 border border-white/5 rounded-lg text-[10px] font-bold text-white/40 uppercase">Gerçek Zamanlı</span>
           </div>
        </div>

        <div className="h-[350px] w-full">
          {history.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ffd700" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ffd700" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis 
                  dataKey="time" 
                  hide={true}
                />
                <YAxis 
                  stroke="rgba(255,255,255,0.2)" 
                  fontSize={10} 
                  fontWeight="bold"
                  tickFormatter={(val: any) => `$${(val / 1000).toFixed(1)}k`}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0a0e27', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '16px', fontWeight: 'bold' }}
                  itemStyle={{ color: '#ffd700' }}
                  labelStyle={{ display: 'none' }}
                  formatter={(value: any) => [`$${value?.toLocaleString()}`, 'Özsermaye']}
                />
                <Area 
                  type="monotone" 
                  dataKey="equity" 
                  stroke="#ffd700" 
                  strokeWidth={4}
                  fillOpacity={1} 
                  fill="url(#equityGradient)" 
                  animationDuration={2000}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-white/10 uppercase font-black tracking-[0.3em]">
               <Activity size={48} className="opacity-10 animate-pulse" />
               Veri Toplanıyor...
            </div>
          )}
        </div>
      </div>

      <div className="bg-[#0a0e27]/40 backdrop-blur-xl border border-white/5 rounded-[40px] overflow-hidden">
        <div className="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
          <h2 className="text-xl font-black tracking-tight uppercase italic">Açık Pozisyonlar</h2>
          <div className="text-[10px] font-black tracking-widest text-white/20 uppercase">Gerçek Zamanlı Veri</div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-white/[0.01] text-white/20 text-[10px] uppercase font-black tracking-[0.2em] border-b border-white/5">
              <tr>
                <th className="px-8 py-5">Varlık</th>
                <th className="px-8 py-5">Miktar</th>
                <th className="px-8 py-5">Maliyet / Fiyat</th>
                <th className="px-8 py-5">Performans</th>
                <th className="px-8 py-5 text-right">Toplam Değer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {portfolio.holdings?.map((item, i) => (
                <tr key={i} className="group hover:bg-white/[0.03] transition-all">
                  <td className="px-8 py-6 font-black text-lg group-hover:text-gold transition-colors">{item.symbol}</td>
                  <td className="px-8 py-6 text-sm font-bold text-white/60">{item.quantity?.toFixed(4)}</td>
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-black text-white/20 uppercase">M: ${item.avg_price?.toFixed(2)}</span>
                      <span className="text-sm font-bold">${item.price?.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl font-black text-xs ${item.pnl >= 0 ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                      {item.pnl >= 0 ? <TrendingUp size={14}/> : <TrendingDown size={14}/>}
                      {item.pnl?.toFixed(2)}%
                    </div>
                  </td>
                  <td className="px-8 py-6 text-right font-black text-gold">${item.value?.toLocaleString()}</td>
                  <td className="px-8 py-6 text-right">
                    <button 
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`${item.symbol} pozisyonunu kapatmak istediğinize emin misiniz?`)) {
                           try {
                             await axios.post('/api/trade', {
                               symbol: item.symbol,
                               side: 'SELL',
                               quantity: item.quantity,
                               price: item.price
                             });
                           } catch (err) {
                             alert('İşlem başarısız.');
                           }
                        }
                      }}
                      className="px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl text-[10px] font-black uppercase hover:bg-red-500 hover:text-white transition-all"
                    >
                      Kapat
                    </button>
                  </td>
                </tr>
              ))}
              {(!portfolio.holdings || portfolio.holdings.length === 0) && (
                <tr>
                  <td colSpan={5} className="px-8 py-24 text-center">
                    <div className="flex flex-col items-center gap-4 text-white/10 uppercase font-black tracking-[0.3em]">
                      <Zap size={48} className="opacity-10" />
                      Portföy Boş
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  className?: string;
}

const StatCard = ({ label, value, icon, className }: StatCardProps) => (
  <div className={`p-8 bg-[#0a0e27]/40 backdrop-blur-xl border border-white/5 rounded-[32px] flex items-center gap-8 ${className}`}>
    <div className="w-16 h-16 bg-white/5 rounded-[24px] flex items-center justify-center border border-white/5">
      {icon}
    </div>
    <div>
      <span className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] block mb-1">{label}</span>
      <h3 className="text-3xl font-black tracking-tighter">{value}</h3>
    </div>
  </div>
);
